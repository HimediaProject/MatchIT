from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_
from src.database import get_db
from src.models import BootcampPost as BootcampPo, JobCategory, Skill
from src.schemas import BootcampCreate, BootcampUpdate, \
                            BootcampResponse, PaginatedBootcampResponse, \
                            BootcampDetailResponse
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel

router = APIRouter(prefix = '/bootcamps')

@router.post('/', response_model = BootcampResponse, status_code = 201)
def create_bootcamp(
    bootcamp: BootcampCreate,
    db: Session = Depends(get_db)
):
    """
    부트캠프 게시글 생성
    """
    # JobCategory 존재 확인
    # 이게 None...
    category = db.query(JobCategory).filter(
        JobCategory.CategoryID == bootcamp.JobCategoryID
    ).first()
    # print(f'🛠️🛠️ JobCategory: {category}')
    if not category:
        raise HTTPException(status_code = 404, detail = "JobCategory not found")

    # 새 부트캠프 게시글 생성
    db_bootcamp = BootcampPo(**bootcamp.model_dump())
    db.add(db_bootcamp)
    db.commit()
    db.refresh(db_bootcamp)

    return db_bootcamp


@router.get('/', response_model = PaginatedBootcampResponse)
async def get_bootcamp_list(
    page: int = Query(1, ge = 1, description = "페이지 번호"),
    size: int = Query(10, ge = 1, le = 100, description = "페이지 당 항목 수"),
    keyword: Optional[str] = Query(None, description = "검색 키워드 (제목, 기관명)"),
    category_id: Optional[int] = Query(None, description = "직무 카테고리 ID"),
    category_names: List[str] = Query(None, description = "직무 카테고리 이름 필터"),
    online_offline: List[str] = Query(None, description = "온라인/오프라인 필터"),
    cost_support_type: List[str] = Query(None, description = "비용 지원 유형"),
    location: Optional[str] = Query(None, description = "지역 필터"),
    show_expired: bool = Query(False, description = "마감 공고 포함 여부 (False: 진행 중만, True: 모두)"),
    db: Session = Depends(get_db)
):
    """
    부트캠프 목록 조회 (페이지네이션, 필터링, 검색)

    Args:
        page: 페이지 번호 (1부터 시작)
        size: 페이지당 항목 수 (1~100)
        keyword: 제목, 기관명, 교육 내용에서 검색
        category_id: 직무 카테고리 필터
        online_offline: 온라인/오프라인 필터
        cost_support_type: 비용 지원 유형 필터
        location: 지역 필터
        show_expired: 마감 공고 포함 여부
            - False (기본): 마감일이 지나지 않은 공고만 (진행 중 + 상시 모집)
            - True: 모든 공고 (마감된 공고 포함)

    Returns:
        PaginatedBootcampResponse: 페이지네이션된 부트캠프 목록

    Example:
        GET /bootcamps?page=1&size=10&show_expired=false
        → 진행 중인 공고 10개

        GET /bootcamps?page=1&size=10&show_expired=true
        → 모든 공고 10개 (마감된 것 포함)
    """
    # Jobcategory join
    # query = db.query(BootcampPo).join(
    #     JobCategory, BootcampPo.JobCategoryID == JobCategory.CategoryID
    # )

    # query = db.query(BootcampPo).options(
    #     joinedload(BootcampPo.job_category)
    # )

    query = (
        db.query(BootcampPo)
        ).join(
            BootcampPo.job_category
        )
    # print(f'🛠️🛠️ query: {query.all()}')
    # print(f'🛠️🛠️ JobCategory: {JobCategory}')

    # 필터 적용
    filters = []

    if keyword:
        keyword_filter = or_(
            BootcampPo.Title.ilike(f"%{keyword}%"),
            BootcampPo.InstituteName.ilike(f"%{keyword}%"),
            BootcampPo.EducationContent.ilike(f"%{keyword}%")
        )
        filters.append(keyword_filter)

    if category_id:
        filters.append(BootcampPo.JobCategoryID == category_id)

    if category_names:
        filters.append(JobCategory.CategoryName.in_(category_names))

    if online_offline:
        filters.append(BootcampPo.OnlineOffline.in_(online_offline))

    if cost_support_type:
        filters.append(BootcampPo.CostSupportType.in_(cost_support_type))

    if location:
        filters.append(BootcampPo.Location.ilike(f"%{location}%"))

    # 🔹 마감일 필터링 로직
    # show_expired가 False(기본값)일 때는 마감되지 않은 공고만 표시
    # show_expired가 True일 때는 모든 공고 표시 (마감된 공고 포함)
    if not show_expired:
        today = date.today()  # 오늘 날짜 (시간 제외)

        # 마감일이 오늘 이후이거나 마감일이 없는 공고만 필터링
        # CloseDate >= today: 마감일이 오늘 포함 이후 (진행 중)
        # CloseDate is None: 마감일이 없는 공고 (상시 모집)
        expired_filter = or_(
            BootcampPo.CloseDate >= today,
            BootcampPo.CloseDate.is_(None)
        )
        filters.append(expired_filter)

    if filters:
        query = query.filter(and_(*filters))
        # print(f'🛠️🛠️ filtered_query: {query}')

    # 전체 개수 조회
    total = query.count()

    # 페이지네이션 적용
    offset = (page - 1) * size
    items = query.order_by(BootcampPo.CreatedAt.desc()).offset(offset).limit(size).all()

    # CategoryName 추가
    result_items = []
    for item in items:       # Tuple 언패킹
        item_dict = {
            "BootcampID": item.BootcampID,
            "Title": item.Title,
            "InstituteName": item.InstituteName,
            "JobCategoryID": item.JobCategoryID,
            "CategoryName": item.job_category.CategoryName,      # 추가된 값

            "Location": item.Location,
            "OnlineOffline": item.OnlineOffline,
            "CostSupportType": item.CostSupportType,
            "EducationContent": item.EducationContent,
            "Qualification": item.Qualification,
            "Benefits": item.Benefits,
            "StartDate": item.StartDate,
            "RegistrationDate": item.RegistrationDate,
            "CloseDate": item.CloseDate,
            "DetailUrl": item.DetailUrl,
            "ViewCount": item.ViewCount,
            "CreatedAt": item.CreatedAt,
            "UpdatedAt": item.UpdatedAt,
        }
        result_items.append(item_dict)

    return {
        "total": total,
        "page": page,
        "size": size,
        "items": result_items
    }


@router.get('/filter-options')
async def get_filter_options(db: Session = Depends(get_db)):
    """
    필터 옵션 목록 조회 (체크박스용)

    Returns:
        dict: 카테고리, 수강 형태, 비용 지원 유형의 고유 목록

    Example:
        GET /bootcamps/filter-options
        → {
            "categories": ["빅데이터", "인공지능", ...],
            "modes": ["온라인", "오프라인", "혼합형"],
            "fundings": ["국비지원", "본인부담"]
          }
    """
    # JobCategory와 조인하여 모든 부트캠프 조회
    query = db.query(BootcampPo).join(BootcampPo.job_category)
    items = query.all()

    # 중복 제거하여 고유한 값만 추출
    categories = list(set([item.job_category.CategoryName for item in items]))
    modes = list(set([item.OnlineOffline for item in items]))
    fundings = list(set([item.CostSupportType for item in items]))

    return {
        "categories": sorted(categories),  # 알파벳 순 정렬
        "modes": modes,
        "fundings": fundings
    }


@router.get('/{bootcamp_id}', response_model = BootcampDetailResponse)
def get_bootcamp_detail(
    bootcamp_id: int,
    db: Session = Depends(get_db)
):
    """
    부트캠프 상세 조회 (조회수 증가)
    """
    bootcamp = db.query(BootcampPo).filter(
        BootcampPo.BootcampID == bootcamp_id
    ).first()

    if not bootcamp:
        raise HTTPException(status_code = 404, detail = "Bootcamp not found")

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
    bootcamp = db.query(BootcampPo).filter(
        BootcampPo.BootcampID == bootcamp_id
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
    update_data = bootcamp_update.model_dump(exclude_unset = True)
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
    bootcamp = db.query(BootcampPo).filter(
        BootcampPo.BootcampID == bootcamp_id
    ).first()

    if not bootcamp:
        raise HTTPException(status_code = 404, detail = "Bootcamp not found")

    db.delete(bootcamp)
    db.commit()

    return None
