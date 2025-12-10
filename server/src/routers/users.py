from fastapi import APIRouter, \
                    Depends, \
                    Response, \
                    Request, \
                    status, \
                    HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any, cast, Union
from src.database import get_db
from src import models


router = APIRouter(prefix="/users", tags=['유저 프로필 기능'])

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

class JobPostOut(BaseModel):
    id: int
    title: Optional[str] = None
    company_name: Optional[str] = None

    class Config:
        orm_mode = True

class BootcampPostOut(BaseModel):
    id: int
    title: Optional[str] = None
    institute_name: Optional[str] = None

    class Config:
        orm_mode = True

class UserScrapGet(BaseModel):
    '''
    endpoint:
        /users/{user_id}/scraps

    params:
        post_type,
        job_post_id, bootcamp_post_id

    description:
        특정 유저가 스크랩한 항목(직무/부트캠프)의 목록을 조회.
        filter를 통해, 직무 또는 부트캠프 별로 필터링.
    '''
    post_type: Optional[str] = None
    job_post_id: Optional[int] = None
    bootcamp_post_id: Optional[int] = None
    job_post: Optional[JobPostOut] = None
    bootcamp_post: Optional[BootcampPostOut] = None

    class Config:
        orm_mode = True

class UserNotifications(BaseModel):
    notification_type: Optional[str] = None
    isenabled: Optional[bool] = None
    notificationtime: Optional[str] = None

    class Config:
        orm_mode = True

class UserNotificationsUpdate(BaseModel):
    notification_type: Optional[str] = None
    isenabled: Optional[bool] = None
    notificationtime: Optional[str] = None

    class Config:
        orm_mode = True
    
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

def get_user_scrap(db: Session, user_id: int):
    return (
        db.query(models.UserScrap)
        .options(joinedload(models.UserScrap.job_post))
        .options(joinedload(models.UserScrap.bootcamp_post))
        .filter(models.UserScrap.UserID == user_id)
        .all()
    )

def get_user_notifications(db: Session, user_id: int):
    notifications = (
        db.query(models.UserNotificationSetting)
        .filter(models.UserNotificationSetting.UserID == user_id)
        .all()
    )

    if not notifications:
        raise HTTPException(status_code=404, detail="알림 항목을 찾을 수 없습니다.")
    return notifications

@router.get("/{user_id}", response_model=ProfileOut)
def read_profile(user_id: int, db: Session = Depends(get_db)):
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


@router.patch("/me", response_model=ProfileOut)
def update_my_profile(data: ProfileUpdate, db: Session = Depends(get_db), request: Request = None):
    """현재 로그인한 사용자의 프로필 업데이트"""
    # 세션 또는 쿠키에서 사용자 ID 추출
    # authApi.getCurrentUser()와 동일한 로직으로 user_id 가져옴
    if not hasattr(request, 'session') or 'user_id' not in request.session:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")
    
    user_id = request.session.get('user_id')
    return update_profile(user_id, data, db)


@router.get("/{user_id}/scraps", response_model=List[UserScrapGet])
def read_userscrap(user_id: int, db: Session = Depends(get_db)):
    scraps = get_user_scrap(db, user_id)

    result = []

    for scrap in scraps:

        if scrap.PostType == "Job" and scrap.job_post:
            job_post = JobPostOut(
                id=scrap.job_post.PostID,
                title=scrap.job_post.Title,
                company_name=scrap.job_post.CompanyName,
            )
        else:
            job_post = None

        if scrap.PostType == "Bootcamp" and scrap.bootcamp_post:
            bootcamp_post = BootcampPostOut(
                id=scrap.bootcamp_post.BootcampID,
                title=scrap.bootcamp_post.Title,
                institute_name=scrap.bootcamp_post.InstituteName,
            )
        else:
            bootcamp_post = None

        result.append(
            UserScrapGet(
                post_type=scrap.PostType,
                job_post_id=scrap.JobPostID,
                bootcamp_post_id=scrap.BootcampPostID,
                job_post=job_post,
                bootcamp_post=bootcamp_post
            )
        )
    return result


@router.get("/{user_id}/notifications", response_model=List[UserNotifications])
def read_notifications(user_id: int, db: Session = Depends(get_db)):
    notifications = get_user_notifications(db, user_id)

    if not notifications:
        raise HTTPException(404, "알림 항목을 찾을 수 없습니다.")
    
    return [
        UserNotifications(
            notification_type=n.NotificationType,
            isenabled=n.IsEnabled,
            notificationtime=n.NotificationTime,
        )
        for n in notifications
    ]


# @router.put("/{user_id}/notifications", response_model=UserNotificationsUpdate)
# def update_notifications(user_id: int, db: Session = Depends(get_db)):
#     notifications = get_user_notifications(db, user_id)

#     return UserNotifications(
#         notification_type=notifications.NotificationType,
#         isenabled=notifications.IsEnabled,
#         notificationtime=notifications.NotificationTime,
#     )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)