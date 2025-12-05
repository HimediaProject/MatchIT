from fastapi import APIRouter, \
                    Depends, \
                    Response, \
                    Request, \
                    status, \
                    HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any, cast, Union
from src.database import get_db
from src import models


router = APIRouter(prefix="/users")

# schemas 부분
class ProfileOut(BaseModel):
    user_id: int
    name: Optional[str]
    email: str
    career_level: Optional[str] = None
    skills: List[str] = []
    desired_jobs: List[str] = []

    class Config:
        orm_mode = True


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    career_level: Optional[Union[str, int]] = None
    skills: Optional[List[str]] = None
    desired_jobs: Optional[List[str]] = None
    employment_type: Optional[str] = None
    work_type: Optional[str] = None

    
def get_user_data(db: Session, user_id: int):
    user = (
        db.query(models.User)
        .outerjoin(models.CareerLevel, models.User.CareerLevelID == models.CareerLevel.CareerLevelID)
        .filter(models.User.UserID == user_id)
        .first()
    )

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user


@router.get("/{user_id}", response_model=ProfileOut)
def read_profile(user_id: int, db: Session = Depends(get_db)):
    """
    return 어떤것을 해야하는지
    """
    user = get_user_data(db, user_id)
    career_name = None

    user_skills = [s.SkillName for s in user.skills]
    user_desired_jobs = [j.JobName for j in user.desired_jobs]

    career_name = user.career_level.CareerName if user.career_level else None

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
    if data.name is not None:
        user.Name = data.name
    
    # 이메일
    if data.email is not None:
        user.Email = data.email

    # 경력 레벨
    if data.career_level is not None:
        # 문자열인 경우
        if isinstance(data.career_level, str):
            career = db.query(models.CareerLevel).filter(
                models.CareerLevel.CareerName == data.career_level
            ).first()
            if not career:
                raise HTTPException(400, "존재하지 않는 커리어 레벨 이름입니다.")

            user.CareerLevelID = career.CareerLevelID

        # 숫자인 경우
        elif isinstance(data.career_level, int):
            career = db.query(models.CareerLevel).filter(
                models.CareerLevel.CareerLevelID == data.career_level
            ).first()
            if not career:
                raise HTTPException(400, "유효하지 않은 커리어 레벨 ID입니다.")

            user.CareerLevelID = data.career_level

            

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


    # # 3) 스킬 (존재하지 않으면 오류 ver)
    # if data.skills is not None:
    #     new_skill_objs = []
    #     for name in data.skills:
    #         skill = db.query(models.Skill).filter(models.Skill.SkillName == name).first()
    #         if not skill:
    #             raise HTTPException(status_code=400, detail=f"존재하지 않는 스킬: {name}")
    #         new_skill_objs.append(skill)
    #     user.skills = new_skill_objs


    # # 4) 희망직무 (존재하지 않으면 오류 ver)

    # if data.desired_jobs is not None:
    #     new_job_objs = []
    #     for name in data.desired_jobs:
    #         job = db.query(models.DesiredJob).filter(models.DesiredJob.JobName == name).first()
    #         if not job:
    #             raise HTTPException(status_code=400, detail=f"존재하지 않는 희망직무: {name}")
    #         new_job_objs.append(job)
    #     user.desired_jobs = new_job_objs

    db.commit()
    db.refresh(user)

    return read_profile(user.UserID, db)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)