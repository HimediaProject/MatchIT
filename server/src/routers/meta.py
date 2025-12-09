from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import logging

from src.database import get_db
from src import models

router = APIRouter(prefix="", tags=["meta"])

logger = logging.getLogger(__name__)


@router.get("/careerlevels", summary="Get career levels")
def get_career_levels(db: Session = Depends(get_db)):
    try:
        items = db.query(models.CareerLevel).order_by(models.CareerLevel.CareerLevelID).all()
        results = []
        for c in items:
            # Normalize field names for frontend
            results.append({
                "id": c.CareerLevelID,
                "name": c.CareerName,
            })
        return {"careerlevels": results} if results else []
    except Exception as e:
        logger.exception("get_career_levels failed: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/experienceranges", summary="Get experience ranges")
def get_experience_ranges(db: Session = Depends(get_db)):
    try:
        items = db.query(models.ExperienceRange).order_by(models.ExperienceRange.RangeID).all()
        results = []
        for r in items:
            results.append({
                "id": r.RangeID,
                "name": r.RangeName,
                "min_years": r.MinYears,
                "max_years": r.MaxYears,
            })
        return {"experienceranges": results} if results else []
    except Exception as e:
        logger.exception("get_experience_ranges failed: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
