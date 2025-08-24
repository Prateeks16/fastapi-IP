from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from services.resume_service import extract_text_from_file
from core.security import get_current_user
from database.connection import get_db
from database.models import Interview, InterviewQuestions, UserRole, Resumes
from schemas.interview import InterviewCreate, InterviewOut
from core.roles import role_required
from services.question_generator import generate_resume_based_questions
import secrets
from services import storage

router = APIRouter(prefix="/interviews", tags=["Interviews"])

@router.post("/", response_model=InterviewOut)
def create_interview(
    interview: InterviewCreate,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(["recruiter"]))
):
    token = secrets.token_urlsafe(8)
    new_interview = Interview(
        title=interview.title,
        description=interview.description,
        job_description=interview.job_description,
        created_by=current_user.id,
        link_token=token,
    )
    db.add(new_interview)
    db.commit()
    db.refresh(new_interview)
    return new_interview

@router.get("/{interview_id}", response_model=InterviewOut)
def get_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(["recruiter", "candidate"]))
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    if current_user.userrole == UserRole.recruiter and interview.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this interview")
    return interview

@router.get("/token/{link_token}", response_model=InterviewOut)
def get_interview_by_token(
    link_token: str,
    db: Session = Depends(get_db),
    current_user=Depends(role_required(["recruiter", "candidate"]))
):
    interview = db.query(Interview).filter(Interview.link_token == link_token).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Invalid token")
    if current_user.userrole == UserRole.recruiter and interview.created_by != current_user.id:
        raise HTTPException(status_code=403, detail="Not allowed to access this interview")
    return interview

@router.delete("/{interview_id}")
def delete_interview(
    interview_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    if interview.created_by != current_user.id or current_user.userrole != UserRole.recruiter:
        raise HTTPException(status_code=403, detail="Not authorized to delete this interview")
    db.delete(interview)
    db.commit()
    return {"message": f"Interview {interview_id} deleted successfully"}

@router.post("/{link_token}/upload-resume")
def upload_resume(
    link_token: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user=Depends(role_required(["candidate", "recruiter"]))
):
    # fetch interview via link
    interview = db.query(Interview).filter(Interview.link_token == link_token).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Invalid interview link")

    # parse text
    resume_text = extract_text_from_file(file)

    # save file to /uploads/resumes
    saved_path = storage.save_upload_file(file, subdir="uploads/resumes")

    # persist resume row
    resume_row = Resumes(
        user_id=current_user.id,
        interview_id=interview.id,
        resume_text=resume_text,
        file_path=saved_path
    )
    db.add(resume_row)

    # mirror into interview.resume_text for quick access
    interview.resume_text = resume_text
    db.commit()
    db.refresh(interview)

    # generate questions via stub/ML
    questions = generate_resume_based_questions(resume_text)

    created = []
    for q in questions:
        new_q = InterviewQuestions(
            question_text=q.get("question_text"),
            category=q.get("category", "resume"),
            difficulty=q.get("difficulty", "medium"),
            source=q.get("source", "resume"),
            interview_id=interview.id,
            created_by=interview.created_by  # recruiter who owns interview
        )
        db.add(new_q)
        created.append(new_q)
    db.commit()

    return {
        "message": "Resume uploaded, parsed and questions generated.",
        "interview_id": interview.id,
        "resume_id": resume_row.id,
        "file_path": saved_path,
        "generated_questions": len(created)
    }
