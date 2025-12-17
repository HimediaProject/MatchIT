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
    # # # 1. 시퀀스 초기화
    # op.execute("SELECT setval(pg_get_serial_sequence('roles', 'roleid'), 1, false);")
    # op.execute("SELECT setval(pg_get_serial_sequence('careerlevels', 'careerlevelid'), 1, false);")
    # op.execute("SELECT setval(pg_get_serial_sequence('experienceranges', 'rangeid'), 1, false);")
    # op.execute("SELECT setval(pg_get_serial_sequence('users', 'userid'), 1, false);")
    # op.execute("SELECT setval(pg_get_serial_sequence('skills', 'skillid'), 1, false);")
    # op.execute("SELECT setval(pg_get_serial_sequence('desiredjobs', 'desiredjobid'), 1, false);")
    # op.execute("SELECT setval(pg_get_serial_sequence('platforms', 'platformid'), 1, false);")
    # op.execute("SELECT setval(pg_get_serial_sequence('jobcategories', 'categoryid'), 1, false);")
    # op.execute("SELECT setval(pg_get_serial_sequence('jobposts', 'postid'), 1, false);")
    # op.execute("SELECT setval(pg_get_serial_sequence('bootcampposts', 'bootcampid'), 1, false);")
    # op.execute("SELECT setval(pg_get_serial_sequence('sociallogins', 'socialloginid'), 1, false);")
    # op.execute("SELECT setval(pg_get_serial_sequence('usernotificationsettings', 'usernotificationid'), 1, false);")
    
    # 2. 데이터 삽입

    # CareerLevels 더미 데이터
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

    # DesiredJobs 더미 데이터
    op.execute("""
    INSERT INTO desiredjobs (jobname) VALUES
    ('백엔드 개발자'),
    ('프론트엔드 개발자'),
    ('데이터 엔지니어');
    """)

    # Skills 더미 데이터
    op.execute("""
    INSERT INTO skills (skillname) VALUES
    ('Python'),
    ('JavaScript'),
    ('SQL');
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