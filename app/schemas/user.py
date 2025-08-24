from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from enum import Enum

class UserRoleEnum(str, Enum):
    candidate = "candidate"
    recruiter = "recruiter"
    admin = "admin"


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    role: UserRoleEnum =Field(..., alias="userrole")

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRoleEnum = Field(..., alias="userrole")

    class Config:
        from_attributes = True
        use_enum_values = True
