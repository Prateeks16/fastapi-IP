from services.celery_app import celery
from sqlalchemy.orm import Session
from database.connection import SessionLocal
from database.models import Interview, InterviewQuestions
from services.celery_app import celery
from fastapi import APIRouter
from services.question_generator import generate_resume_based_questions


router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("/{task_id}")
def task_status(task_id: str):
    res = celery.AsyncResult(task_id)
    return {
        "id": task_id,
        "state": res.state,
        "result": res.result if res.ready() else None,
    }

@celery.task(name="services.tasks.generate_questions_for_interview")
def generate_questions_for_interview(interview_id: int):
    db: Session = SessionLocal()
    try:
        itv = db.query(Interview).filter(Interview.id == interview_id).first()
        if not itv or not itv.resume_text:
            return {"ok": False, "reason": "resume missing or interview not found"}

        qs = generate_resume_based_questions(itv.resume_text)
        for q in qs:
            db.add(InterviewQuestions(
                interview_id=itv.id,
                question_text=q.get("question_text"),
                category=q.get("category", "resume"),
                difficulty=q.get("difficulty", "medium"),
                source="resume",
                created_by=itv.created_by,
            ))
        db.commit()
        return {"ok": True, "count": len(qs)}
    finally:
        db.close()




