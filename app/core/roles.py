from fastapi import Depends, HTTPException, status, APIRouter
from core.security import get_current_user



router = APIRouter(tags=["Roles in APP"])

def role_required(allowed_roles: list[str]):
    def wrapper(current_user=Depends(get_current_user)):
        if current_user.userrole.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have access to this resource"
            )
        return current_user
    return wrapper

@router.post("/job-creater")
def create_job( current_user=Depends(role_required(["recruiter"]))):
    return {"message": "Job created successfully"}

@router.get("/jobs-seeker")
def list_jobs(current_user=Depends(role_required(["candidate"]))):
    return {"message": "Job list"}

@router.post("/admin")
def admin_dashboard(current_user=Depends(role_required(["admin"]))):
    return {"message" : f"Welcome Admin {current_user.username}"}
