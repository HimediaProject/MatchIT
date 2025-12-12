from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import JobCategory

router = APIRouter(prefix="/jobcategories", tags=["jobcategories"])


@router.get("/")
def get_categories(db: Session = Depends(get_db)):
    categories = db.query(JobCategory).all()
    return [
        {
            "CategoryID": c.CategoryID,
            "CategoryName": c.CategoryName,
        }
        for c in categories
    ]
