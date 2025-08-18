from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from typing import List
from schemas.job import JobBase, JobCreate, JobResponse, JobUpdate
from database.connection import get_db
from database.models import JobDetails
from sqlalchemy.orm import Session
from core.roles import role_required

router = APIRouter(tags=["CRUD JOB"])

@router.post("/job/", status_code=status.HTTP_201_CREATED, response_model=JobResponse)
def create_job(request : JobCreate, db : Session=Depends(get_db), current_user=Depends(role_required(["recruiter", "admin"]))):
    new_job = JobDetails(
        title = request.title,
        description = request.description,
        skills = ",".join(request.skills),
        salary = request.salary,
        created_by = current_user.id
    )
    db.add(new_job)
    db.commit()
    db.refresh(new_job)
    new_job.skills = new_job.skills.split(",")
    return new_job

@router.get("/jobs/{job_id}", response_model=JobResponse)
def get_jobs_by_id(job_id : int, response : Response, db : Session=Depends(get_db) ,current_user=Depends(role_required(["recruiter", "admin", "candidate"]))):
    job = db.query(JobDetails).filter(JobDetails.id == job_id).first()
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The job id {job_id} is not found")
    job.skills = job.skills.split(",")
    return job

@router.delete("/jobs/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job(job_id : int, db : Session=Depends(get_db), current_user=Depends(role_required(["recruiter", "admin"]))):
    jobs = db.query(JobDetails).filter(JobDetails.id == job_id).first()
    if not jobs: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="The job id {job_id} does not exist")
    db.delete(jobs)
    db.commit()
    return JSONResponse(content={"message": "Job deleted successfully"}, status_code=status.HTTP_200_OK)



@router.patch("/jobs/{job_id}", response_model=JobResponse)
def update_job(job_id: int, request: JobUpdate, db: Session = Depends(get_db), current_user=Depends(role_required(["recruiter", "admin"]))):
    job = db.query(JobDetails).filter(JobDetails.id == job_id).first()
    if not job: 
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"The job id {job_id} does not exist")

    update_data = request.dict(exclude_unset=True)  # only provided fields
    if "skills" in update_data and isinstance(update_data["skills"], list):
        update_data["skills"] = ",".join(update_data["skills"])

    for key, value in update_data.items():
        setattr(job, key, value)

    db.commit()
    db.refresh(job)
    job.skills = job.skills.split(",")
    return job


@router.get("/jobs/", response_model=List[JobResponse])
def list_jobs(db: Session = Depends(get_db),current_user=Depends(role_required(["recruiter", "admin", "candidate"]))):
    jobs = db.query(JobDetails).all()
    for job in jobs:
        job.skills = job.skills.split(",") if job.skills else []
    return jobs
