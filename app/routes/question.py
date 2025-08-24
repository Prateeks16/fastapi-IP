from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from schemas.question import QuestionCreate, QuestionOut, QuestionUpdate
from database.models import InterviewQuestions, Interview
from core.roles import role_required
from services.question_generator import generate_resume_based_questions
from core.dependencies import get_interview_or_404

router = APIRouter(prefix="/interviews", tags=["Questions"])

@router.post("/{interview_id}/generate_questions", response_model=list[QuestionOut])
def generate_questions_from_resume(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(["recruiter"])),
    interview: Interview = Depends(get_interview_or_404)
):
    if interview.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to generate questions for this interview")

    if not interview.resume_text:
        raise HTTPException(status_code=400, detail="Resume not uploaded yet")

    generated_questions = generate_resume_based_questions(interview.resume_text)

    saved_questions = []
    for q in generated_questions:
        new_q = InterviewQuestions(
            question_text=q["question_text"],
            category=q.get("category", "resume_based"),
            difficulty=q.get("difficulty", "medium"),
            interview_id=interview_id,
            created_by=current_user.id,
            source="resume",
        )
        db.add(new_q)
        db.flush()
        saved_questions.append(new_q)

    db.commit()
    return saved_questions

@router.post("/{interview_id}/questions", response_model=QuestionOut)
def add_question(
    interview_id: int,
    payload: QuestionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(["recruiter"])),
    interview: Interview = Depends(get_interview_or_404)
):
    if interview.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to add questions to this interview")

    new_question = InterviewQuestions(
        question_text=payload.question_text,
        category=payload.category,
        difficulty=payload.difficulty,
        interview_id=interview_id,
        created_by=current_user.id,
        source=payload.source or "manual",  # if your schema supports it; else default manual
    )
    db.add(new_question)
    db.commit()
    db.refresh(new_question)
    return new_question

@router.get("/{interview_id}/questions", response_model=list[QuestionOut])
def get_questions(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(["recruiter", "candidate"])),
    interview: Interview = Depends(get_interview_or_404)
):
    return db.query(InterviewQuestions).filter(InterviewQuestions.interview_id == interview_id).all()

@router.patch("/{interview_id}/questions/{question_id}", response_model=QuestionOut)
def update_question(
    interview_id: int,
    question_id: int,
    payload: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(["recruiter"])),
    interview: Interview = Depends(get_interview_or_404)
):
    question = db.query(InterviewQuestions).filter(
        InterviewQuestions.id == question_id,
        InterviewQuestions.interview_id == interview_id
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if interview.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to update questions for this interview")

    if payload.question_text is not None:
        question.question_text = payload.question_text
    if payload.category is not None:
        question.category = payload.category
    if payload.difficulty is not None:
        question.difficulty = payload.difficulty

    db.commit()
    db.refresh(question)
    return question

@router.delete("/{interview_id}/questions/{question_id}")
def delete_question(
    interview_id: int,
    question_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(["recruiter"])),
    interview: Interview = Depends(get_interview_or_404)
):
    question = db.query(InterviewQuestions).filter(
        InterviewQuestions.id == question_id,
        InterviewQuestions.interview_id == interview_id
    ).first()

    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    if interview.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to delete questions for this interview")

    db.delete(question)
    db.commit()
    return {"message": "Question deleted successfully"}
