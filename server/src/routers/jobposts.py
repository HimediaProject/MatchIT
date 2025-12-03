from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_ 
from typing import Optional
from src.database import get_db
from src.models import JobPost, JobCategory, Skill, Platform 
from src.schemas import JobPostCreate, JobPostUpdate, JobPostResponse, PaginatedJobPostResponse
from datetime import datetime

router = APIRouter(prefix="/jobs")


@router.post("/", response_model=JobPostResponse, status_code=201)  # 새 채용공고를 생성하는 POST /jobs 엔드포인트
def create_job_post( 
    job: JobPostCreate,  
    db: Session = Depends(get_db),  
):  
    # 1) Platform 존재 여부 확인
    platform = db.query(Platform).filter(Platform.PlatformID == job.PlatformID).first()
    if not platform:  # 플랫폼이 조회되지 않은 경우
        raise HTTPException(status_code=404, detail="Platform not found")  # 404 에러를 발생시켜 잘못된 PlatformID임을 알려줌

    # 2) JobCategory 존재 여부 확인
    category = db.query(JobCategory).filter(JobCategory.CategoryID == job.JobCategoryID).first()  # JobCategoryID가 유효한지 DB에서 조회
    if not category:
        raise HTTPException(status_code=404, detail="JobCategory not found")  # 404 에러를 발생시켜 잘못된 카테고리임을 알려줌

    # 3) JobPost 테이블에 삽입할 ORM 객체 생성
    job_data = job.model_dump(exclude={"SkillIDs"})  # Pydantic 모델을 dict로 변환하되, SkillIDs는 별도 처리할 것이므로 제외
    db_job = JobPost(**job_data)  # dict로 변환된 데이터를 언팩해서 JobPost ORM 인스턴스를 생성

    db.add(db_job)  # 새로 만든 JobPost 객체를 세션에 추가
    db.commit()  # 트랜잭션을 커밋하여 실제 DB에 반영
    db.refresh(db_job)  # 커밋 후 db_job 객체를 다시 읽어와서 생성된 PostID 등 값을 반영

    # 4) SkillIDs가 넘어온 경우 M2M 관계 설정
    if job.SkillIDs:  # 요청에 SkillIDs 리스트가 포함되어 있는지 확인
        for skill_id in job.SkillIDs:  # 각 스킬 ID에 대해 반복
            skill_obj = db.query(Skill).filter(Skill.SkillID == skill_id).first()  # 해당 스킬이 DB에 존재하는지 조회
            if not skill_obj:  # 스킬이 존재하지 않을 경우
                raise HTTPException(status_code=404, detail=f"Skill not found: {skill_id}")  # 어떤 스킬 ID가 잘못되었는지 명시하여 404 에러 발생
            db_job.skills.append(skill_obj)  # JobPost와 Skill 사이의 관계 리스트에 이 스킬을 추가하여 M2M 관계를 설정
        db.commit()  # 스킬 연결 관계를 DB에 반영하기 위해 커밋
        db.refresh(db_job)  # 변경된 관계를 반영한 최신 상태의 db_job 객체를 다시 로드

    # 5) 응답 스키마로 변환할 때 Skills 필드에 스킬 이름을 넣기 위해 수동으로 리스트 생성
    skills_names = [skill.SkillName for skill in db_job.skills]  # 현재 공고와 연결된 Skill 객체들에서 스킬 이름만 추출한 리스트 생성
    response_data = JobPostResponse(  # JobPostResponse 스키마 인스턴스를 직접 생성
        PostID=db_job.PostID,  # ORM 객체에서 PostID 값을 복사
        PlatformID=db_job.PlatformID,  # 플랫폼 ID 복사
        Title=db_job.Title,  # 제목 복사
        CompanyName=db_job.CompanyName,  # 회사 이름 복사
        JobCategoryID=db_job.JobCategoryID,  # 카테고리 ID 복사
        EmploymentType=db_job.EmploymentType,  # 고용 형태 복사
        ExperienceRequirement=db_job.ExperienceRequirement,  # 경력 요건 복사
        MinExperienceYears=db_job.MinExperienceYears,  # 최소 경력 연차 복사
        EducationRequirement=db_job.EducationRequirement,  # 학력 요건 복사
        Location=db_job.Location,  # 근무지 복사
        MainTasks=db_job.MainTasks,  # 주요 업무 내용 복사
        Qualifications=db_job.Qualifications,  # 자격 요건 복사
        Preferences=db_job.Preferences,  # 우대사항 복사
        Benefits=db_job.Benefits,  # 복지/혜택 복사
        Process=db_job.Process,  # 전형 절차 복사
        Salary=db_job.Salary,  # 연봉 정보 복사
        PostedDate=db_job.PostedDate,  # 게시일 복사
        CloseDate=db_job.CloseDate,  # 마감일 복사
        ViewCount=db_job.ViewCount,  # 조회수 복사
        Url=db_job.Url,  # 공고 URL 복사
        IsActive=db_job.IsActive,  # 활성 여부 복사
        CreatedAt=db_job.CreatedAt,  # 생성 시각 복사
        UpdatedAt=db_job.UpdatedAt,  # 수정 시각 복사
        Skills=skills_names,  # 스킬 이름 리스트를 Skills 필드에 대입
    )  # 응답 데이터 생성 끝

    return response_data  # 생성된 JobPostResponse 객체를 클라이언트에게 반환


@router.get("/", response_model=PaginatedJobPostResponse)  # 채용공고 목록을 페이지네이션+검색과 함께 조회하는 GET /jobs 엔드포인트 정의
def get_job_posts(  # JobPost 목록 조회 함수 정의
    page: int = Query(1, ge=1, description="페이지 번호"),  # page 쿼리 파라미터, 1 이상의 정수만 허용하고 기본값은 1
    size: int = Query(10, ge=1, le=100, description="페이지 당 항목 수"),  # size 쿼리 파라미터, 1~100 사이의 정수만 허용
    keyword: Optional[str] = Query(None, description="검색 키워드 (제목, 회사명, 스킬 이름)"),  # keyword 쿼리 파라미터, 제목/회사/스킬명을 부분 검색에 사용
    category_id: Optional[int] = Query(None, description="직무 카테고리 ID"),  # 직무 카테고리 필터용 쿼리 파라미터
    location: Optional[str] = Query(None, description="지역 필터"),  # 근무지(지역) 필터용 쿼리 파라미터
    experience_requirement: Optional[str] = Query(None, description="경력 요건 필터 (신입/경력)"),  # ExperienceRequirement 필터용 쿼리 파라미터
    db: Session = Depends(get_db),  # DB 세션을 의존성 주입으로 받아옴
):  # 함수 헤더 끝
    query = db.query(JobPost)  # JobPost 테이블을 대상으로 하는 기본 쿼리 객체 생성

    if keyword:  # keyword가 전달된 경우에만 검색 조건을 추가
        query = query.outerjoin(JobPost.skills)  # Skill 테이블과의 M2M 관계를 outer join하여 스킬 이름으로도 검색 가능하게 함
        pattern = f"%{keyword}%"  # 부분 일치를 위한 LIKE 패턴 생성
        query = query.filter(  # 제목, 회사명, 스킬명 중 하나라도 keyword를 포함하는지 필터링
            or_(
                JobPost.Title.ilike(pattern),  # 제목에서 keyword 대소문자 구분 없이 검색
                JobPost.CompanyName.ilike(pattern),  # 회사명에서 keyword 검색
                Skill.SkillName.ilike(pattern),  # 스킬 이름에서 keyword 검색
            )
        ).distinct()  # 동일 JobPost가 여러 스킬과 매칭될 때 중복 row를 제거하기 위해 distinct 사용

    if category_id is not None:  # 카테고리 ID가 전달된 경우
        query = query.filter(JobPost.JobCategoryID == category_id)  # JobCategoryID가 일치하는 공고만 필터링

    if location:  # location 필터가 전달된 경우
        query = query.filter(JobPost.Location.ilike(f"%{location}%"))  # Location 컬럼에서 부분 일치 검색 수행

    if experience_requirement:  # 경력 요건 필터가 전달된 경우
        query = query.filter(JobPost.ExperienceRequirement == experience_requirement)  # ExperienceRequirement가 정확히 일치하는 공고만 선택

    total = query.count()  # 현재 필터 조건을 만족하는 전체 공고 수를 먼저 계산

    offset = (page - 1) * size  # 페이지네이션을 위한 offset 계산 (0부터 시작하는 인덱스)
    jobs = (  # 실제로 조회할 JobPost 목록을 쿼리 실행하여 가져옴
        query.order_by(JobPost.CreatedAt.desc())  # 최신 생성 순으로 정렬하여 보여주기 위해 CreatedAt 기준 내림차순 정렬
        .offset(offset)  # offset만큼 건너뛰고
        .limit(size)  # size 개수만큼만 가져옴
        .all()  # 쿼리를 실행하여 결과를 리스트로 반환
    )

    items: list[JobPostResponse] = []  # 최종 응답에 담을 JobPostResponse 객체 리스트를 초기화

    for job_post in jobs:  # 조회된 각 JobPost ORM 객체에 대해 반복
        skills_names = [skill.SkillName for skill in job_post.skills]  # 연결된 스킬들의 이름만 추출하여 리스트로 만듦
        item = JobPostResponse(  # JobPostResponse 스키마 인스턴스를 생성
            PostID=job_post.PostID,  # 각 필드는 db에서 가져온 값으로 채움
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
            Skills=skills_names,  # 공고와 연결된 스킬 이름 리스트를 포함
        )
        items.append(item)  # 생성한 JobPostResponse 인스턴스를 items 리스트에 추가

    return PaginatedJobPostResponse(  # 페이지네이션 정보를 포함한 최종 응답 객체 생성
        total=total,  # 전체 공고 수
        page=page,  # 현재 페이지 번호
        size=size,  # 한 페이지당 항목 수
        items=items,  # JobPostResponse 리스트
    )  # 응답 객체 반환 끝


@router.get("/{job_id}", response_model=JobPostResponse)  # 단일 채용공고 상세 조회를 위한 GET /jobs/{job_id} 엔드포인트 정의
def get_job_post_detail(  # JobPost 상세 조회 함수 정의
    job_id: int,  # 경로 파라미터로 전달되는 채용공고 ID
    db: Session = Depends(get_db),  # DB 세션 의존성 주입
):  # 함수 헤더 끝
    job_post = db.query(JobPost).filter(JobPost.PostID == job_id).first()  # 주어진 PostID에 해당하는 JobPost를 DB에서 조회

    if not job_post:  # 조회 결과가 없는 경우
        raise HTTPException(status_code=404, detail="JobPost not found")  # 404 에러를 발생시켜 존재하지 않는 공고임을 알림

    job_post.ViewCount += 1  # 상세 조회 시 조회수를 1 증가
    job_post.UpdatedAt = datetime.now(job_post.UpdatedAt.tzinfo) if job_post.UpdatedAt else datetime.utcnow()  # UpdatedAt을 현재 시각으로 갱신(타임존 유지)
    db.commit()  # 변경 사항(조회수, UpdatedAt)을 DB에 반영
    db.refresh(job_post)  # 갱신된 값을 재조회하여 job_post 객체를 최신 상태로 만듦

    skills_names = [skill.SkillName for skill in job_post.skills]  # 연결된 스킬 이름을 리스트로 준비

    return JobPostResponse(  # JobPostResponse 스키마로 응답 객체를 생성하여 반환
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
        Skills=skills_names,  # 스킬 이름 리스트 포함
    )


@router.put("/{job_id}", response_model=JobPostResponse)  # 채용공고 수정을 위한 PUT /jobs/{job_id} 엔드포인트 정의
def update_job_post(  # JobPost 수정 함수 정의
    job_id: int,  # 수정할 공고의 ID
    job_update: JobPostUpdate,  # 수정 요청으로 받은 데이터(모든 필드가 Optional)
    db: Session = Depends(get_db),  # DB 세션 의존성 주입
):  # 함수 헤더 끝
    job_post = db.query(JobPost).filter(JobPost.PostID == job_id).first()  # DB에서 해당 ID의 JobPost를 조회

    if not job_post:  # 조회 결과가 없는 경우
        raise HTTPException(status_code=404, detail="JobPost not found")  # 404 에러를 발생시켜 존재하지 않는 공고임을 알림

    if job_update.JobCategoryID is not None:  # 요청에 JobCategoryID가 포함되어 있으면
        category = db.query(JobCategory).filter(JobCategory.CategoryID == job_update.JobCategoryID).first()  # 해당 카테고리가 존재하는지 확인
        if not category:  # 카테고리가 존재하지 않을 경우
            raise HTTPException(status_code=404, detail="JobCategory not found")  # 404 에러 발생

    if job_update.PlatformID is not None:  # PlatformID 변경 요청이 있을 경우
        platform = db.query(Platform).filter(Platform.PlatformID == job_update.PlatformID).first()  # 플랫폼이 존재하는지 확인
        if not platform:  # 플랫폼이 존재하지 않을 경우
            raise HTTPException(status_code=404, detail="Platform not found")  # 404 에러 발생

    update_data = job_update.model_dump(exclude_unset=True, exclude={"SkillIDs"})  # 전달된 필드 중 실제 수정할 값만 dict로 추출(SkillIDs 제외)
    for field, value in update_data.items():  # 수정할 각 필드에 대해 반복
        setattr(job_post, field, value)  # job_post 객체의 해당 속성에 새로운 값을 설정

    if job_update.SkillIDs is not None:  # SkillIDs가 요청에 포함된 경우(스킬 목록 전체 재설정)
        job_post.skills.clear()  # 기존에 연결된 모든 스킬 관계를 제거
        for skill_id in job_update.SkillIDs:  # 새로운 스킬 ID 리스트를 순회
            skill_obj = db.query(Skill).filter(Skill.SkillID == skill_id).first()  # 각 스킬이 DB에 존재하는지 조회
            if not skill_obj:  # 존재하지 않는 스킬이 있을 경우
                raise HTTPException(status_code=404, detail=f"Skill not found: {skill_id}")  # 어떤 스킬 ID가 잘못되었는지 포함하여 에러 반환
            job_post.skills.append(skill_obj)  # 유효한 스킬이라면 JobPost와의 관계에 추가

    job_post.UpdatedAt = datetime.now(job_post.UpdatedAt.tzinfo) if job_post.UpdatedAt else datetime.utcnow()  # 수정 시각을 현재 시각으로 갱신
    db.commit()  # 모든 변경 사항을 DB에 커밋
    db.refresh(job_post)  # 갱신된 내용을 반영하기 위해 job_post 객체를 새로 읽어옴

    skills_names = [skill.SkillName for skill in job_post.skills]  # 최종적으로 연결된 스킬 이름 리스트 생성

    return JobPostResponse(  # 수정된 JobPost 정보를 스키마로 감싸서 반환
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


@router.delete("/{job_id}", status_code=204)  # 채용공고 삭제를 위한 DELETE /jobs/{job_id} 엔드포인트 정의, 성공 시 204 No Content 반환
def delete_job_post(  # JobPost 삭제 함수 정의
    job_id: int,  # 삭제할 공고의 ID
    db: Session = Depends(get_db),  # DB 세션 의존성 주입
):  # 함수 헤더 끝
    job_post = db.query(JobPost).filter(JobPost.PostID == job_id).first()  # 해당 ID의 JobPost를 DB에서 조회

    if not job_post:  # 조회 결과가 없는 경우
        raise HTTPException(status_code=404, detail="JobPost not found")  # 404 에러를 발생시켜 존재하지 않는 공고임을 알림

    db.delete(job_post)  # 조회된 JobPost 객체를 세션에서 삭제 대상으로 표시
    db.commit()  # 트랜잭션을 커밋하여 실제 DB에서 레코드를 삭제

    return None  # 204 상태코드에 맞게 응답 본문은 비워둠
