from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class QuestionCreate(BaseModel):
    question_text: str = Field(..., min_length=1, max_length=500)
    category: Optional[str] = Field(None, min_length=1)
    difficulty: Optional[str] = None

class QuestionOut(BaseModel):
    id: int
    question_text: str
    category: Optional[str] = None
    difficulty: Optional[str] = None
    created_at: datetime
