from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, date
import logging
from fastapi import status
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src import models
from src import schemas

router = APIRouter(prefix="/comparison", tags=["비교함 기능"])

logger = logging.getLogger(__name__)

# 안전한 provider 매핑: 플랫폼 이름 -> Provider_job enum 값(문자열)
# 알려진 플랫폼 이름은 소문자형으로 매핑한다. 알 수 없는 플랫폼은 'remember'를 기본으로 사용.
PROVIDER_MAP = {
    "wanted": "wanted",
    "want": "wanted",
    "원티드": "wanted",
    "remember": "remember",
    "rem": "remember",
    "saramin": "remember",
    "jobkorea": "remember",
}

def map_platform_to_provider(platform_name: str) -> str:
    if not platform_name:
        return "remember"
    key = platform_name.strip().lower()
    provider = PROVIDER_MAP.get(key)
    if provider:
        return provider
    # try fuzzy matching: 'wanted' substring
    if 'want' in key:
        return 'wanted'
    if 'remember' in key or 'rem' in key:
        return 'remember'
    # default fallback to 'remember' to satisfy Provider_job enum
    return 'remember'


def job_to_dict(job: models.JobPost):
    # Map DB column/relationship names (PascalCase) to API schema names (snake_case)
    platform_name = None
    if hasattr(job, 'platform') and job.platform is not None:
        platform_name = job.platform.PlatformName or ''
    provider_val = map_platform_to_provider(platform_name)

    job_category_name = None
    if hasattr(job, 'job_category') and job.job_category is not None:
        job_category_name = job.job_category.CategoryName

    def _to_dt(val):
        if val is None:
            return None
        if isinstance(val, datetime):
            return val
        if isinstance(val, date):
            return datetime.combine(val, datetime.min.time())
        return val

    return {
        "provider": provider_val,
        "title": job.Title,
        "company_name": job.CompanyName,
        "job_category": job_category_name,
        "employment_type": job.EmploymentType,
        "experience_requirement": job.ExperienceRequirement,
        # normalize to snake_case and match schema: 'education_requirement'
        "education_requirement": job.EducationRequirement,
        "location": job.Location,
        "main_tasks": job.MainTasks,
        "qualifications": job.Qualifications,
        "preferences": job.Preferences,
        "benefits": job.Benefits,
        "process": job.Process,
        "salary": job.Salary,
        "posted_date": _to_dt(job.PostedDate),
        "close_date": _to_dt(job.CloseDate),
        "url": job.Url,
        "is_active": job.IsActive,
        "created_at": _to_dt(job.CreatedAt),
        "updated_at": _to_dt(job.UpdatedAt),
        "skills": [s.SkillName for s in job.skills] if hasattr(job, 'skills') else [],
    }


def bootcamp_to_dict(b: models.BootcampPost):
    # Map DB columns and ensure API response matches schemas.BootcampPost
    def _to_dt(val):
        if val is None:
            return None
        if isinstance(val, datetime):
            return val
        if isinstance(val, date):
            return datetime.combine(val, datetime.min.time())
        return val

    return {
        "title": b.Title,
        "institute_name": b.InstituteName,
        "job_category_id": b.JobCategoryID,
        "location": b.Location,
        "online_offline": b.OnlineOffline,
        "cost_support_type": b.CostSupportType,
        "education_content": b.EducationContent,
        "qualification": b.Qualification,
        "benefits": b.Benefits,
        "start_date": _to_dt(b.StartDate),
        "registration_date": _to_dt(b.RegistrationDate),
        "close_date": _to_dt(b.CloseDate),
        "detail_url": b.DetailUrl,
    }

# JobPosts 비교 관련 엔드포인트
@router.get('/jobs/{post_id}', response_model=schemas.JobPost)
def get_job(post_id: int, db: Session = Depends(get_db)):
    try:
        job = db.query(models.JobPost).filter(models.JobPost.PostID == post_id).first()
        if not job:
            raise HTTPException(status_code=404, detail='Job post not found')
        return job_to_dict(job)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get job %s: %s", post_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error")

@router.post('/jobs', response_model=List[schemas.JobPost])
def compare_jobs(ids: List[int], db: Session = Depends(get_db)):
    if len(ids) > 3:
        raise HTTPException(status_code=400, detail='Maximum of 3 job posts can be compared')
    try:
        jobs = db.query(models.JobPost).filter(models.JobPost.PostID.in_(ids)).all()
        return [job_to_dict(j) for j in jobs]
    except Exception as e:
        logger.exception("Failed to compare jobs %s: %s", ids, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error")

# BootcampPosts 비교 관련 엔드포인트
@router.get('/bootcamps/{bootcamp_id}', response_model=schemas.BootcampPost)
def get_bootcamp(bootcamp_id: int, db: Session = Depends(get_db)):
    try:
        b = db.query(models.BootcampPost).filter(models.BootcampPost.BootcampID == bootcamp_id).first()
        if not b:
            raise HTTPException(status_code=404, detail='Bootcamp not found')
        return bootcamp_to_dict(b)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get bootcamp %s: %s", bootcamp_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error")

@router.post('/bootcamps', response_model=List[schemas.BootcampPost])
def compare_bootcamps(ids: List[int], db: Session = Depends(get_db)):
    if len(ids) > 3:
        raise HTTPException(status_code=400, detail='Maximum of 3 bootcamps can be compared')
    try:
        posts = db.query(models.BootcampPost).filter(models.BootcampPost.BootcampID.in_(ids)).all()
        return [bootcamp_to_dict(b) for b in posts]
    except Exception as e:
        logger.exception("Failed to compare bootcamps %s: %s", ids, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error")
