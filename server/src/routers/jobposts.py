from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import Integer, cast, func, or_, select
from sqlalchemy.orm import Session

from src.database import get_db
from src.models import JobCategory, JobPost, Platform, Skill
from src.schemas import JobPostCreate, JobPostResponse, JobPostUpdate, PaginatedJobPostResponse
from sentence_transformers import SentenceTransformer
from ai.ai_models import get_embedding_model

router = APIRouter(prefix="/jobs")


@router.post("/", response_model=JobPostResponse, status_code=201)
def create_job_post(
    job: JobPostCreate,
    db: Session = Depends(get_db),
):
    platform = db.query(Platform).filter(Platform.PlatformID == job.PlatformID).first()
    if not platform:
        raise HTTPException(status_code=404, detail="Platform not found")

    category = db.query(JobCategory).filter(JobCategory.CategoryID == job.JobCategoryID).first()
    if not category:
        raise HTTPException(status_code=404, detail="JobCategory not found")

    job_data = job.model_dump(exclude={"SkillIDs"})
    db_job = JobPost(**job_data)

    db.add(db_job)
    db.commit()
    db.refresh(db_job)

    if job.SkillIDs:
        for skill_id in job.SkillIDs:
            skill_obj = db.query(Skill).filter(Skill.SkillID == skill_id).first()
            if not skill_obj:
                raise HTTPException(status_code=404, detail=f"Skill not found: {skill_id}")
            db_job.skills.append(skill_obj)
        db.commit()
        db.refresh(db_job)

    skills_names = [skill.SkillName for skill in db_job.skills]
    response_data = JobPostResponse(
        PostID=db_job.PostID,
        PlatformID=db_job.PlatformID,
        Title=db_job.Title,
        CompanyName=db_job.CompanyName,
        JobCategoryID=db_job.JobCategoryID,
        EmploymentType=db_job.EmploymentType,
        ExperienceRequirement=db_job.ExperienceRequirement,
        MinExperienceYears=db_job.MinExperienceYears,
        EducationRequirement=db_job.EducationRequirement,
        Location=db_job.Location,
        MainTasks=db_job.MainTasks,
        Qualifications=db_job.Qualifications,
        Preferences=db_job.Preferences,
        Benefits=db_job.Benefits,
        Process=db_job.Process,
        Salary=db_job.Salary,
        PostedDate=db_job.PostedDate,
        CloseDate=db_job.CloseDate,
        ViewCount=db_job.ViewCount,
        Url=db_job.Url,
        IsActive=db_job.IsActive,
        CreatedAt=db_job.CreatedAt,
        UpdatedAt=db_job.UpdatedAt,
        Skills=skills_names,
    )

    return response_data


@router.get("/", response_model=PaginatedJobPostResponse)
def get_job_posts(
    page: int = Query(1, ge=1, description="페이지 번호"),
    size: int = Query(10, ge=1, le=100, description="페이지 당 개수"),
    keyword: Optional[str] = Query(None, description="검색어(제목, 회사명, 스킬 이름)"),
    category_id: Optional[int] = Query(None, description="직무 카테고리 ID"),
    location: Optional[str] = Query(None, description="지역 필터"),
    experience_requirement: Optional[str] = Query(None, description="경력 조건 필터 (신입/경력)"),
    sort: str = Query(
        "created",
        pattern="^(created|deadline|views)$",
        description="정렬 방식 (created: 최신 등록순, deadline: 마감일 오름차순, views: 조회수)",
    ),
    db: Session = Depends(get_db),
):
    query = db.query(JobPost)

    if keyword:
        query = query.outerjoin(JobPost.skills)
        pattern = f"%{keyword}%"
        query = query.filter(
            or_(
                JobPost.Title.ilike(pattern),
                JobPost.CompanyName.ilike(pattern),
                Skill.SkillName.ilike(pattern),
            )
        ).distinct()

    if category_id is not None:
        query = query.filter(JobPost.JobCategoryID == category_id)

    if location:
        query = query.filter(JobPost.Location.ilike(f"%{location}%"))

    if experience_requirement:
        query = query.filter(JobPost.ExperienceRequirement == experience_requirement)

    total = query.count()

    offset = (page - 1) * size

    if sort == "deadline":
        order_clause = JobPost.CloseDate.asc().nulls_last()
    elif sort == "views":
        order_clause = JobPost.ViewCount.desc().nulls_last()
    elif sort == "created":
        order_clause = JobPost.CreatedAt.desc().nulls_last()
    else:
        order_clause = JobPost.CreatedAt.desc().nulls_last()

    jobs = (
        query.order_by(order_clause, JobPost.PostID.desc())
        .offset(offset)
        .limit(size)
        .all()
    )

    items: list[JobPostResponse] = []

    for job_post in jobs:
        skills_names = [skill.SkillName for skill in job_post.skills]
        item = JobPostResponse(
            PostID=job_post.PostID,
            PlatformID=job_post.PlatformID,
            Title=job_post.Title,
            CompanyName=job_post.CompanyName,
            JobCategoryID=job_post.JobCategoryID,
            EmploymentType=job_post.EmploymentType,
            ExperienceRequirement=job_post.ExperienceRequirement,
            MinExperienceYears=job_post.MinExperienceYears,
            EducationRequirement=job_post.EducationRequirement,
            Location=job_post.Location,
            MainTasks=job_post.MainTasks,
            Qualifications=job_post.Qualifications,
            Preferences=job_post.Preferences,
            Benefits=job_post.Benefits,
            Process=job_post.Process,
            Salary=job_post.Salary,
            PostedDate=job_post.PostedDate,
            CloseDate=job_post.CloseDate,
            ViewCount=job_post.ViewCount,
            Url=job_post.Url,
            IsActive=job_post.IsActive,
            CreatedAt=job_post.CreatedAt,
            UpdatedAt=job_post.UpdatedAt,
            Skills=skills_names,
        )
        items.append(item)

    return PaginatedJobPostResponse(
        total=total,
        page=page,
        size=size,
        items=items,
    )


@router.get("/{job_id}", response_model=JobPostResponse)
def get_job_post_detail(
    job_id: int,
    db: Session = Depends(get_db),
):
    job_post = db.query(JobPost).filter(JobPost.PostID == job_id).first()

    if not job_post:
        raise HTTPException(status_code=404, detail="JobPost not found")

    job_post.ViewCount += 1
    job_post.UpdatedAt = datetime.now(job_post.UpdatedAt.tzinfo) if job_post.UpdatedAt else datetime.now(timezone.utc)
    db.commit()
    db.refresh(job_post)

    skills_names = [skill.SkillName for skill in job_post.skills]

    return JobPostResponse(
        PostID=job_post.PostID,
        PlatformID=job_post.PlatformID,
        Title=job_post.Title,
        CompanyName=job_post.CompanyName,
        JobCategoryID=job_post.JobCategoryID,
        EmploymentType=job_post.EmploymentType,
        ExperienceRequirement=job_post.ExperienceRequirement,
        MinExperienceYears=job_post.MinExperienceYears,
        EducationRequirement=job_post.EducationRequirement,
        Location=job_post.Location,
        MainTasks=job_post.MainTasks,
        Qualifications=job_post.Qualifications,
        Preferences=job_post.Preferences,
        Benefits=job_post.Benefits,
        Process=job_post.Process,
        Salary=job_post.Salary,
        PostedDate=job_post.PostedDate,
        CloseDate=job_post.CloseDate,
        ViewCount=job_post.ViewCount,
        Url=job_post.Url,
        IsActive=job_post.IsActive,
        CreatedAt=job_post.CreatedAt,
        UpdatedAt=job_post.UpdatedAt,
        Skills=skills_names,
    )


@router.put("/{job_id}", response_model=JobPostResponse)
def update_job_post(
    job_id: int,
    job_update: JobPostUpdate,
    db: Session = Depends(get_db),
):
    job_post = db.query(JobPost).filter(JobPost.PostID == job_id).first()

    if not job_post:
        raise HTTPException(status_code=404, detail="JobPost not found")

    if job_update.JobCategoryID is not None:
        category = db.query(JobCategory).filter(JobCategory.CategoryID == job_update.JobCategoryID).first()
        if not category:
            raise HTTPException(status_code=404, detail="JobCategory not found")

    if job_update.PlatformID is not None:
        platform = db.query(Platform).filter(Platform.PlatformID == job_update.PlatformID).first()
        if not platform:
            raise HTTPException(status_code=404, detail="Platform not found")

    update_data = job_update.model_dump(exclude_unset=True, exclude={"SkillIDs"})
    for field, value in update_data.items():
        setattr(job_post, field, value)
    if job_update.SkillIDs is not None:
        job_post.skills.clear()
        for skill_id in job_update.SkillIDs:
            skill_obj = db.query(Skill).filter(Skill.SkillID == skill_id).first()
            if not skill_obj:
                raise HTTPException(status_code=404, detail=f"Skill not found: {skill_id}")
            job_post.skills.append(skill_obj)

    job_post.UpdatedAt = datetime.now(job_post.UpdatedAt.tzinfo) if job_post.UpdatedAt else datetime.now(timezone.utc)
    db.commit()
    db.refresh(job_post)

    skills_names = [skill.SkillName for skill in job_post.skills]

    return JobPostResponse(
        PostID=job_post.PostID,
        PlatformID=job_post.PlatformID,
        Title=job_post.Title,
        CompanyName=job_post.CompanyName,
        JobCategoryID=job_post.JobCategoryID,
        EmploymentType=job_post.EmploymentType,
        ExperienceRequirement=job_post.ExperienceRequirement,
        MinExperienceYears=job_post.MinExperienceYears,
        EducationRequirement=job_post.EducationRequirement,
        Location=job_post.Location,
        MainTasks=job_post.MainTasks,
        Qualifications=job_post.Qualifications,
        Preferences=job_post.Preferences,
        Benefits=job_post.Benefits,
        Process=job_post.Process,
        Salary=job_post.Salary,
        PostedDate=job_post.PostedDate,
        CloseDate=job_post.CloseDate,
        ViewCount=job_post.ViewCount,
        Url=job_post.Url,
        IsActive=job_post.IsActive,
        CreatedAt=job_post.CreatedAt,
        UpdatedAt=job_post.UpdatedAt,
        Skills=skills_names,
    )


@router.delete("/{job_id}", status_code=204)
def delete_job_post(
    job_id: int,
    db: Session = Depends(get_db),
):
    job_post = db.query(JobPost).filter(JobPost.PostID == job_id).first()

    if not job_post:
        raise HTTPException(status_code=404, detail="JobPost not found")

    db.delete(job_post)
    db.commit()

    return None

# 전체 채용공고 내용 임베딩 생성 (관리자용)
@router.post("/embeddings")
def update_all_job_posting_embeddings(db: Session = Depends(get_db),
                                      model: SentenceTransformer = Depends(get_embedding_model)):
    # 채용공고 내용만 있고 임베딩 벡터가 없을 때 임베딩 벡터 컬럼을 업데이트하는 api
    
    # 1. jobposting에 있는 content 컬럼 내용 가져오기
    # 시나리오1. 채용공고 100개를 가지고 와서 이미 벡터화 데이터를 업데이트 해두었다 -> 이미 벡터가 있으면 제와
    # 시나리오2. 추가로 채용공고 100개를 더 추가했지만 벡터화 데이터를 업데이트 하지 못했다
    jobposting = db.query(JobPost).filter(JobPost.Embedding.is_(None)).all()  # 벡터화 데이터가 없는 것들만 조회

    # 2. SBRET 모델로 content 데이터를 벡터화하기
    if not jobposting:
        """
        업데이트할 채용공고가 없으면 없다 리턴
        """
        return {"message": "업데이트할 채용공고가 없습니다."}
    
    update_count = 0

    for post in jobposting:
        embedding = model.encode(post.MainTasks).tolist()
        post.embedding = embedding  # embedding 컬럼에 벡터 넣기
        update_count += 1

    # 3. 데이터베이스에 저장하기
    db.commit()

    # 4. 응답하기
    return {"message": f"{update_count}개 채용공고가 업데이트 되었습니다."}