from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from schemas.job import JobApplicationCreate,JobApplicationResponse
from database.connection import get_db
from database.models import JobApplication, JobDetails
from sqlalchemy.orm import Session
from core.roles import role_required
from schemas.job import JobApplicationCreate
from datetime import datetime


router = APIRouter(tags=["Candidate Panel"])

@router.post("/apply-job/")
def apply_job(request : JobApplicationCreate ,db : Session=Depends(get_db), current_user=Depends(role_required(["candidate"]))):
    job = db.query(JobDetails).filter(JobDetails.id == request.job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job not found")
    existing_application  = db.query(JobApplication).filter(JobApplication.job_id==request.job_id, JobApplication.user_id==current_user.id).first()
    if existing_application:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already applied")
    application = JobApplication(job_id = request.job_id,
                                 user_id = current_user.id,
                                 cover_letter = request.cover_letter,
                                 status = "applied",
                                 applied_at = datetime.utcnow())
    db.add(application)
    db.commit()
    db.refresh(application)

    return {
        "message": "Application submitted successfully",
        "application_id": application.id,
        "job_id": request.job_id
    }
    
@router.get("/my-application", response_model=List[JobApplicationResponse] )
def get_application(db : Session=Depends(get_db), current_user=Depends(role_required(["candidate"]))):
    applications = db.query(JobApplication).filter(
        JobApplication.user_id == current_user.id
    ).all()
    
    return [JobApplicationResponse.model_validate(app) for app in applications]
