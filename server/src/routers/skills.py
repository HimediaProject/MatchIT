from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
import logging

from src.database import get_db
from src import models

router = APIRouter(prefix="/skills", tags=["skills"])

logger = logging.getLogger(__name__)


@router.get("/all", summary="Get all skills")
def get_all_skills(
    db: Session = Depends(get_db),
):
    try:
        skills = db.query(models.Skill).all()
        results = [s.SkillName for s in skills]
        return JSONResponse(content={"skills": results}, media_type="application/json; charset=utf-8")
    except Exception as e:
        logger.exception("get_all_skills failed: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/", summary="Skill autocomplete")
def autocomplete_skills(
    query: str = Query(..., min_length=1, description="검색어"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    try:
        q = db.query(models.Skill).filter(models.Skill.SkillName.ilike(f"{query}%"))
        results = [s.SkillName for s in q.limit(limit).all()]
        return {"skills": results}
    except Exception as e:
        logger.exception("autocomplete_skills failed: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
