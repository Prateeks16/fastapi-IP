from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum as PyEnum

class UserRoleEnum(str, PyEnum):
    candidate = "candidate"
    recruiter = "recruiter"
    admin = "admin"


# For Registration
class UserCreate(BaseModel):
    username: str = Field(..., description="Enter your username", min_length=3, max_length=50)
    password: str = Field(..., description="Enter your password", min_length=6, max_length=100)
    email: EmailStr = Field(..., description="Enter your email")
    userrole : UserRoleEnum = UserRoleEnum.candidate

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    created_at: datetime

    model_config = {"from_attributes": True}

# For login
class UserLogin(BaseModel):
    username: str
    password: str

# JWT token response
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

# Token payload for decoding
class TokenData(BaseModel):
    username: Optional[str] = None