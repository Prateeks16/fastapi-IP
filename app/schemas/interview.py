from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class InterviewBase(BaseModel):
    title: str
    description: Optional[str] = None
    job_description: str

class InterviewCreate(InterviewBase):
    created_by: int

class InterviewOut(InterviewBase):
    id: int
    link_token: str
    created_by: int
    created_at: datetime

    class Config:
        from_attributes = True