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
    -- 시퀀스 재설정
    ALTER SEQUENCE careerlevels_careerlevelid_seq RESTART WITH 1;
    
    INSERT INTO careerlevels (careername) VALUES
    ('학생'),
    ('신입'),
    ('경력');
    """)

    # ExperienceRanges 더미 데이터
    op.execute("""
    -- 시퀀스 재설정
    ALTER SEQUENCE experienceranges_rangeid_seq RESTART WITH 1;
    
    INSERT INTO experienceranges (rangename, minyears, maxyears) VALUES
    ('1년 미만', 0, 1),
    ('1~3년', 1, 3),
    ('3~5년', 3, 5),
    ('5년 이상', 5, NULL);
    """)

    # DesiredJobs 더미 데이터
    op.execute("""
    -- 시퀀스 재설정
    ALTER SEQUENCE desiredjobs_desiredjobid_seq RESTART WITH 1;
    
    INSERT INTO desiredjobs (jobname) VALUES
    ('백엔드 개발자'),
    ('프론트엔드 개발자'),
    ('데이터 엔지니어');
    """)

    # Roles 테이블 더미 데이터
    op.execute("""
    -- 시퀀스 재설정
    ALTER SEQUENCE roles_roleid_seq RESTART WITH 1;
    
    INSERT INTO roles (rolename) VALUES
    ('admin'),
    ('user');
    """)

    # Skills 더미 데이터
    op.execute("""
    -- 시퀀스 재설정
    ALTER SEQUENCE skills_skillid_seq RESTART WITH 1;
    
    INSERT INTO skills (skillname) VALUES
    ('Python'),
    ('JavaScript'),
    ('SQL');
    """)

    # Platforms 더미 데이터
    op.execute("""
    -- 시퀀스 재설정
    ALTER SEQUENCE platforms_platformid_seq RESTART WITH 1;
    
    INSERT INTO platforms (platformname) VALUES
    ('Saramin'),
    ('JobKorea'),
    ('Wanted');
    """)

    # JobCategories 더미 데이터 (최상위 3개)
    op.execute("""
    -- 시퀀스 재설정
    ALTER SEQUENCE jobcategories_categoryid_seq RESTART WITH 1;
    
    INSERT INTO jobcategories (categoryname, depth) VALUES
    ('개발', 1),
    ('디자인', 1),
    ('마케팅', 1);
    """)

    # UserNotificationSettings 더미 데이터
    # op.execute("""
    # INSERT INTO usernotificationsettings (userid, notificationtype, isenabled, notificationtime) VALUES
    # (1, '채용 알림', TRUE, '09:00'),
    # (2, '맞춤형 정보', FALSE, '12:00'),
    # (3, '이벤트 소식', TRUE, '18:00');
    # """)

    # JobPostSkills 더미 데이터
    # op.execute("""
    # INSERT INTO jobpostskills (postid, skillid) VALUES
    # (1, 2),
    # (2, 2),
    # (3, 1);
    # """)


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