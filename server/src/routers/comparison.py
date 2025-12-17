from datetime import date, datetime
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src import models, schemas
from src.database import get_db

router = APIRouter(prefix="/comparison", tags=["비교함 기능"])

logger = logging.getLogger(__name__)

# 플랫폼 이름을 안전하게 Provider_job enum 값으로 매핑
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
    if "want" in key:
        return "wanted"
    if "remember" in key or "rem" in key:
        return "remember"
    return "remember"


def _to_dt(val):
    if val is None:
        return None
    if isinstance(val, datetime):
        return val
    if isinstance(val, date):
        return datetime.combine(val, datetime.min.time())
    return val


def job_to_dict(job: models.JobPost):
    platform_name = None
    if hasattr(job, "platform") and job.platform is not None:
        platform_name = job.platform.PlatformName or ""
    provider_val = map_platform_to_provider(platform_name)

    job_category_name = None
    if hasattr(job, "job_category") and job.job_category is not None:
        job_category_name = job.job_category.CategoryName

    return {
        "id": job.PostID,
        "provider": provider_val,
        "title": job.Title,
        "company_name": job.CompanyName,
        "job_category": job_category_name,
        "employment_type": job.EmploymentType,
        "experience_requirement": job.ExperienceRequirement,
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
        "skills": [s.SkillName for s in job.skills] if hasattr(job, "skills") else [],
    }


def bootcamp_to_dict(b: models.BootcampPost):
    return {
        "id": b.BootcampID,
        "title": b.Title,
        "institute_name": b.InstituteName,
        "job_category_id": b.JobCategoryID,
        "category_name": b.job_category.CategoryName if b.job_category else None,
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


@router.get("/jobs/{post_id}", response_model=schemas.JobPost)
def get_job(post_id: int, db: Session = Depends(get_db)):
    try:
        job = db.query(models.JobPost).filter(models.JobPost.PostID == post_id).first()
        if not job:
            raise HTTPException(status_code=404, detail="Job post not found")
        return job_to_dict(job)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get job %s: %s", post_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error")


@router.post("/jobs", response_model=List[schemas.JobPost])
def compare_jobs(ids: List[int], db: Session = Depends(get_db)):
    if len(ids) > 3:
        raise HTTPException(status_code=400, detail="Maximum of 3 job posts can be compared")
    try:
        jobs = db.query(models.JobPost).filter(models.JobPost.PostID.in_(ids)).all()
        return [job_to_dict(j) for j in jobs]
    except Exception as e:
        logger.exception("Failed to compare jobs %s: %s", ids, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error")


@router.get("/bootcamps/{bootcamp_id}", response_model=schemas.BootcampPost)
def get_bootcamp(bootcamp_id: int, db: Session = Depends(get_db)):
    try:
        b = db.query(models.BootcampPost).filter(models.BootcampPost.BootcampID == bootcamp_id).first()
        if not b:
            raise HTTPException(status_code=404, detail="Bootcamp not found")
        return bootcamp_to_dict(b)
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Failed to get bootcamp %s: %s", bootcamp_id, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error")


@router.post("/bootcamps", response_model=List[schemas.BootcampPost])
def compare_bootcamps(ids: List[int], db: Session = Depends(get_db)):
    if len(ids) > 3:
        raise HTTPException(status_code=400, detail="Maximum of 3 bootcamps can be compared")
    try:
        posts = db.query(models.BootcampPost).filter(models.BootcampPost.BootcampID.in_(ids)).all()
        return [bootcamp_to_dict(b) for b in posts]
    except Exception as e:
        logger.exception("Failed to compare bootcamps %s: %s", ids, e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal Error")
