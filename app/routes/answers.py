from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Answers, InterviewSession, InterviewQuestions
from core.roles import role_required
from datetime import datetime
from services import storage

router = APIRouter(prefix="/answers", tags=["Answers"])

@router.post("/")
def submit_answer(
    session_id: int = Form(...),
    question_id: int = Form(...),
    answer_text: str | None = Form(None),
    video: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    current_user=Depends(role_required(["candidate"])),
):
    sess = db.query(InterviewSession).filter(InterviewSession.id == session_id).first()
    if not sess:
        raise HTTPException(status_code=404, detail="Session not found")
    if sess.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your session")

    q = db.query(InterviewQuestions).filter(InterviewQuestions.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    video_path = storage.save_upload_file(video) if video else None

    ans = Answers(
        question_id=question_id,
        session_id=session_id,
        answer_text=answer_text,
        video_path=video_path,
        created_at=datetime.utcnow()
    )
    db.add(ans)
    db.commit()
    db.refresh(ans)

    return {"id": ans.id, "message": "Answer saved"}
