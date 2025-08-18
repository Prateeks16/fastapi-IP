from database.connection import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum


class UserRole(enum.Enum):
    candidate = "candidate"
    recruiter = "recruiter"
    admin = "admin"


class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username =  Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    userrole = Column(Enum(UserRole), default=UserRole.candidate, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sessions = relationship("InterviewSession", back_populates="user")
    jobs = relationship("JobDetails", back_populates="creator")
    applications = relationship("JobApplication", back_populates="user")



class Questions(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True)
    question_text = Column(String, nullable=False)
    category = Column(String)
    difficulty = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)

class InterviewSession(Base):
    __tablename__ = 'interview_session'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    answers = relationship("Answers", back_populates="session")
    user = relationship("Users", back_populates="sessions")
    performance_review = relationship("PerformanceReview", back_populates="session", uselist=False)



class Answers(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("questions.id"))
    session_id = Column(Integer, ForeignKey("interview_session.id"))
    answer_text = Column(String)
    video_path = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("InterviewSession", back_populates="answers")
    question = relationship("Questions")

class PerformanceReview(Base):
    __tablename__ = 'performance_review'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("interview_session.id"))
    overall_score = Column(Integer)
    strengths = Column(String)
    weakness = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    session = relationship("InterviewSession", back_populates="performance_review")


class JobDetails(Base):
    __tablename__ = "job_details"  
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=False)
    skills = Column(String, nullable=False)  
    salary = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    creator = relationship("Users", back_populates="jobs")
    applications = relationship("JobApplication", back_populates="job")

class ApplicationStatus(enum.Enum):
    pending = "pending"
    shortlisted = "shortlisted"
    rejected = "rejected"
    applied = "applied"


class JobApplication(Base):
    __tablename__ = "job_application"
    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, ForeignKey("job_details.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False) 
    cover_letter = Column(String)
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.pending, nullable=False)
    applied_at = Column(DateTime, default=datetime.utcnow)
    job = relationship("JobDetails", back_populates="applications")
    user = relationship("Users", back_populates="applications")
