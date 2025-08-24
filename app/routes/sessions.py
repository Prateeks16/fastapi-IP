# routes/sessions.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Interview, InterviewSession, InterviewQuestions, Users
from core.roles import role_required
from datetime import datetime

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.post("/start/{interview_id}")
def start_session(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(["candidate"])),
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Create session
    sess = InterviewSession(
        user_id=current_user.id,
        # interview_id=interview.id,
        start_time=datetime.utcnow(),
    )
    db.add(sess)
    db.commit()
    db.refresh(sess)

    # Return questions for this interview
    questions = db.query(InterviewQuestions).filter(
        InterviewQuestions.interview_id == interview.id
    ).all()

    return {
        "session_id": sess.id,
        "questions": [
            {
                "id": q.id,
                "question_text": q.question_text,
                "source": getattr(q, "source", "general")
            } for q in questions
        ]
    }

@router.post("/finish/{session_id}")
def finish_session(
    session_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(["candidate", "recruiter"])),
):
    sess = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")

    # Only the candidate who owns the session or a recruiter can finish
    if current_user.userrole == "candidate" and sess.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed")

    sess.end_time = datetime.utcnow()
    db.commit()
    db.refresh(sess)
    return {"message": "Session finished", "session_id": sess.id}
