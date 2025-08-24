from pydantic import BaseModel, Field
from typing import Optional, Annotated
from datetime import datetime

class AnswerCreate(BaseModel):
    question_id: int
    answer_text: Optional[Annotated[str, Field(min_length=1)]] = None
    video_path: str

class PerformanceReviewOut(BaseModel):
    id: int
    overall_score: int


class CandidateResponse(BaseModel):
    interview_id: int
    candidate_name: str
    candidate_email: str
    answers: list[str] = []
    video_url: Optional[str] = None
    transcript: Optional[str] = None

class Evaluation(BaseModel):
    response_id: int
    score: float
    feedback: str
    strengths: list[str]
    weaknesses: list[str]
