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
    # CareerLevels 더미 데이터
    op.execute("""
    INSERT INTO CareerLevels (CareerName) VALUES
    ('신입'),
    ('경력'),
    ('전문가');
    """)

    # Users 더미 데이터
    op.execute("""
    INSERT INTO Users (Name, Email, CareerLevelID) VALUES
    ('홍길동', 'hong@example.com', 1),
    ('김철수', 'kim@example.com', 2),
    ('박영희', 'park@example.com', 3);
    """)

    # Skills 더미 데이터
    op.execute("""
    INSERT INTO Skills (SkillName) VALUES
    ('Python'),
    ('JavaScript'),
    ('SQL');
    """)

    # DesiredJobs 더미 데이터
    op.execute("""
    INSERT INTO DesiredJobs (JobName) VALUES
    ('백엔드 개발자'),
    ('프론트엔드 개발자'),
    ('데이터 엔지니어');
    """)

    # Platforms 더미 데이터
    op.execute("""
    INSERT INTO Platforms (PlatformName) VALUES
    ('Saramin'),
    ('JobKorea'),
    ('Wanted');
    """)

    # JobCategories 더미 데이터 (최상위 3개)
    op.execute("""
    INSERT INTO JobCategories (CategoryName, Depth) VALUES
    ('개발', 1),
    ('디자인', 1),
    ('마케팅', 1);
    """)

    # SocialLogins 더미 데이터 (UserID와 FK 맞춰서)
    op.execute("""
    INSERT INTO SocialLogins (UserID, Provider, ProviderUserID) VALUES
    (1, 'Kakao', 'kakao_001'),
    (2, 'Naver', 'naver_002'),
    (3, 'Google', 'google_003');
    """)

    # UserDesiredJobs 더미 데이터
    op.execute("""
    INSERT INTO UserDesiredJobs (UserID, DesiredJobID) VALUES
    (1, 1),
    (2, 2),
    (3, 3);
    """)

    # UserSkills 더미 데이터
    op.execute("""
    INSERT INTO UserSkills (UserID, SkillID) VALUES
    (1, 1),
    (2, 2),
    (3, 3);
    """)

    # UserNotificationSettings 더미 데이터
    op.execute("""
    INSERT INTO UserNotificationSettings (UserID, NotificationType, IsEnabled, NotificationTime) VALUES
    (1, '채용 알림', TRUE, '09:00'),
    (2, '맞춤형 정보', FALSE, '12:00'),
    (3, '이벤트 소식', TRUE, '18:00');
    """)

    # JobPosts 더미 데이터
    op.execute("""
    INSERT INTO JobPosts (PlatformID, Title, CompanyName, JobCategoryID, EmploymentType,
        ExperienceRequirement, MinExperienceYears, EducationRequirement, Location, MainTasks,
        Qualifications, Preferences, Benefits, Process, Salary, PostedDate, CloseDate, IsActive) VALUES
    (1, '백엔드 개발자 모집', 'A회사', 1, '정규직', '경력', 3, '학사 이상', '서울', '서버 개발 및 운영',
     'Java 경험자', '원격근무 가능', '연봉 5000만원', '서류 -> 면접', '5000만원 이상', '2025-11-01', '2025-12-01', TRUE),
    (2, '프론트엔드 개발자 채용', 'B회사', 1, '계약직', '신입', 0, '학사 이상', '부산', '웹 프론트 개발',
     'React 능숙자', '유연 근무', '복지 제공', '서류 -> 코딩 테스트', '3500만원', '2025-11-15', '2025-12-15', TRUE),
    (3, '데이터 엔지니어 구함', 'C회사', 1, '정규직', '경력', 2, '학사 이상', '원격', '데이터 파이프라인 구축',
     'Python, SQL 숙련자', '주 4일 근무', '스톡옵션', '서류 -> 면접', '6000만원', '2025-11-20', '2025-12-20', TRUE);
    """)

    # JobPostSkills 더미 데이터
    op.execute("""
    INSERT INTO JobPostSkills (PostID, SkillID) VALUES
    (1, 2),
    (2, 2),
    (3, 1);
    """)

    # BootcampPosts 더미 데이터
    op.execute("""
    INSERT INTO BootcampPosts (Title, InstituteName, JobCategoryID, Location, OnlineOffline, CostSupportType,
        EducationContent, Qualification, Benefits, StartDate, RegistrationDate, CloseDate, DetailUrl) VALUES
    ('파이썬 부트캠프', '코드스쿨', 1, '서울', '온라인', '국비지원', 'Python 기본, 데이터 분석', '없음', '수료증 발급',
     '2025-12-01', '2025-11-01', '2025-11-25', 'http://bootcamp1.example.com'),
    ('리액트 부트캠프', '프론트캠프', 1, '부산', '오프라인', '본인부담', 'React 기초부터 심화', '고등학교 졸업 이상', '취업 연계',
     '2026-01-05', '2025-12-01', '2025-12-30', 'http://bootcamp2.example.com'),
    ('데이터 엔지니어링 부트캠프', '데이터캠퍼스', 1, '원격', '혼합형', '국비지원', '빅데이터 처리, ETL', '학사 이상', '프로젝트 실습',
     '2026-02-01', '2026-01-01', '2026-01-20', 'http://bootcamp3.example.com');
    """)

    # UserScraps 더미 데이터
    op.execute("""
    INSERT INTO UserScraps (UserID, PostType, JobPostID, BootcampPostID) VALUES
    (1, 'Job', 1, NULL),
    (2, 'Job', 2, NULL),
    (3, 'Bootcamp', NULL, 3);
    """)


def downgrade():
    # 더미 데이터 삭제 (역순으로)
    op.execute("DELETE FROM UserScraps;")
    op.execute("DELETE FROM BootcampPosts;")
    op.execute("DELETE FROM JobPostSkills;")
    op.execute("DELETE FROM JobPosts;")
    op.execute("DELETE FROM UserNotificationSettings;")
    op.execute("DELETE FROM UserSkills;")
    op.execute("DELETE FROM UserDesiredJobs;")
    op.execute("DELETE FROM SocialLogins;")
    op.execute("DELETE FROM JobCategories;")
    op.execute("DELETE FROM Platforms;")
    op.execute("DELETE FROM DesiredJobs;")
    op.execute("DELETE FROM Skills;")
    op.execute("DELETE FROM Users;")
    op.execute("DELETE FROM CareerLevels;")