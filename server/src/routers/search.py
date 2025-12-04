from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session
import logging

from src.database import get_db
from src import models
from src.routers.comparison import job_to_dict, bootcamp_to_dict

router = APIRouter(prefix="/search", tags=["검색 기능"])

logger = logging.getLogger(__name__)


@router.get('/')
def search(
	keyword: str = Query(..., min_length=1, description="검색 키워드"),
	limit: int = Query(20, ge=1, le=100, description="최대 반환 개수"),
	db: Session = Depends(get_db),
):
	"""
	키워드로 채용공고(JobPost)와 부트캠프(BootcampPost)를 각각 검색하여
	분리된 리스트로 반환합니다.
	"""
	try:
		jobs_q = db.query(models.JobPost).filter(
			or_(
				models.JobPost.Title.ilike(f"%{keyword}%"),
				models.JobPost.CompanyName.ilike(f"%{keyword}%"),
				models.JobPost.MainTasks.ilike(f"%{keyword}%"),
				models.JobPost.Qualifications.ilike(f"%{keyword}%"),
				models.JobPost.Preferences.ilike(f"%{keyword}%"),
				models.JobPost.Benefits.ilike(f"%{keyword}%"),
			)
		).limit(limit)

		bootcamps_q = db.query(models.BootcampPost).filter(
			or_(
				models.BootcampPost.Title.ilike(f"%{keyword}%"),
				models.BootcampPost.InstituteName.ilike(f"%{keyword}%"),
				models.BootcampPost.EducationContent.ilike(f"%{keyword}%"),
				models.BootcampPost.Qualification.ilike(f"%{keyword}%"),
				models.BootcampPost.Benefits.ilike(f"%{keyword}%"),
			)
		).limit(limit)

		jobs = [job_to_dict(j) for j in jobs_q.all()]
		bootcamps = [bootcamp_to_dict(b) for b in bootcamps_q.all()]

		return {"jobs": jobs, "bootcamps": bootcamps}
	except Exception as e:
		logger.exception("Search failed: %s", e)
		raise HTTPException(status_code=500, detail="Internal Server Error")