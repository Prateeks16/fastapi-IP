from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
import jwt as pyjwt
from passlib.context import CryptContext
from core.config import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM
from schemas.user import TokenData, UserCreate, UserOut, Token
from datetime import datetime, timedelta, timezone
from fastapi import HTTPException, status, Depends, APIRouter
from typing import Annotated
from database.connection import get_db
from database.models import Users, UserRole
from sqlalchemy.orm import Session

router = APIRouter(tags=["Authentication and Authorisation"])

pwd_cxt = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Token URL for Swagger "Authorize" button
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login", scheme_name="Bearer")

# ------------------------------
# PASSWORD HASHING
# ------------------------------
def hash_password(plain_password: str):
    return pwd_cxt.hash(plain_password)

def verify_password(plain_password, hashed_password):
    return pwd_cxt.verify(plain_password, hashed_password)

# ------------------------------
# TOKEN CREATION
# ------------------------------
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = pyjwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# ------------------------------
# GET CURRENT USER
# ------------------------------
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = pyjwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        if username is None or role is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except pyjwt.InvalidTokenError:
        raise credentials_exception

    user = db.query(Users).filter(Users.username == token_data.username).first()
    if not user:
        raise credentials_exception

    # Enum comparison fix
    if user.userrole.value != role:
        raise credentials_exception

    return user

# ------------------------------
# LOGIN ROUTE
# ------------------------------
@router.post("/login", response_model=Token)
def login_user(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    db_user = db.query(Users).filter(Users.username == form_data.username).first()

    if not db_user or not verify_password(form_data.password, db_user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password")

    access_token = create_access_token(
        data={"sub": db_user.username, "role": db_user.userrole.value},  # Enum fix
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )

    return {"access_token": access_token, "token_type": "bearer"}

# ------------------------------
# GET CURRENT LOGGED-IN USER
# ------------------------------
@router.get("/me", response_model=UserOut)
def read_users_me(current_user: Users = Depends(get_current_user)):
    return current_user

# ------------------------------
# REGISTER ROUTE
# ------------------------------
@router.post("/register", response_model=UserOut)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    if db.query(Users).filter(Users.username == user.username).first():
        raise HTTPException(status_code=400, detail="Username already taken")
    if db.query(Users).filter(Users.email == user.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        role_enum = UserRole(user.userrole)  
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid role value")

    new_user = Users(
        username=user.username,
        email=user.email,
        userrole=role_enum,
        password_hash=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user
