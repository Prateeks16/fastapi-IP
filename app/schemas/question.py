from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime



class QuestionCreate(BaseModel):
    question_text: str = Field(..., min_length=1, max_length=500)
    category: Optional[str] = Field(None, min_length=1)
    difficulty: Optional[str] = None
    interview_id: int
    source: Optional[str] = Field(None, min_length=1)  # e.g., "manual", "resume", "ml" 


class QuestionOut(BaseModel):
    id: int
    question_text: str
    category: Optional[str] = None
    difficulty: Optional[str] = None
    created_at: datetime
    interview_id: int  

    class Config:
        from_attributes = True

class QuestionUpdate(BaseModel):
    question_text: Optional[str] = None
    category: Optional[str] = None
    difficulty: Optional[str] = None