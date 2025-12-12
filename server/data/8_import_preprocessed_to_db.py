"""
전처리된 채용 공고 및 부트캠프 데이터를 PostgreSQL DB에 삽입

이 스크립트는 preprocess_jobs_data.py로 생성된 preprocessed_data.json 파일을
읽어서 DB에 삽입합니다.

실행 방법:
    python 8_import_preprocessed_to_db.py

필요 패키지:
    pip install psycopg2-binary sqlalchemy

전제 조건:
    - preprocessed_data.json 파일이 존재해야 함
    - DB 연결 정보 설정 필요 (DATABASE_URL)
"""

import os
import sys
import json
import locale
from dotenv import load_dotenv
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from typing import Dict, List, Optional
from urllib.parse import quote_plus

# Windows 환경에서 UTF-8 설정 강제
if sys.platform == 'win32':
    try:
        locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
    except:
        try:
            locale.setlocale(locale.LC_ALL, 'C.UTF-8')
        except:
            pass  # locale 설정 실패해도 계속 진행

# ============================================
# DB 연결 설정
# ============================================

# .env 파일 로드
load_dotenv()

# Windows 환경에서 UTF-8 인코딩 강제 설정
os.environ['PGCLIENTENCODING'] = 'UTF8'
os.environ['PYTHONIOENCODING'] = 'utf-8'

# 환경 변수 설정
USER = os.getenv("POSTGRES_USER")
PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB = os.getenv("POSTGRES_DB")

# 환경 변수 확인
if not all([USER, PASSWORD, DB]):
    print("\n❌ 에러: DB 연결 정보가 설정되지 않았습니다!")
    print("   .env 파일에 다음 환경 변수를 설정하세요:")
    print("   - POSTGRES_USER")
    print("   - POSTGRES_PASSWORD")
    print("   - POSTGRES_DB")
    print("\n   예시 (.env 파일):")
    print("   POSTGRES_USER = myuser")
    print("   POSTGRES_PASSWORD = mypassword")
    print("   POSTGRES_DB = mydb\n")
    exit(1)

# URL 인코딩 (특수문자 처리)
encoded_password = quote_plus(PASSWORD)
DATABASE_URL = f"postgresql://{USER}:{encoded_password}@postgres:5432/{DB}"

# 디버깅: DATABASE_URL 확인 (비밀번호 마스킹)
masked_url = DATABASE_URL.replace(encoded_password, "****")
print(f"🔗 DB 연결 URL: {masked_url}")
print(f"   인코딩: PGCLIENTENCODING={os.environ.get('PGCLIENTENCODING')}")

# UTF-8 인코딩으로 DB 연결
try:
    engine = create_engine(
        DATABASE_URL,
        echo = False,
        client_encoding = 'utf8',
        connect_args = {
            'client_encoding': 'utf8'
        },
        isolation_level = "AUTOCOMMIT"
    )
    SessionLocal = sessionmaker(bind=engine)
    print("   ✅ 엔진 생성 완료\n")
except Exception as e:
    print(f"   ❌ 엔진 생성 실패: {e}\n")
    raise

# ============================================
# 마스터 데이터 관리
# ============================================

class MasterDataManager:
    """Skills, JobCategories, Platforms의 ID 관리"""

    def __init__(self,
                 db_session):
        self.db = db_session
        self.skill_cache = {}      # {skill_name_lower: skill_id}
        self.category_cache = {}   # {category_name_lower: category_id}
        self.platform_cache = {}   # {platform_name_lower: platform_id}

        self._load_existing_data()

    def _load_existing_data(self):
        """기존 DB의 Skills, JobCategories, Platforms 로드"""
        print("📋 기존 DB마스터 데이터 로드 중...")

        # Skills
        result = self.db.execute(text("SELECT skillid, skillname FROM skills"))
        for row in result:
            self.skill_cache[row[1].lower()] = row[0]
        print(f"   Skills: {len(self.skill_cache)}개")

        # JobCategories
        result = self.db.execute(text("SELECT categoryid, categoryname FROM jobcategories"))
        for row in result:
            self.category_cache[row[1].lower()] = row[0]
        print(f"   Categories: {len(self.category_cache)}개")

        # Platforms
        result = self.db.execute(text("SELECT platformid, platformname FROM platforms"))
        for row in result:
            self.platform_cache[row[1].lower()] = row[0]
        print(f"   Platforms: {len(self.platform_cache)}개\n")

    def get_or_create_skill(self, skill_name: str) -> int:
        """Skill ID 가져오기 (없으면 생성)"""
        skill_lower = skill_name.lower()

        if skill_lower in self.skill_cache:
            return self.skill_cache[skill_lower]

        # 새로 생성
        result = self.db.execute(
            text("INSERT INTO skills (skillname) VALUES (:name) RETURNING skillid"),
            {"name": skill_name}
        )
        skill_id = result.fetchone()[0]
        self.skill_cache[skill_lower] = skill_id

        return skill_id

    def get_or_create_platform(self,
                               platform_name: str) -> int:
        """Platform ID 가져오기 (없으면 생성)"""
        platform_lower = platform_name.lower()

        if platform_lower in self.platform_cache:
            return self.platform_cache[platform_lower]

        # 새로 생성
        result = self.db.execute(
            text("INSERT INTO platforms (platformname) VALUES (:name) RETURNING platformid"),
            {"name": platform_name}
        )
        platform_id = result.fetchone()[0]
        self.platform_cache[platform_lower] = platform_id

        return platform_id

    def get_or_create_category(self,
                               category_name: str) -> int:
        """Category ID 가져오기 (없으면 생성)"""
        category_lower = category_name.lower()

        if category_lower in self.category_cache:
            return self.category_cache[category_lower]

        # 새로 생성 (ParentCategoryID=NULL, Depth=1)
        result = self.db.execute(
            text("""
                INSERT INTO jobcategories (categoryname, parentcategoryid, depth)
                VALUES (:name, NULL, 1)
                RETURNING categoryid
            """),
            {"name": category_name}
        )
        category_id = result.fetchone()[0]
        self.category_cache[category_lower] = category_id

        return category_id

# ============================================
# 데이터 로드
# ============================================

def load_preprocessed_data(filepath: str = 'preprocessed_data.json') -> Dict:
    """전처리된 데이터 로드 (인코딩 자동 감지)"""
    print(f"📂 전처리된 데이터 로드 중: {filepath}")

    # 여러 인코딩 시도
    encodings = ['utf-8', 'utf-8-sig', 'cp949', 'euc-kr', 'latin1']

    for encoding in encodings:
        try:
            with open(filepath, 'r', encoding=encoding) as f:
                data = json.load(f)
            print(f"   ℹ️  인코딩: {encoding}")
            print(f"   ✅ 채용 공고: {len(data.get('jobs', []))}개")
            print(f"   ✅ 부트캠프: {len(data.get('bootcamps', []))}개\n")
            return data
        except (UnicodeDecodeError, json.JSONDecodeError):
            continue

    # 모든 인코딩 실패
    raise Exception(f"파일을 읽을 수 없습니다: {filepath}. 시도한 인코딩: {encodings}")

def parse_date(date_str: Optional[str]) -> Optional[datetime]:
    """날짜 문자열 파싱"""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return None

# ============================================
# JobPosts 삽입
# ============================================

def insert_job_posts(db_session, preprocessed_jobs: List[Dict], master_data: MasterDataManager):
    """JobPosts 테이블에 전처리된 데이터 삽입"""

    print("=" * 70)
    print("📝 JobPosts 삽입 시작")
    print("=" * 70)

    inserted_count = 0
    updated_count = 0
    skipped_count = 0
    job_post_mapping = {}  # {original_id: (PostID, normalized_skills)}

    for idx, job_item in enumerate(preprocessed_jobs, 1):
        try:
            processed = job_item['processed']

            # 중복 체크 (URL 기준)
            existing = db_session.execute(
                text("SELECT postid FROM jobposts WHERE url = :url"),
                {"url": processed['url']}
            ).fetchone()

            # Platform ID
            platform_id = master_data.get_or_create_platform(processed['platform_name'])

            # Category ID
            category_id = master_data.get_or_create_category(processed['category_name'])

            if existing:
                # 기존 데이터 업데이트
                post_id = existing[0]
                db_session.execute(text("""
                    UPDATE jobposts SET
                        platformid = :platform_id,
                        title = :title,
                        companyname = :company,
                        jobcategoryid = :category_id,
                        employmenttype = :employment_type,
                        experiencerequirement = :experience_req,
                        minexperienceyears = :min_exp,
                        educationrequirement = :education_req,
                        location = :location,
                        maintasks = :main_tasks,
                        qualifications = :qualifications,
                        preferences = :preferences,
                        benefits = :benefits,
                        salary = :salary,
                        closedate = :close_date
                    WHERE postid = :post_id
                """), {
                    "post_id": post_id,
                    "platform_id": platform_id,
                    "title": processed['title'],
                    "company": processed['company_name'],
                    "category_id": category_id,
                    "employment_type": processed['employment_type'],
                    "experience_req": processed['career_type'],
                    "min_exp": processed['min_experience_years'],
                    "education_req": processed.get('education_requirement'),
                    "location": processed.get('location'),
                    "main_tasks": processed.get('main_tasks'),
                    "qualifications": processed.get('qualifications'),
                    "preferences": processed.get('preferences'),
                    "benefits": processed.get('benefits'),
                    "salary": processed['parsed_salary'] if processed['parsed_salary'] else None,
                    "close_date": parse_date(processed.get('parsed_close_date'))
                })

                job_post_mapping[processed['original_id']] = (
                    post_id,
                    processed['normalized_skills']
                )
                updated_count += 1
            else:
                # 신규 데이터 삽입
                result = db_session.execute(text("""
                    INSERT INTO jobposts (
                        platformid, title, companyname, jobcategoryid,
                        employmenttype, experiencerequirement, minexperienceyears,
                        educationrequirement, location, maintasks,
                        qualifications, preferences, benefits, process,
                        salary, posteddate, closedate, url, isactive
                    ) VALUES (
                        :platform_id, :title, :company, :category_id,
                        :employment_type, :experience_req, :min_exp,
                        :education_req, :location, :main_tasks,
                        :qualifications, :preferences, :benefits, :process,
                        :salary, CURRENT_DATE, :close_date, :url, :is_active
                    ) RETURNING postid
                """), {
                    "platform_id": platform_id,
                    "title": processed['title'],
                    "company": processed['company_name'],
                    "category_id": category_id,
                    "employment_type": processed['employment_type'],
                    "experience_req": processed['career_type'],
                    "min_exp": processed['min_experience_years'],
                    "education_req": processed.get('education_requirement'),
                    "location": processed.get('location'),
                    "main_tasks": processed.get('main_tasks'),
                    "qualifications": processed.get('qualifications'),
                    "preferences": processed.get('preferences'),
                    "benefits": processed.get('benefits'),
                    "process": None,
                    "salary": processed['parsed_salary'] if processed['parsed_salary'] else None,
                    "close_date": parse_date(processed.get('parsed_close_date')),
                    "url": processed['url'],
                    "is_active": True
                })

                post_id = result.fetchone()[0]
                job_post_mapping[processed['original_id']] = (
                    post_id,
                    processed['normalized_skills']
                )
                inserted_count += 1

            if idx % 100 == 0:
                print(f"   진행: {idx}/{len(preprocessed_jobs)} ({inserted_count}개 삽입, {updated_count}개 업데이트)")

        except Exception as e:
            print(f"   ❌ 에러 (Job ID: {job_item.get('processed', {}).get('original_id', 'unknown')}): {e}")
            continue

    db_session.commit()

    print(f"\n✅ JobPosts 삽입 완료!")
    print(f"   신규 삽입: {inserted_count}개")
    print(f"   업데이트: {updated_count}개")
    print(f"   총 처리: {inserted_count + updated_count}개\n")

    return job_post_mapping

# ============================================
# JobPostSkills 삽입
# ============================================

def insert_job_post_skills(db_session,
                           job_post_mapping: Dict,
                           master_data: MasterDataManager):
    """JobPostSkills 관계 테이블 삽입"""

    print("=" * 70)
    print("🔗 JobPostSkills 삽입 시작")
    print("=" * 70)

    inserted_count = 0

    for original_id, (post_id, normalized_skills) in job_post_mapping.items():
        for skill_name in normalized_skills:
            try:
                skill_id = master_data.get_or_create_skill(skill_name)

                # 중복 체크
                existing = db_session.execute(
                    text("SELECT 1 FROM jobpostskills WHERE postid = :post_id AND skillid = :skill_id"),
                    {"post_id": post_id, "skill_id": skill_id}
                ).fetchone()

                if existing:
                    continue

                # INSERT
                db_session.execute(
                    text("INSERT INTO jobpostskills (postid, skillid) VALUES (:post_id, :skill_id)"),
                    {"post_id": post_id, "skill_id": skill_id}
                )

                inserted_count += 1

            except Exception as e:
                print(f"   ❌ 에러 (PostID: {post_id}, Skill: {skill_name}): {e}")
                continue

    db_session.commit()

    print(f"✅ JobPostSkills 삽입 완료: {inserted_count}개\n")

# ============================================
# BootcampPosts 삽입
# ============================================

def insert_bootcamp_posts(db_session,
                          preprocessed_bootcamps: List[Dict],
                          master_data: MasterDataManager):
    """BootcampPosts 테이블에 전처리된 데이터 삽입"""

    print("=" * 70)
    print("🎓 BootcampPosts 삽입 시작")
    print("=" * 70)

    inserted_count = 0
    skipped_count = 0

    for idx, bootcamp_item in enumerate(preprocessed_bootcamps, 1):
        try:
            processed = bootcamp_item['processed']

            # 필수 필드 검증 (title, detail_url)
            if not processed.get('title'):
                skipped_count += 1
                continue

            # 중복 체크 (URL 기준)
            if not processed['detail_url']:
                skipped_count += 1
                continue

            existing = db_session.execute(
                text("SELECT bootcampid FROM bootcampposts WHERE detailurl = :url"),
                {"url": processed['detail_url']}
            ).fetchone()

            if existing:
                skipped_count += 1
                continue

            # Category ID
            category_id = master_data.get_or_create_category(processed['category_name'])

            # INSERT
            result = db_session.execute(text("""
                INSERT INTO bootcampposts (
                    title, institutename, jobcategoryid, location,
                    onlineoffline, costsupporttype, educationcontent,
                    qualification, benefits, startdate, registrationdate,
                    closedate, detailurl
                ) VALUES (
                    :title, :institute, :category_id, :location,
                    :online_offline, :cost_support, :education_content,
                    :qualification, :benefits, :start_date, :reg_date,
                    :close_date, :detail_url
                ) RETURNING bootcampid
            """), {
                "title": processed['title'],
                "institute": processed['institute_name'],
                "category_id": category_id,
                "location": processed.get('location'),
                "online_offline": processed['online_offline'],
                "cost_support": processed['cost_support'],
                "education_content": processed.get('education_content', ''),
                "qualification": processed.get('qualification', ''),
                "benefits": processed.get('benefits', ''),
                "start_date": parse_date(processed.get('start_date')),
                "reg_date": None,
                "close_date": parse_date(processed.get('close_date')),
                "detail_url": processed['detail_url']
            })

            inserted_count += 1

            if idx % 50 == 0:
                print(f"   진행: {idx}/{len(preprocessed_bootcamps)} ({inserted_count}개 삽입, {skipped_count}개 스킵)")

        except Exception as e:
            print(f"   ❌ 에러 (Bootcamp: {bootcamp_item.get('processed', {}).get('title', 'unknown')}): {e}")
            continue

    db_session.commit()

    print(f"\n✅ BootcampPosts 삽입 완료!")
    print(f"   삽입: {inserted_count}개")
    print(f"   스킵(중복): {skipped_count}개\n")

# ============================================
# 메인 실행
# ============================================

def main():
    print("\n" + "=" * 70)
    print("🚀 전처리된 데이터 DB 삽입 시작")
    print("=" * 70 + "\n")

    # 전처리된 데이터 로드
    try:
        preprocessed_data = load_preprocessed_data('preprocessed_data.json')
    except FileNotFoundError:
        print("❌ preprocessed_data.json 파일을 찾을 수 없습니다!")
        print("   먼저 preprocess_jobs_data.py를 실행하세요.\n")
        return

    # DB 세션 생성
    db = SessionLocal()

    try:
        # 마스터 데이터 관리자 초기화
        master_data = MasterDataManager(db)

        # 1. 채용 공고 처리
        preprocessed_jobs = preprocessed_data.get('jobs', [])
        if preprocessed_jobs:
            print("\n[1/2] 채용 공고 DB 삽입")
            print("-" * 70)
            job_post_mapping = insert_job_posts(db,
                                                preprocessed_jobs,
                                                master_data)
            insert_job_post_skills(db,
                                   job_post_mapping,
                                   master_data)

        # 2. 부트캠프 처리
        preprocessed_bootcamps = preprocessed_data.get('bootcamps', [])
        if preprocessed_bootcamps:
            print("\n[2/2] 부트캠프 DB 삽입")
            print("-" * 70)
            insert_bootcamp_posts(db,
                                  preprocessed_bootcamps,
                                  master_data)

        # 최종 결과
        print("=" * 70)
        print("🎉 모든 작업 완료!")
        print("=" * 70)
        print(f"\n📊 최종 결과:")
        print(f"   Skills: {len(master_data.skill_cache)}개")
        print(f"   Categories: {len(master_data.category_cache)}개")
        print(f"   Platforms: {len(master_data.platform_cache)}개\n")

    except Exception as e:
        print(f"\n❌ 에러 발생: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
        raise

    finally:
        db.close()

if __name__ == "__main__":
    # ⚠️ 실행 전 DATABASE_URL 수정 필수!
    print("\n⚠️  주의: DATABASE_URL을 실제 DB 정보로 변경하세요!")
    print("   (스크립트 상단의 DATABASE_URL 변수)\n")

    response = input("계속하시겠습니까? (y/N): ")
    if response.lower() == 'y':
        main()
    else:
        print("취소되었습니다.")
