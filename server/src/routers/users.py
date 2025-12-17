from fastapi import APIRouter, \
                    Depends, \
                    Response, \
                    Request, \
                    status, \
                    HTTPException, \
                    Cookie
from pydantic import BaseModel, Field, EmailStr, field_validator
from sqlalchemy.orm import Session, joinedload
from typing import List, Optional, Dict, Any, cast, Union
from src.database import get_db
from src import models
from datetime import datetime
from fastapi import Depends as _Depends
import logging
import uuid
import json
from sqlalchemy.exc import IntegrityError

logger = logging.getLogger(__name__)
from src.schemas import UserScrapPost


router = APIRouter(prefix="/users", tags=['유저 프로필 기능'])

# schemas 부분
class ProfileOut(BaseModel):
    user_id: int
    name: Optional[str]
    email: Optional[str] = None
    experience_range: Optional[str] = None
    career_level: Optional[str] = None
    skills: List[str] = []
    desired_jobs: List[str] = []
    recentviews: Optional[List[str]] = None

    class Config:
        orm_mode = True


class ProfileUpdate(BaseModel):
    name: Optional[str] = Field(
        None,
        min_length=2,
        max_length=30,
        example="홍길동",
        description="사용자 이름 (2~30자)"
    )
    email: Optional[EmailStr] = Field(
        None,
        example="honggildong@example.com",
        description="유효한 이메일 주소"
    )
    career_level: Optional[Union[str, int]] = Field(
        None,
        example="신입",
        description="커리어 레벨 (예: 신입, 경력 또는 코드값)"
    )
    experience_range: Optional[Union[str, int]] = Field(
    None,
    examples=[
        "1년 미만",
        "3~5년",
        "5년 이상",
        0,
        3
    ],
    description="경력 범위 (자연어 또는 코드값)"
    )
    role_id: Optional[int] = Field(
        None,
        ge=1,
        example=2,
        description="역할 ID (1 이상의 정수)"
    )
    skills: Optional[List[Union[str, int, Dict[str, Any]]]] = Field(
        None,
        example=[
            "Python",
            3,
            {"skillid": 5, "skillname": "FastAPI"}
        ],
        description="보유 기술 목록"
    )
    desired_jobs: Optional[List[Union[str, int, Dict[str, Any]]]] = Field(
        None,
        example=[
            "Backend Developer",
            {"desiredjobid": 2, "jobname": "API Engineer"}
        ],
        description="희망 직무 목록"
    )
    recentviews: Optional[List[str]] = None

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

class UserRecentViewsGet(BaseModel):
    '''
    endpoint:
        /users/{user_id}/recentviews

    params:
        post_type,
        job_post_id, bootcamp_post_id

    description:
        특정 유저가 최근 열람한 항목(직무/부트캠프)의 목록을 조회.
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
    # 관련 관계를 명시적으로 eager load 하여
    # 저장된 스킬/희망직무/커리어 레벨을 확실히 조회하도록 합니다.
    user = (
        db.query(models.User)
        .options(
            joinedload(models.User.career_level),
            joinedload(models.User.experience_range),
            joinedload(models.User.skills),
            joinedload(models.User.desired_jobs),
        )
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
        .order_by(models.UserScrap.ScrappedAt.desc())
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


def get_current_user(db: Session = _Depends(get_db), user_id: Optional[str] = Cookie(None), session_id: Optional[str] = Cookie(None)):
    """Dependency: 쿠키 기반 세션을 검사하고 현재 User 객체를 반환합니다.

    - 소셜 로그인에서 발급한 `user_id`/`session_id` 쿠키를 사용합니다.
    - 세션이 없거나 만료되었으면 HTTPException(401)을 발생시킵니다.
    """
    if not user_id or not session_id:
        raise HTTPException(status_code=401, detail="로그인이 필요합니다.")

    try:
        try:
            session_uuid = uuid.UUID(session_id)
        except Exception:
            raise HTTPException(status_code=401, detail="유효하지 않은 세션입니다.")

        session = (
            db.query(models.UserSession)
            .filter(
                models.UserSession.SessionID == session_uuid,
                models.UserSession.UserID == int(user_id),
            )
            .first()
        )

        if not session:
            raise HTTPException(status_code=401, detail="유효하지 않은 세션입니다.")

        if session.ExpiresAt < datetime.now():
            db.delete(session)
            db.commit()
            raise HTTPException(status_code=401, detail="세션이 만료되었습니다.")

        user = db.query(models.User).filter(models.User.UserID == int(user_id)).first()
        if not user:
            raise HTTPException(status_code=401, detail="존재하지 않는 사용자입니다.")

        return user
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"세션 검증 중 오류: {e}")

@router.get("/me", response_model=ProfileOut)
def get_my_profile(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """현재 로그인한 사용자의 프로필 조회"""
    return read_profile(current_user.UserID, db)


@router.get("/{user_id}", response_model=ProfileOut)
def read_profile(user_id: int, db: Session = Depends(get_db)):
    user = get_user_data(db, user_id)
    career_name = None
    experience_name = None
    user_skills = [s.SkillName for s in user.skills]
    user_desired_jobs = [j.JobName for j in (user.desired_jobs or [])]

    career_name = user.career_level.CareerName if user.career_level else None
    experience_name = user.experience_range.RangeName if getattr(user, 'experience_range', None) else None

    recentviews = None
    _rv = getattr(user, "RecentViews", None)
    if _rv:
        try:
            recentviews = json.loads(_rv)
        except Exception:
            pass

    return ProfileOut(
        user_id=user.UserID,
        name=user.Name,
        email=user.Email,
        career_level=career_name,
        experience_range=experience_name,
        skills=user_skills,
        desired_jobs=user_desired_jobs,
        recentviews=recentviews
    )



@router.put("/{user_id}", response_model=ProfileOut)
def update_profile(user_id: int, data: ProfileUpdate, db: Session = Depends(get_db)):
    logger.info(f"프로필 업데이트 시작 - user_id: {user_id}, data: {data}")
    user = get_user_data(db, user_id)

    # RoleID 업데이트
    if data.role_id is not None:
        if data.role_id > 0:  # 유효한 ID인 경우
            role = db.query(models.Role).filter(models.Role.RoleID == data.role_id).first()
            if not role:
                raise HTTPException(400, "유효하지 않은 역할 ID입니다.")
            user.RoleID = data.role_id
        else:
            # 0이나 음수는 null로 처리
            user.RoleID = None

    # 이름
    if data.name is not None:
        user.Name = data.name
    
    # 이메일
    if data.email is not None:
        next_email = (data.email or "").strip()
        if next_email == "":
            next_email = None

        if next_email is not None:
            dup = (
                db.query(models.User)
                .filter(models.User.Email == next_email, models.User.UserID != user_id)
                .first()
            )
            if dup is not None:
                raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")

        user.Email = next_email

    # 경력 레벨 (잘못된 타입 방지)
    if data.career_level is not None:
        if isinstance(data.career_level, list):
            logger.warning(f"career_level가 list로 전달되어 무시합니다: {data.career_level}")
        # 문자열인 경우
        elif isinstance(data.career_level, str):
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
        else:
            logger.warning(f"career_level 타입을 알 수 없어 무시: {type(data.career_level)}")

    # 경력 구간 (experience range)
    if data.experience_range is not None:
        # DB 컬럼이 없는 환경(초기 스키마)에서도 저장이 실패하지 않도록 보호
        if not hasattr(user, "RangeID"):
            logger.warning("RangeID 컬럼이 없어 experience_range 업데이트를 건너뜁니다.")
        else:
            # list가 들어오면 관계 필드에 할당되지 않도록 방어
            if isinstance(data.experience_range, list):
                logger.warning(f"experience_range가 list로 전달되어 무시합니다: {data.experience_range}")
            # 문자열인 경우: 이름으로 찾기
            elif isinstance(data.experience_range, str):
                if data.experience_range:  # 빈 문자열이 아닌 경우
                    exp = db.query(models.ExperienceRange).filter(
                        models.ExperienceRange.RangeName == data.experience_range
                    ).first()
                    if exp:
                        user.RangeID = exp.RangeID
                    else:
                        user.RangeID = None
                else:
                    user.RangeID = None

            # 숫자인 경우: ID로 설정
            elif isinstance(data.experience_range, int):
                if data.experience_range and data.experience_range > 0:  # 유효한 ID인 경우
                    exp = db.query(models.ExperienceRange).filter(
                        models.ExperienceRange.RangeID == data.experience_range
                    ).first()
                    if exp:
                        user.RangeID = data.experience_range
                        logger.info(f"경력 구간 저장: user_id={user_id}, range_id={data.experience_range}")
                    else:
                        user.RangeID = None
                else:
                    # 0이나 음수는 null로 처리
                    user.RangeID = None
            else:
                logger.warning(f"experience_range 타입을 알 수 없어 무시: {type(data.experience_range)}")

    # 스킬
    if data.skills is not None:
        resolved_skills = []
        seen = set()
        for item in data.skills:
            skill = None

            if isinstance(item, int):
                if item <= 0:
                    continue
                key = f"id:{item}"
                if key in seen:
                    continue
                seen.add(key)
                skill = db.query(models.Skill).filter(models.Skill.SkillID == item).first()
                if not skill:
                    raise HTTPException(400, "유효하지 않은 스킬 ID입니다.")

            elif isinstance(item, dict):
                raw_id = item.get("id") or item.get("skill_id") or item.get("SkillID") or item.get("skillId")
                if isinstance(raw_id, int) and raw_id > 0:
                    key = f"id:{raw_id}"
                    if key in seen:
                        continue
                    seen.add(key)
                    skill = db.query(models.Skill).filter(models.Skill.SkillID == raw_id).first()
                    if not skill:
                        raise HTTPException(400, "유효하지 않은 스킬 ID입니다.")
                else:
                    candidate = item.get("name") or item.get("skill") or item.get("label") or item.get("value")
                    s2 = (candidate or "").strip()
                    if not s2:
                        continue
                    key = f"name:{s2.lower()}"
                    if key in seen:
                        continue
                    seen.add(key)
                    skill = db.query(models.Skill).filter(models.Skill.SkillName == s2).first()
                    if not skill:
                        try:
                            with db.begin_nested():
                                skill = models.Skill(SkillName=s2)
                                db.add(skill)
                                db.flush()
                        except IntegrityError:
                            skill = db.query(models.Skill).filter(models.Skill.SkillName == s2).first()
                            if not skill:
                                raise

            elif isinstance(item, str):
                s2 = (item or "").strip()
                if not s2:
                    continue
                key = f"name:{s2.lower()}"
                if key in seen:
                    continue
                seen.add(key)
                skill = db.query(models.Skill).filter(models.Skill.SkillName == s2).first()
                if not skill:
                    try:
                        with db.begin_nested():
                            skill = models.Skill(SkillName=s2)
                            db.add(skill)
                            db.flush()
                    except IntegrityError:
                        skill = db.query(models.Skill).filter(models.Skill.SkillName == s2).first()
                        if not skill:
                            raise

            if skill is not None:
                resolved_skills.append(skill)

        if user.skills is None:
            user.skills = []
        else:
            user.skills.clear()

        for skill in resolved_skills:
            user.skills.append(skill)

    # 4) 희망직무
    if data.desired_jobs is not None:
        resolved_jobs = []
        seen = set()
        for item in data.desired_jobs:
            job = None

            if isinstance(item, int):
                if item <= 0:
                    continue
                key = f"id:{item}"
                if key in seen:
                    continue
                seen.add(key)
                job = db.query(models.DesiredJob).filter(models.DesiredJob.DesiredJobID == item).first()
                if not job:
                    raise HTTPException(400, "유효하지 않은 희망직무 ID입니다.")

            elif isinstance(item, dict):
                raw_id = item.get("id") or item.get("job_id") or item.get("DesiredJobID") or item.get("desiredJobId")
                if isinstance(raw_id, int) and raw_id > 0:
                    key = f"id:{raw_id}"
                    if key in seen:
                        continue
                    seen.add(key)
                    job = db.query(models.DesiredJob).filter(models.DesiredJob.DesiredJobID == raw_id).first()
                    if not job:
                        raise HTTPException(400, "유효하지 않은 희망직무 ID입니다.")
                else:
                    candidate = item.get("name") or item.get("job") or item.get("label") or item.get("value")
                    j2 = (candidate or "").strip()
                    if not j2:
                        continue
                    key = f"name:{j2.lower()}"
                    if key in seen:
                        continue
                    seen.add(key)
                    job = db.query(models.DesiredJob).filter(models.DesiredJob.JobName == j2).first()
                    if not job:
                        try:
                            with db.begin_nested():
                                job = models.DesiredJob(JobName=j2)
                                db.add(job)
                                db.flush()
                        except IntegrityError:
                            job = db.query(models.DesiredJob).filter(models.DesiredJob.JobName == j2).first()
                            if not job:
                                raise

            elif isinstance(item, str):
                j2 = (item or "").strip()
                if not j2:
                    continue
                key = f"name:{j2.lower()}"
                if key in seen:
                    continue
                seen.add(key)
                job = db.query(models.DesiredJob).filter(models.DesiredJob.JobName == j2).first()
                if not job:
                    try:
                        with db.begin_nested():
                            job = models.DesiredJob(JobName=j2)
                            db.add(job)
                            db.flush()
                    except IntegrityError:
                        job = db.query(models.DesiredJob).filter(models.DesiredJob.JobName == j2).first()
                        if not job:
                            raise

            if job is not None:
                resolved_jobs.append(job)

        if user.desired_jobs is None:
            user.desired_jobs = []
        else:
            user.desired_jobs.clear()
        for job in resolved_jobs:
            user.desired_jobs.append(job)

        user.DesiredJobID = resolved_jobs[0].DesiredJobID if len(resolved_jobs) > 0 else None

    # 최근 열람(문자열 리스트) 저장
    if data.recentviews is not None and hasattr(user, "RecentViews"):
        try:
            setattr(user, "RecentViews", json.dumps(list(data.recentviews), ensure_ascii=False))
        except Exception:
            setattr(user, "RecentViews", None)

    try:
        db.commit()
    except IntegrityError as e:
        db.rollback()
        msg = str(getattr(e, "orig", e))
        if "email" in msg.lower():
            raise HTTPException(status_code=409, detail="이미 사용 중인 이메일입니다.")
        raise
    except Exception:
        db.rollback()
        raise

    db.refresh(user)
    
    logger.info(f"프로필 업데이트 완료 - user_id: {user_id}")

    return read_profile(user.UserID, db)


@router.patch("/me", response_model=ProfileOut)
def update_my_profile(data: ProfileUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """현재 로그인한 사용자의 프로필 업데이트

    `get_current_user` 종속성으로 현재 로그인한 User 객체를 주입받아
    동일한 `update_profile` 로직을 재사용합니다.
    """
    return update_profile(current_user.UserID, data, db)


@router.get("/me/scraps", response_model=List[UserScrapGet])
def read_my_scraps(current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    scraps = get_user_scrap(db, current_user.UserID)
    result: List[UserScrapGet] = []
    for scrap in scraps:
        job_post = None
        bootcamp_post = None

        if scrap.PostType == "Job" and scrap.job_post:
            job_post = JobPostOut(
                id=scrap.job_post.PostID,
                title=scrap.job_post.Title,
                company_name=scrap.job_post.CompanyName,
            )
        if scrap.PostType == "Bootcamp" and scrap.bootcamp_post:
            bootcamp_post = BootcampPostOut(
                id=scrap.bootcamp_post.BootcampID,
                title=scrap.bootcamp_post.Title,
                institute_name=scrap.bootcamp_post.InstituteName,
            )

        result.append(
            UserScrapGet(
                post_type=scrap.PostType,
                job_post_id=scrap.JobPostID,
                bootcamp_post_id=scrap.BootcampPostID,
                job_post=job_post,
                bootcamp_post=bootcamp_post,
            )
        )
    return result


@router.get("/{user_id}/scraps", response_model=List[UserScrapGet])
def read_userscrap(user_id: int, db: Session = Depends(get_db)):
    scraps = get_user_scrap(db, user_id)
    result: List[UserScrapGet] = []
    for scrap in scraps:
        job_post = None
        bootcamp_post = None

        if scrap.PostType == "Job" and scrap.job_post:
            job_post = JobPostOut(
                id=scrap.job_post.PostID,
                title=scrap.job_post.Title,
                company_name=scrap.job_post.CompanyName,
            )

        if scrap.PostType == "Bootcamp" and scrap.bootcamp_post:
            bootcamp_post = BootcampPostOut(
                id=scrap.bootcamp_post.BootcampID,
                title=scrap.bootcamp_post.Title,
                institute_name=scrap.bootcamp_post.InstituteName,
            )

        result.append(
            UserScrapGet(
                post_type=scrap.PostType,
                job_post_id=scrap.JobPostID,
                bootcamp_post_id=scrap.BootcampPostID,
                job_post=job_post,
                bootcamp_post=bootcamp_post,
            )
        )
    return result


@router.post("/me/scraps", response_model=Dict[str, Any])
def create_my_scrap(data: UserScrapPost, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """현재 로그인한 사용자의 스크랩 추가 (Job 또는 Bootcamp)."""
    try:
        current_count = db.query(models.UserScrap).filter(
            models.UserScrap.UserID == current_user.UserID
        ).count()

        if data.post_type.value.lower() == 'job':
            existing = db.query(models.UserScrap).filter(
                models.UserScrap.UserID == current_user.UserID,
                models.UserScrap.PostType == 'Job',
                models.UserScrap.JobPostID == data.target_id,
            ).first()
            if existing:
                return {"status": "ok", "message": "already_scrapped"}

            scrap = models.UserScrap(
                UserID=current_user.UserID,
                PostType='Job',
                JobPostID=data.target_id,
            )
        else:
            existing = db.query(models.UserScrap).filter(
                models.UserScrap.UserID == current_user.UserID,
                models.UserScrap.PostType == 'Bootcamp',
                models.UserScrap.BootcampPostID == data.target_id,
            ).first()
            if existing:
                return {"status": "ok", "message": "already_scrapped"}

            scrap = models.UserScrap(
                UserID=current_user.UserID,
                PostType='Bootcamp',
                BootcampPostID=data.target_id,
            )

        db.add(scrap)
        db.commit()
        db.refresh(scrap)
        return {"status": "ok", "scrap_id": scrap.ScrapID}
    except Exception as e:
        db.rollback()
        logger.exception("스크랩 생성 실패")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/me/scraps", response_model=Dict[str, Any])
def delete_my_scrap(data: UserScrapPost, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    """현재 로그인한 사용자의 스크랩 삭제"""
    try:
        if data.post_type.value.lower() == 'job':
            scrap = db.query(models.UserScrap).filter(
                models.UserScrap.UserID == current_user.UserID,
                models.UserScrap.PostType == 'Job',
                models.UserScrap.JobPostID == data.target_id,
            ).first()
        else:
            scrap = db.query(models.UserScrap).filter(
                models.UserScrap.UserID == current_user.UserID,
                models.UserScrap.PostType == 'Bootcamp',
                models.UserScrap.BootcampPostID == data.target_id,
            ).first()

        if not scrap:
            return {"status": "ok", "message": "not_found"}

        db.delete(scrap)
        db.commit()
        return {"status": "ok", "message": "deleted"}
    except Exception as e:
        db.rollback()
        logger.exception("스크랩 삭제 실패")
        raise HTTPException(status_code=500, detail=str(e))


# @router.get("/{user_id}/notifications", response_model=List[UserNotifications])
# def read_notifications(user_id: int, db: Session = Depends(get_db)):
#     notifications = get_user_notifications(db, user_id)
#     if not notifications:
#         raise HTTPException(404, "알림 항목을 찾을 수 없습니다.")
    
#     return [
#         UserNotifications(
#             notification_type=n.NotificationType,
#             isenabled=n.IsEnabled,
#             notificationtime=n.NotificationTime,
#         )
#         for n in notifications
#     ]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)