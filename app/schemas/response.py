from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime

class AnswerCreate(BaseModel):
    question_id: int
    answer_text: Optional[Annotated[str, Field(min_length=1)]] = None
    video_path: str

class AnswerOut(BaseModel):
    id: int
    question_id: int
    session_id: int
    answer_text: Optional[str] = None
    video_path: str
    created_at: datetime

class PerformanceReviewOut(BaseModel):
    id: int
    overall_score: str
