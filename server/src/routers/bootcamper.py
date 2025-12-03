from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from src.database import get_db
from src.models import BootcampPost, JobCategory, Skill
from utils.schemas import BootcampCreate, BootcampUpdate, \
                            BootcampResponse, PaginatedBootcampResponse
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

router = APIRouter(prefix = '/bootcamps')


# # Pydantic schemas for request/response
# class BootcampCreate(BaseModel):
#     Title: str
#     InstituteName: str
#     JobCategoryID: int
#     Location: Optional[str] = None
#     OnlineOffline: str = "온라인"
#     CostSupportType: str = "본인부담"
#     EducationContent: Optional[str] = None
#     Qualification: Optional[str] = None
#     Benefits: Optional[str] = None
#     StartDate: Optional[date] = None
#     RegistrationDate: Optional[date] = None
#     CloseDate: Optional[date] = None
#     DetailUrl: Optional[str] = None


# class BootcampUpdate(BaseModel):
#     Title: Optional[str] = None
#     InstituteName: Optional[str] = None
#     JobCategoryID: Optional[int] = None
#     Location: Optional[str] = None
#     OnlineOffline: Optional[str] = None
#     CostSupportType: Optional[str] = None
#     EducationContent: Optional[str] = None
#     Qualification: Optional[str] = None
#     Benefits: Optional[str] = None
#     StartDate: Optional[date] = None
#     RegistrationDate: Optional[date] = None
#     CloseDate: Optional[date] = None
#     DetailUrl: Optional[str] = None
#     ViewCount: Optional[int] = None


# class BootcampResponse(BaseModel):
#     BootcampID: int
#     Title: str
#     InstituteName: str
#     JobCategoryID: int
#     Location: Optional[str]
#     OnlineOffline: str
#     CostSupportType: str
#     EducationContent: Optional[str]
#     Qualification: Optional[str]
#     Benefits: Optional[str]
#     StartDate: Optional[date]
#     RegistrationDate: Optional[date]
#     CloseDate: Optional[date]
#     DetailUrl: Optional[str]
#     ViewCount: int
#     CreatedAt: datetime
#     UpdatedAt: datetime

#     class Config:
#         from_attributes = True


# class PaginatedBootcampResponse(BaseModel):
#     total: int
#     page: int
#     size: int
#     items: List[BootcampResponse]


@router.post('/', response_model = BootcampResponse, status_code = 201)
def create_bootcamp(
    bootcamp: BootcampCreate,
    db: Session = Depends(get_db)
):
    """
    부트캠프 게시글 생성
    """
    # JobCategory 존재 확인
    category = db.query(JobCategory).filter(
        JobCategory.CategoryID == bootcamp.JobCategoryID
    ).first()
    if not category:
        raise HTTPException(status_code = 404, detail = "JobCategory not found")

    # 새 부트캠프 게시글 생성
    db_bootcamp = BootcampPost(**bootcamp.model_dump())
    db.add(db_bootcamp)
    db.commit()
    db.refresh(db_bootcamp)

    return db_bootcamp


@router.get('/', response_model = PaginatedBootcampResponse)
def get_bootcamp_list(
    page: int = Query(1, ge = 1, description = "페이지 번호"),
    size: int = Query(10, ge = 1, le = 100, description = "페이지 당 항목 수"),
    keyword: Optional[str] = Query(None, description = "검색 키워드 (제목, 기관명)"),
    category_id: Optional[int] = Query(None, description = "직무 카테고리 ID"),
    online_offline: Optional[str] = Query(None, description = "온라인/오프라인 필터"),
    cost_support_type: Optional[str] = Query(None, description = "비용 지원 유형"),
    location: Optional[str] = Query(None, description = "지역 필터"),
    db: Session = Depends(get_db)
):
    """
    부트캠프 목록 조회 (페이지네이션, 필터링, 검색)
    """
    # 기본 쿼리
    query = db.query(BootcampPost)

    # 필터 적용
    filters = []

    if keyword:
        keyword_filter = or_(
            BootcampPost.Title.ilike(f"%{keyword}%"),
            BootcampPost.InstituteName.ilike(f"%{keyword}%"),
            BootcampPost.EducationContent.ilike(f"%{keyword}%")
        )
        filters.append(keyword_filter)

    if category_id:
        filters.append(BootcampPost.JobCategoryID == category_id)

    if online_offline:
        filters.append(BootcampPost.OnlineOffline == online_offline)

    if cost_support_type:
        filters.append(BootcampPost.CostSupportType == cost_support_type)

    if location:
        filters.append(BootcampPost.Location.ilike(f"%{location}%"))

    if filters:
        query = query.filter(and_(*filters))

    # 전체 개수 조회
    total = query.count()

    # 페이지네이션 적용
    offset = (page - 1) * size
    items = query.order_by(BootcampPost.CreatedAt.desc()).offset(offset).limit(size).all()

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": items
    }


@router.get('/{bootcamp_id}', response_model = BootcampResponse)
def get_bootcamp_detail(
    bootcamp_id: int,
    db: Session = Depends(get_db)
):
    """
    부트캠프 상세 조회 (조회수 증가)
    """
    bootcamp = db.query(BootcampPost).filter(
        BootcampPost.BootcampID == bootcamp_id
    ).first()

    if not bootcamp:
        raise HTTPException(status_code=404, detail = "Bootcamp not found")

    # 조회수 증가
    bootcamp.ViewCount += 1
    db.commit()
    db.refresh(bootcamp)

    return bootcamp


@router.put('/{bootcamp_id}', response_model = BootcampResponse)
def update_bootcamp(
    bootcamp_id: int,
    bootcamp_update: BootcampUpdate,
    db: Session = Depends(get_db)
):
    """
    부트캠프 게시글 수정
    """
    # 기존 부트캠프 조회
    bootcamp = db.query(BootcampPost).filter(
        BootcampPost.BootcampID == bootcamp_id
    ).first()

    if not bootcamp:
        raise HTTPException(status_code = 404, detail = "Bootcamp not found")

    # JobCategory 변경 시 존재 확인
    if bootcamp_update.JobCategoryID is not None:
        category = db.query(JobCategory).filter(
            JobCategory.CategoryID == bootcamp_update.JobCategoryID
        ).first()
        if not category:
            raise HTTPException(status_code = 404, detail = "JobCategory not found")

    # 업데이트할 필드만 수정
    update_data = bootcamp_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(bootcamp, field, value)

    db.commit()
    db.refresh(bootcamp)

    return bootcamp


@router.delete('/{bootcamp_id}', status_code=204)
def delete_bootcamp(
    bootcamp_id: int,
    db: Session = Depends(get_db)
):
    """
    부트캠프 게시글 삭제
    """
    bootcamp = db.query(BootcampPost).filter(
        BootcampPost.BootcampID == bootcamp_id
    ).first()

    if not bootcamp:
        raise HTTPException(status_code = 404, detail = "Bootcamp not found")

    db.delete(bootcamp)
    db.commit()

    return None
