from database.connection import Base
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

# -------------------------------
# User Roles
# -------------------------------
class UserRole(enum.Enum):
    candidate = "candidate"
    recruiter = "recruiter"
    admin = "admin"

# -------------------------------
# Users Table
# -------------------------------
class Users(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    email = Column(String, nullable=False, unique=True)
    userrole = Column(Enum(UserRole), default=UserRole.candidate, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    sessions = relationship("InterviewSession", back_populates="user")
    jobs = relationship("JobDetails", back_populates="creator")
    interviews = relationship("Interview", back_populates="creator")
    resumes = relationship("Resumes", back_populates="user")




class Resumes(Base):
    __tablename__ = "resumes"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    file_path = Column(String, nullable=False)
    parsed_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("Users", back_populates="resumes")

# -------------------------------
# Interview Table
# -------------------------------
class Interview(Base):
    __tablename__ = "interviews"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    job_description = Column(Text, nullable=False)
    link_token = Column(String, unique=True, index=True)
    resume_text = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    creator = relationship("Users", back_populates="interviews")
    questions = relationship("InterviewQuestions", back_populates="interview", cascade="all, delete-orphan")

# -------------------------------
# InterviewQuestions Table
# -------------------------------
class InterviewQuestions(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)
    interview_id = Column(Integer, ForeignKey("interviews.id", ondelete="CASCADE"))
    question_text = Column(String, nullable=False)
    category = Column(String, nullable=True)
    source = Column(String, default="general")  # "manual" | "general" | "resume"
    difficulty = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Relationships
    interview = relationship("Interview", back_populates="questions")
    answers = relationship("Answers", back_populates="question", cascade="all, delete-orphan")

# -------------------------------
# InterviewSession Table
# -------------------------------
class InterviewSession(Base):
    __tablename__ = 'interview_session'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), index=True)
    start_time = Column(DateTime, default=datetime.utcnow)
    end_time = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)

    answers = relationship("Answers", back_populates="session", cascade="all, delete-orphan")
    user = relationship("Users", back_populates="sessions")
    performance_review = relationship("PerformanceReview", back_populates="session", uselist=False)

# -------------------------------
# Answers Table
# -------------------------------
class Answers(Base):
    __tablename__ = 'answers'
    id = Column(Integer, primary_key=True)
    question_id = Column(Integer, ForeignKey("interview_questions.id", ondelete="CASCADE"))
    session_id = Column(Integer, ForeignKey("interview_session.id", ondelete="CASCADE"))
    answer_text = Column(Text, nullable=True)
    video_path = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="answers")
    question = relationship("InterviewQuestions", back_populates="answers")

# -------------------------------
# PerformanceReview Table
# -------------------------------
class PerformanceReview(Base):
    __tablename__ = 'performance_review'
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("interview_session.id"))
    overall_score = Column(Integer, nullable=False)
    strengths = Column(Text, nullable=True)
    weakness = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="performance_review")

# -------------------------------
# JobDetails Table
# -------------------------------
class JobDetails(Base):
    __tablename__ = "job_details"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    company_name = Column(String, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"))
    created_at = Column(DateTime, default=datetime.utcnow)

    creator = relationship("Users", back_populates="jobs")
