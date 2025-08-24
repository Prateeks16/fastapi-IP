from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import InterviewSession, Answers, PerformanceReview, UserRole
from core.roles import role_required
from core.ml_client import MLClient
import os

router = APIRouter(prefix="/evaluation", tags=["Evaluation"])

@router.post("/trigger/{session_id}")
async def trigger_evaluation(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(["recruiter"])),
):
    sess = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    # collect answers
    answers = db.query(Answers).filter(Answers.session_id == session_id).all()
    payload = [
        {"question_id": a.question_id, "answer_text": a.answer_text, "video_path": a.video_path}
        for a in answers
    ]

    ml_url = os.getenv("ML_SERVICE_URL")
    webhook_url = os.getenv("ML_WEBHOOK_URL")  # e.g. https://your-api.com/evaluation/webhook
    if not ml_url or not webhook_url:
        raise HTTPException(status_code=500, detail="ML_SERVICE_URL/ML_WEBHOOK_URL missing")

    client = MLClient(ml_url)
    try:
        resp = await client.evaluate_session(session_id, payload, webhook_url=webhook_url)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"ML service error: {e}")

    return {"status": "queued", "ml_response": resp}

# Webhook for ML -> save results
@router.post("/webhook")
async def evaluation_webhook(
    request: Request,
    db: Session = Depends(get_db),
):
    body = await request.json()
    # Expected:
    # { "session_id": 123, "overall_score": 78, "strengths": ["..."], "weaknesses": ["..."] }

    session_id = body.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id missing")

    sess = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    pr = PerformanceReview(
        session_id=session_id,
        overall_score=body.get("overall_score"),
        strengths=", ".join(body.get("strengths", [])),
        weakness=", ".join(body.get("weaknesses", [])),
    )
    db.add(pr)
    db.commit()
    return {"status": "saved"}
