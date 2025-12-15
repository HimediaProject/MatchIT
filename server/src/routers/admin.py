from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from typing import List, Optional
from src.database import get_db
from src import models
from datetime import datetime

router = APIRouter(prefix="/admin", tags=["admin"])

# ========== Schemas ==========

class UserOut(BaseModel):
    userid: int
    email: str
    name: Optional[str]
    role: str

    class Config:
        from_attributes = True


class UserRoleUpdate(BaseModel):
    role: str  # "user" or "admin"


class JobPostOut(BaseModel):
    jobid: int
    jobtitle: str
    jobdescription: Optional[str]

    class Config:
        from_attributes = True


class JobPostUpdate(BaseModel):
    jobtitle: Optional[str] = None
    jobdescription: Optional[str] = None


class BootcampOut(BaseModel):
    bootcampid: int
    bootcampname: str
    description: Optional[str] = None

    class Config:
        from_attributes = True


class BootcampUpdate(BaseModel):
    bootcampname: Optional[str] = None
    description: Optional[str] = None


# ========== 권한 확인 함수 ==========

def check_admin_role(db: Session = Depends(get_db)):
    """
    관리자 역할 확인
    현재 사용자가 관리자인지 확인하는 의존성
    """
    # 주의: 실제 구현에서는 JWT에서 사용자 정보를 추출해야 합니다
    # 현재는 예시 구현입니다
    # from src.routers.jwt_login import get_current_user
    # user = get_current_user(...)
    # if user.role != "admin":
    #     raise HTTPException(status_code=403, detail="Admin access required")
    # return user
    pass


# ========== 회원 관리 API ==========

@router.get("/users", response_model=List[UserOut])
def get_all_users(db: Session = Depends(get_db)):
    """
    모든 사용자 조회
    """
    try:
        users = db.query(models.User).all()
        return users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get users: {str(e)}")


@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
    사용자 삭제
    """
    try:
        user = db.query(models.User).filter(models.User.UserID == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # 사용자와 관련된 데이터 정리
        db.query(models.UserDesiredJob).filter(
            models.UserDesiredJob.UserID == user_id
        ).delete()
        db.query(models.UserSkill).filter(
            models.UserSkill.UserID == user_id
        ).delete()
        db.query(models.UserNotificationSetting).filter(
            models.UserNotificationSetting.UserID == user_id
        ).delete()
        db.query(models.UserScrap).filter(
            models.UserScrap.UserID == user_id
        ).delete()
        db.query(models.SocialLogin).filter(
            models.SocialLogin.UserID == user_id
        ).delete()

        # 사용자 삭제
        db.delete(user)
        db.commit()

        return {"message": "User deleted successfully", "user_id": user_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete user: {str(e)}")


@router.patch("/users/{user_id}/role", response_model=UserOut)
def update_user_role(user_id: int, data: UserRoleUpdate, db: Session = Depends(get_db)):
    """
    사용자 역할 변경 (admin 또는 user)
    """
    try:
        # 역할 검증
        if data.role not in ["user", "admin"]:
            raise HTTPException(status_code=400, detail="Invalid role. Must be 'user' or 'admin'")

        # 역할 ID 조회
        role = db.query(models.Role).filter(models.Role.Name == data.role).first()
        if not role:
            raise HTTPException(status_code=404, detail="Role not found")

        user = db.query(models.User).filter(models.User.UserID == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.RoleID = role.RoleID
        db.commit()
        db.refresh(user)

        return user
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update user role: {str(e)}")


# ========== 채용 공고 관리 API ==========

@router.get("/jobposts", response_model=List[JobPostOut])
def get_all_jobposts(db: Session = Depends(get_db)):
    """
    모든 채용 공고 조회
    """
    try:
        jobposts = db.query(models.JobPost).all()
        return jobposts
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get job posts: {str(e)}")


@router.patch("/jobposts/{job_id}", response_model=JobPostOut)
def update_jobpost(job_id: int, data: JobPostUpdate, db: Session = Depends(get_db)):
    """
    채용 공고 수정
    """
    try:
        jobpost = db.query(models.JobPost).filter(models.JobPost.JobID == job_id).first()
        if not jobpost:
            raise HTTPException(status_code=404, detail="Job post not found")

        if data.jobtitle is not None:
            jobpost.JobTitle = data.jobtitle
        if data.jobdescription is not None:
            jobpost.JobDescription = data.jobdescription

        jobpost.UpdatedAt = datetime.now()
        db.commit()
        db.refresh(jobpost)

        return jobpost
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update job post: {str(e)}")


@router.delete("/jobposts/{job_id}")
def delete_jobpost(job_id: int, db: Session = Depends(get_db)):
    """
    채용 공고 삭제
    """
    try:
        jobpost = db.query(models.JobPost).filter(models.JobPost.JobID == job_id).first()
        if not jobpost:
            raise HTTPException(status_code=404, detail="Job post not found")

        # 관련 데이터 정리
        db.query(models.JobPostSkill).filter(
            models.JobPostSkill.JobID == job_id
        ).delete()
        db.query(models.UserScrap).filter(
            models.UserScrap.JobID == job_id
        ).delete()

        db.delete(jobpost)
        db.commit()

        return {"message": "Job post deleted successfully", "job_id": job_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete job post: {str(e)}")


# ========== 부트캠프 관리 API ==========

@router.get("/bootcamps", response_model=List[BootcampOut])
def get_all_bootcamps(db: Session = Depends(get_db)):
    """
    모든 부트캠프 조회
    """
    try:
        bootcamps = db.query(models.Bootcamp).all()
        return bootcamps
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get bootcamps: {str(e)}")


@router.patch("/bootcamps/{bootcamp_id}", response_model=BootcampOut)
def update_bootcamp(bootcamp_id: int, data: BootcampUpdate, db: Session = Depends(get_db)):
    """
    부트캠프 수정
    """
    try:
        bootcamp = db.query(models.Bootcamp).filter(
            models.Bootcamp.BootcampID == bootcamp_id
        ).first()
        if not bootcamp:
            raise HTTPException(status_code=404, detail="Bootcamp not found")

        if data.bootcampname is not None:
            bootcamp.BootcampName = data.bootcampname
        if data.description is not None:
            bootcamp.Description = data.description

        bootcamp.UpdatedAt = datetime.now()
        db.commit()
        db.refresh(bootcamp)

        return bootcamp
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to update bootcamp: {str(e)}")


@router.delete("/bootcamps/{bootcamp_id}")
def delete_bootcamp(bootcamp_id: int, db: Session = Depends(get_db)):
    """
    부트캠프 삭제
    """
    try:
        bootcamp = db.query(models.Bootcamp).filter(
            models.Bootcamp.BootcampID == bootcamp_id
        ).first()
        if not bootcamp:
            raise HTTPException(status_code=404, detail="Bootcamp not found")

        # 관련 데이터 정리 (필요시)
        db.query(models.UserScrap).filter(
            models.UserScrap.BootcampID == bootcamp_id
        ).delete()

        db.delete(bootcamp)
        db.commit()

        return {"message": "Bootcamp deleted successfully", "bootcamp_id": bootcamp_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to delete bootcamp: {str(e)}")
# Note: 실제로는 JWT 인증을 통해 현재 사용자의 역할을 확인하는 로직이 필요합니다.