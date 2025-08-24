from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session
from database.connection import get_db
from database.models import Interview

def get_interview_or_404(interview_id: int, db: Session = Depends(get_db)):
    interview = db.query(Interview).filter(Interview.id == interview_id).first()
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview
