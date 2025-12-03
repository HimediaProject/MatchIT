from fastapi import APIRouter, \
                    Depends, \
                    Response, \
                    Request, \
                    status, \
                    HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, cast
from src.database import get_db
from src import models


router = APIRouter(prefix="/users")

# schemas 부분
class ProfileOut(BaseModel):
    user_id: int
    name: Optional[str]
    email: str
    career_level: Optional[Dict[str, Any]] = None
    skills: List[str] = []
    desired_jobs: List[str] = []

    class Config:
        orm_mode = True


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    career_level_id: Optional[int] = None
    skills: Optional[List[str]] = None
    desired_jobs: Optional[List[str]] = None
    employment_type: Optional[str] = None
    work_type: Optional[str] = None

    
def get_user_data(db: Session, user_id: int):
    user = db.query(models.User).filter(models.User.UserID == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user


@router.get("/{user_id}", response_model=ProfileOut)
def read_profile(user_id: int, db: Session = Depends(get_db)):
    user = get_user_data(db, user_id)

    career_name = None
    if user.CareerLevelID:
        career = db.query(models.CareerLevel).filter(models.CareerLevel.CareerLevelID == user.CareerLevelID).first()
        if career:
            career_name = career.CareerName

    user_skills = [s.SkillName for s in user.skills]
    user_desired_jobs = [j.JobName for j in user.desired_jobs]

    return ProfileOut(
        user_id=user.UserID,
        name=user.Name,
        email=user.Email,
        career_level=career_name,
        skills=user_skills,
        desired_jobs=user_desired_jobs
    )



@router.put("/{user_id}", response_model=ProfileOut)
def update_profile(user_id: int, data: ProfileUpdate, db: Session = Depends(get_db)):
    user = get_user_data(db, user_id)

    # 이름
    if data.name:
        user.Name = data.name

    # 경력 레벨
    if data.career_level_id:
        career = db.query(models.CareerLevel).filter(
            models.CareerLevel.CareerLevelID == data.career_level_id
        ).first()
        if not career:
            raise HTTPException(400, "커리어 레벨에 오류가 있습니다.")
        user.CareerLevelID = data.career_level_id

    # 스킬
    if data.skills is not None:
        new_skill_objs = []
        for name in data.skills:
            skill = db.query(models.Skill).filter(models.Skill.SkillName == name).first()
            if not skill:
                skill = models.Skill(SkillName=name)
                db.add(skill)
                db.commit()
            new_skill_objs.append(skill)

        user.skills = new_skill_objs


    # 4) 희망직무
    if data.desired_jobs is not None:
        new_job_objs = []
        for name in data.desired_jobs:
            job = db.query(models.DesiredJob).filter(models.DesiredJob.JobName == name).first()
            if not job:
                job = models.DesiredJob(JobName=name)
                db.add(job)
                db.commit()
            new_job_objs.append(job)

        user.desired_jobs = new_job_objs

    db.commit()
    db.refresh(user)

    return read_profile(user.UserID, db)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)

    
    
    
    
































# 1.이전 버전의 수정 엔드포인트
# @router.put("/mypage/{user_id}", response_model=ProfileOut)
# def update_profile(payload: ProfileUpdate, user_id: int, db: Session = Depends(get_db)):

#     user = get_user_data(db, user_id)

#     # name
#     if payload.name is not None:
#         user.Name = payload.name

#     # career level
#     if payload.career_level_id is not None:
#         cl = db.query(models.CareerLevel).filter(models.CareerLevel.CareerLevelID == payload.career_level_id).first()
#         if not cl:
#             raise HTTPException(status_code=400, detail="잘못된 접근입니다.")
#         user.CareerLevelID = payload.career_level_id

#     # skills 
#     if payload.skills is not None:
#         new_skills = [_get_or_create_skill(db, n) for n in payload.skills]
#         user.skills = new_skills

#     # desired_jobs 
#     if payload.desired_jobs is not None:
#         new_jobs = [_get_or_create_desired_job(db, n) for n in payload.desired_jobs]
#         user.desired_jobs = new_jobs


#     if payload.employment_type is not None or payload.work_type is not None:
#         raise HTTPException(
#             status_code=400,
#             detail="올바른 형식이 아닙니다."
#         )

#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     career = None
#     if getattr(user, "CareerLevelID", None):
#         cl = db.query(models.CareerLevel).filter(models.CareerLevel.CareerLevelID == user.CareerLevelID).first()
#         if cl:
#             career = {"id": cl.CareerLevelID, "name": cl.CareerName}
#     skills = [s for s in getattr(user, "skills", [])] if getattr(user, "skills", None) else []
#     desired_jobs = [j for j in getattr(user, "desired_jobs", [])] if getattr(user, "desired_jobs", None) else []

#     return ProfileOut(
#         user_id=user.UserID,
#         name=user.Name,
#         email=user.Email,
#         career_level=career,
#         skills=skills,
#         desired_jobs=desired_jobs,
#     )