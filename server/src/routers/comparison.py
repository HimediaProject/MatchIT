from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from src.database import get_db
from src import models
from src import schemas

router = APIRouter(prefix="/comparison", tags=["비교함 기능"])


def job_to_dict(job: models.JobPost):
    return {
        "PostID": job.PostID,
        "PlatformID": job.PlatformID,
        "Title": job.Title,
        "CompanyName": job.CompanyName,
        "JobCategoryID": job.JobCategoryID,
        "EmploymentType": job.EmploymentType,
        "ExperienceRequirement": job.ExperienceRequirement,
        "EducationRequirement": job.EducationRequirement,
        "Location": job.Location,
        "MainTasks": job.MainTasks,
        "Qualifications": job.Qualifications,
        "Preferences": job.Preferences,
        "Benefits": job.Benefits,
        "Process": job.Process,
        "Salary": job.Salary,
        "PostedDate": job.PostedDate,
        "CloseDate": job.CloseDate,
        "ViewCount": job.ViewCount,
        "Url": job.Url,
        "IsActive": job.IsActive,
        "CreatedAt": job.CreatedAt,
        "UpdatedAt": job.UpdatedAt,
        "Skills": [s.SkillName for s in job.skills] if hasattr(job, 'skills') else [],
    }


def bootcamp_to_dict(b: models.BootcampPost):
    return {
        "BootcampID": b.BootcampID,
        "Title": b.Title,
        "InstituteName": b.InstituteName,
        "JobCategoryID": b.JobCategoryID,
        "Location": b.Location,
        "OnlineOffline": b.OnlineOffline,
        "CostSupportType": b.CostSupportType,
        "EducationContent": b.EducationContent,
        "Qualification": b.Qualification,
        "Benefits": b.Benefits,
        "StartDate": b.StartDate,
        "RegistrationDate": b.RegistrationDate,
        "CloseDate": b.CloseDate,
        "DetailUrl": b.DetailUrl,
        "ViewCount": b.ViewCount,
        "CreatedAt": b.CreatedAt,
        "UpdatedAt": b.UpdatedAt,
    }


@router.get('/jobs', response_model=List[schemas.JobPost])
def list_jobs(limit: int = 50, db: Session = Depends(get_db)):
    jobs = db.query(models.JobPost).filter(models.JobPost.IsActive == True).limit(limit).all()
    return [job_to_dict(j) for j in jobs]


@router.get('/jobs/{post_id}', response_model=schemas.JobPost)
def get_job(post_id: int, db: Session = Depends(get_db)):
    job = db.query(models.JobPost).filter(models.JobPost.PostID == post_id).first()
    if not job:
        raise HTTPException(status_code=404, detail='Job post not found')
    return job_to_dict(job)


@router.post('/jobs', response_model=List[schemas.JobPost])
def compare_jobs(ids: List[int], db: Session = Depends(get_db)):
    if len(ids) > 3:
        raise HTTPException(status_code=400, detail='Maximum of 3 job posts can be compared')
    jobs = db.query(models.JobPost).filter(models.JobPost.PostID.in_(ids)).all()
    return [job_to_dict(j) for j in jobs]


@router.get('/bootcamps', response_model=List[schemas.BootcampPost])
def list_bootcamps(limit: int = 50, db: Session = Depends(get_db)):
    posts = db.query(models.BootcampPost).limit(limit).all()
    return [bootcamp_to_dict(b) for b in posts]


@router.get('/bootcamps/{bootcamp_id}', response_model=schemas.BootcampPost)
def get_bootcamp(bootcamp_id: int, db: Session = Depends(get_db)):
    b = db.query(models.BootcampPost).filter(models.BootcampPost.BootcampID == bootcamp_id).first()
    if not b:
        raise HTTPException(status_code=404, detail='Bootcamp not found')
    return bootcamp_to_dict(b)

@router.post('/bootcamps', response_model=List[schemas.BootcampPost])
def compare_bootcamps(ids: List[int], db: Session = Depends(get_db)):
    if len(ids) > 3:
        raise HTTPException(status_code=400, detail='Maximum of 3 bootcamps can be compared')
    posts = db.query(models.BootcampPost).filter(models.BootcampPost.BootcampID.in_(ids)).all()
    return [bootcamp_to_dict(b) for b in posts]
