import logging
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.database import get_db
from src import models

router = APIRouter(prefix="/skills", tags=["skills"])

logger = logging.getLogger(__name__)

# IT skill allowlist for frontend consumption
ALLOWED_IT_SKILLS = {
    "Python", "JavaScript", "TypeScript", "Java",
    "SQL", "MySQL", "PostgreSQL", "MongoDB",
    "React", "Next.js", "Vue", "Angular",
    "Node.js", "Express", "Django", "Spring", "Flask",
    "AWS", "Azure", "GCP",
    "Docker", "Kubernetes",
    "TensorFlow", "PyTorch", "Deep_Learning", "Machine_Learning",
    "데이터 파이프라인", "Data Engineering", "Data Pipeline",
}


@router.get("/all", summary="Get all skills")
def get_all_skills(db: Session = Depends(get_db)):
    try:
        skills = db.query(models.Skill).all()
        results = [s.SkillName for s in skills if s.SkillName in ALLOWED_IT_SKILLS]
        return {"skills": results}
    except Exception as e:
        logger.exception("get_all_skills failed: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")


@router.get("/", summary="Skill autocomplete")
def autocomplete_skills(
    query: str | None = Query(None, min_length=1, description="Search term"),
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    try:
        q = db.query(models.Skill)
        if query:
            q = q.filter(models.Skill.SkillName.ilike(f"{query}%"))
        raw = q.limit(limit * 2).all()  # overfetch then filter by allowlist
        results = [s.SkillName for s in raw if s.SkillName in ALLOWED_IT_SKILLS][:limit]
        return {"skills": results}
    except Exception as e:
        logger.exception("autocomplete_skills failed: %s", e)
        raise HTTPException(status_code=500, detail="Internal Server Error")
