from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import JSONResponse
from typing import List
from schemas.job import JobApplicationCreate,JobApplicationResponse,JobApplicationUpdate
from database.connection import get_db
from database.models import JobApplication, JobDetails
from sqlalchemy.orm import Session
from core.roles import role_required
from schemas.job import JobApplicationCreate
from datetime import datetime


router = APIRouter(tags=["Recruiter Panel"])

