"""init

Revision ID: 8f3c89db1300
Revises: 
Create Date: 2025-11-28 17:15:56.621422

"""
from typing import Sequence, Union

from alembic import op
# import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8f3c89db1300'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None




def upgrade():
    # 1. 시퀀스 초기화
    op.execute("SELECT setval(pg_get_serial_sequence('roles', 'roleid'), 1, false);")
    op.execute("SELECT setval(pg_get_serial_sequence('careerlevels', 'careerlevelid'), 1, false);")
    op.execute("SELECT setval(pg_get_serial_sequence('experienceranges', 'rangeid'), 1, false);")
    op.execute("SELECT setval(pg_get_serial_sequence('users', 'userid'), 1, false);")
    op.execute("SELECT setval(pg_get_serial_sequence('skills', 'skillid'), 1, false);")
    op.execute("SELECT setval(pg_get_serial_sequence('desiredjobs', 'desiredjobid'), 1, false);")
    op.execute("SELECT setval(pg_get_serial_sequence('platforms', 'platformid'), 1, false);")
    op.execute("SELECT setval(pg_get_serial_sequence('jobcategories', 'categoryid'), 1, false);")
    op.execute("SELECT setval(pg_get_serial_sequence('jobposts', 'postid'), 1, false);")
    op.execute("SELECT setval(pg_get_serial_sequence('bootcampposts', 'bootcampid'), 1, false);")
    op.execute("SELECT setval(pg_get_serial_sequence('sociallogins', 'socialloginid'), 1, false);")
    op.execute("SELECT setval(pg_get_serial_sequence('usernotificationsettings', 'usernotificationid'), 1, false);")
    
    # 2. 데이터 삽입
    # CareerLevels 더미 데이터
    op.execute("""
    INSERT INTO roles (roleName) VALUES 
    ('User'),
    ('Admin')
    """)

    op.execute("""
    INSERT INTO careerlevels (careername) VALUES
    ('학생'),
    ('신입'),
    ('경력')
    """)

    # ExperienceRanges 더미 데이터
    op.execute("""
    INSERT INTO experienceranges (rangename, minyears, maxyears) VALUES
    ('1년 미만', 0, 1),
    ('1~3년', 1, 3),
    ('3~5년', 3, 5),
    ('5년 이상', 5, NULL);
    """)

    # 2️⃣ 종속된 테이블 (위의 테이블들을 참조)
    op.execute("""
    INSERT INTO users (name, email, roleid, careerlevelid, rangeid) VALUES
    ('홍길동', 'hong@example.com', 1, 1, 1),
    ('김철수', 'kim@example.com', 2, 2, 3),
    ('박영희', 'park@example.com', 2, 3, 4)
    """)

    # Skills 더미 데이터
    op.execute("""
    INSERT INTO skills (skillname) VALUES
    ('Python'),
    ('JavaScript'),
    ('SQL');
    """)

    # DesiredJobs 더미 데이터
    op.execute("""
    INSERT INTO desiredjobs (jobname) VALUES
    ('백엔드 개발자'),
    ('프론트엔드 개발자'),
    ('데이터 엔지니어');
    """)

    # Platforms 더미 데이터
    op.execute("""
    INSERT INTO platforms (platformname) VALUES
    ('Saramin'),
    ('JobKorea'),
    ('Wanted');
    """)

    # JobCategories 더미 데이터 (최상위 3개)
    op.execute("""
    INSERT INTO jobcategories (categoryname, depth) VALUES
    ('개발', 1),
    ('디자인', 1),
    ('마케팅', 1);
    """)

    # SocialLogins 더미 데이터 (UserID와 FK 맞춰서)
    op.execute("""
    INSERT INTO sociallogins (userid, provider, provideruserid) VALUES
    (1, 'Kakao', 'kakao_001'),
    (2, 'Naver', 'naver_002'),
    (3, 'Google', 'google_003');
    """)

    # UserDesiredJobs 더미 데이터
    op.execute("""
    INSERT INTO userdesiredjobs (userid, desiredjobid) VALUES
    (1, 1),
    (2, 2),
    (3, 3);
    """)

    # UserSkills 더미 데이터
    op.execute("""
    INSERT INTO userskills (userid, skillid) VALUES
    (1, 1),
    (2, 2),
    (3, 3);
    """)

    # UserNotificationSettings 더미 데이터
    op.execute("""
    INSERT INTO usernotificationsettings (userid, notificationtype, isenabled, notificationtime) VALUES
    (1, '채용 알림', TRUE, '09:00'),
    (2, '맞춤형 정보', FALSE, '12:00'),
    (3, '이벤트 소식', TRUE, '18:00');
    """)

    # JobPosts 더미 데이터
    op.execute("""
    INSERT INTO jobposts (platformid, title, companyname, jobcategoryid, employmenttype,
        experiencerequirement, minexperienceyears, educationrequirement, location, maintasks,
        qualifications, preferences, benefits, process, salary, posteddate, closedate, isactive) VALUES
    (1, '백엔드 개발자 모집', 'A회사', 1, '정규직', '경력', 3, '학사 이상', '서울', '서버 개발 및 운영',
     'Java 경험자', '원격근무 가능', '연봉 5000만원', '서류 -> 면접', '5000만원 이상', '2025-11-01', '2025-12-01', TRUE),
    (2, '프론트엔드 개발자 채용', 'B회사', 1, '계약직', '신입', 0, '학사 이상', '부산', '웹 프론트 개발',
     'React 능숙자', '유연 근무', '복지 제공', '서류 -> 코딩 테스트', '3500만원', '2025-11-15', '2025-12-15', TRUE),
    (3, '데이터 엔지니어 구함', 'C회사', 1, '정규직', '경력', 2, '학사 이상', '원격', '데이터 파이프라인 구축',
     'Python, SQL 숙련자', '주 4일 근무', '스톡옵션', '서류 -> 면접', '6000만원', '2025-11-20', '2025-12-20', TRUE);
    """)

    # JobPostSkills 더미 데이터
    op.execute("""
    INSERT INTO jobpostskills (postid, skillid) VALUES
    (1, 2),
    (2, 2),
    (3, 1);
    """)

    # BootcampPosts 더미 데이터
    op.execute("""
    INSERT INTO bootcampposts (title, institutename, jobcategoryid, location, onlineoffline, costsupporttype,
        educationcontent, qualification, benefits, startdate, registrationdate, closedate, detailurl) VALUES
    ('파이썬 부트캠프', '코드스쿨', 1, '서울', '온라인', '국비지원', 'Python 기본, 데이터 분석', '없음', '수료증 발급',
     '2025-12-01', '2025-11-01', '2025-11-25', 'http://bootcamp1.example.com'),
    ('리액트 부트캠프', '프론트캠프', 1, '부산', '오프라인', '본인부담', 'React 기초부터 심화', '고등학교 졸업 이상', '취업 연계',
     '2026-01-05', '2025-12-01', '2025-12-30', 'http://bootcamp2.example.com'),
    ('데이터 엔지니어링 부트캠프', '데이터캠퍼스', 1, '원격', '혼합형', '국비지원', '빅데이터 처리, ETL', '학사 이상', '프로젝트 실습',
     '2026-02-01', '2026-01-01', '2026-01-20', 'http://bootcamp3.example.com');
    """)

    # UserScraps 더미 데이터
    op.execute("""
    INSERT INTO userscraps (userid, posttype, jobpostid, bootcamppostid) VALUES
    (1, 'Job', 1, NULL),
    (2, 'Job', 2, NULL),
    (3, 'Bootcamp', NULL, 3);
    """)


def downgrade():
    # 더미 데이터 삭제 (역순으로)
    op.execute("DELETE FROM userscraps;")
    op.execute("DELETE FROM bootcampposts;")
    op.execute("DELETE FROM jobpostskills;")
    op.execute("DELETE FROM jobposts;")
    op.execute("DELETE FROM usernotificationsettings;")
    op.execute("DELETE FROM userskills;")
    op.execute("DELETE FROM userdesiredjobs;")
    op.execute("DELETE FROM sociallogins;")
    op.execute("DELETE FROM jobcategories;")
    op.execute("DELETE FROM platforms;")
    op.execute("DELETE FROM desiredjobs;")
    op.execute("DELETE FROM skills;")
    op.execute("DELETE FROM users;")
    op.execute("DELETE FROM careerlevels;")
    op.execute("DELETE FROM experienceranges;")