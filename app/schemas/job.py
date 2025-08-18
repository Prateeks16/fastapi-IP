from pydantic import BaseModel, Field, validator
from typing import Optional, Annotated, List
from datetime import datetime
from enum import Enum

class JobBase(BaseModel):
    title : Annotated[str, Field(...)]
    description : Annotated[str, Field(...)]
    skills : Annotated[List[str], Field(...)]
    salary : Annotated[str, Field(...)]

class JobCreate(JobBase):
    pass

class JobUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    skills: Optional[List[str]] = None
    salary: Optional[str] = None


class JobResponse(JobBase):
    id: int
    created_at: datetime
    created_by: int

    class Config:
        from_attributes = True
    @validator("skills", pre=True)
    def split_skills(cls, v):
        return v.split(",") if isinstance(v, str) else v

class ApplicationStatus(str, Enum):
    pending = "pending"
    shortlisted = "shortlisted"
    rejected = "rejected"
    applied = "applied"

class JobApplicationBase(BaseModel):
    cover_letter: Optional[str] = None

class JobApplicationCreate(JobApplicationBase):
    job_id: int

class JobApplicationUpdate(BaseModel):
    status: ApplicationStatus

class JobApplicationResponse(BaseModel):
    application_id: int
    job_id: int
    job_title: str
    status: str
    cover_letter: str
    applied_at: datetime
    job : JobBase

    class Config:
        from_attributes = True
