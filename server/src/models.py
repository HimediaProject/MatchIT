from src.database import Base
from datetime import datetime
from typing import List, Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, Date, DateTime, Text,
    ForeignKey, UniqueConstraint, CheckConstraint, Index, func
)
from sqlalchemy.orm import declarative_base, relationship

# Base = declarative_base()


# -------------------------------------------------------
# CareerLevels
# -------------------------------------------------------
class CareerLevel(Base):
    __tablename__ = "careerlevels"

    CareerLevelID = Column(Integer, primary_key=True, autoincrement=True)
    CareerName = Column(String(50), unique=True, nullable=False)

    users = relationship("User", back_populates="career_level")


# -------------------------------------------------------
# Users
# -------------------------------------------------------
class User(Base):
    __tablename__ = "users"

    UserID = Column(Integer, primary_key=True, autoincrement=True)
    Name = Column(String(100))
    Email = Column(String(255), unique=True, nullable=False)
    CareerLevelID = Column(Integer, ForeignKey("CareerLevel.CareerLevelID"))
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    career_level = relationship("CareerLevel", back_populates="users")
    social_logins = relationship("SocialLogin", back_populates="user")
    desired_jobs = relationship("DesiredJob", secondary="UserDesiredJobs", back_populates="users")
    skills = relationship("Skill", secondary="UserSkills", back_populates="users")
    notifications = relationship("UserNotificationSetting", back_populates="user")
    scraps = relationship("UserScrap", back_populates="user")


# -------------------------------------------------------
# SocialLogins
# -------------------------------------------------------
class SocialLogin(Base):
    __tablename__ = "socialLogins"

    SocialLoginID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    Provider = Column(String(20), nullable=False)
    ProviderUserID = Column(String(255), nullable=False)
    LinkedAt = Column(DateTime(timezone=True), server_default=func.now())
    UnlinkedAt = Column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("UserID", "Provider", name="uq_sociallogins_user_provider"),
        CheckConstraint("Provider IN ('Kakao', 'Naver', 'Google')",
                        name="chk_sociallogins_provider"),
    )

    user = relationship("User", back_populates="social_logins")


# -------------------------------------------------------
# DesiredJobs + UserDesiredJobs
# -------------------------------------------------------
class DesiredJob(Base):
    __tablename__ = "desiredjobs"

    DesiredJobID = Column(Integer, primary_key=True, autoincrement=True)
    JobName = Column(String(100), unique=True, nullable=False)

    users = relationship("User", secondary="UserDesiredJobs", back_populates="desired_jobs")


class UserDesiredJob(Base):
    __tablename__ = "userdesiredjobs"

    UserID = Column(Integer, ForeignKey("Users.UserID"), primary_key=True)
    DesiredJobID = Column(Integer, ForeignKey("DesiredJobs.DesiredJobID"), primary_key=True)


# -------------------------------------------------------
# Skills + UserSkills (M2M)
# -------------------------------------------------------
class Skill(Base):
    __tablename__ = "skills"

    SkillID = Column(Integer, primary_key=True, autoincrement=True)
    SkillName = Column(String(100), unique=True, nullable=False)

    users = relationship("User", secondary="UserSkills", back_populates="skills")
    job_posts = relationship("JobPost", secondary="JobPostSkills", back_populates="skills")


class UserSkill(Base):
    __tablename__ = "userskills"

    UserID = Column(Integer, ForeignKey("Users.UserID"), primary_key=True)
    SkillID = Column(Integer, ForeignKey("Skills.SkillID"), primary_key=True)


# -------------------------------------------------------
# User Notification Settings
# -------------------------------------------------------
class UserNotificationSetting(Base):
    __tablename__ = "usernotificationsettings"

    UserNotificationID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    NotificationType = Column(String(100))
    IsEnabled = Column(Boolean, default=True)
    NotificationTime = Column(String(50))

    user = relationship("User", back_populates="notifications")


# -------------------------------------------------------
# Platforms
# -------------------------------------------------------
class Platform(Base):
    __tablename__ = "platforms"

    PlatformID = Column(Integer, primary_key=True, autoincrement=True)
    PlatformName = Column(String(100), unique=True, nullable=False)

    job_posts = relationship("JobPost", back_populates="platform")


# -------------------------------------------------------
# JobCategories
# -------------------------------------------------------
class JobCategory(Base):
    __tablename__ = "jobcategories"

    CategoryID = Column(Integer, primary_key=True, autoincrement=True)
    CategoryName = Column(String(100), nullable=False)
    ParentCategoryID = Column(Integer, ForeignKey("JobCategories.CategoryID"))
    Depth = Column(Integer, nullable=False, default=1)

    parent = relationship("JobCategory", remote_side=[CategoryID])
    job_posts = relationship("JobPost", back_populates="job_category")
    bootcamp_posts = relationship("BootcampPost", back_populates="job_category")


# -------------------------------------------------------
# JobPosts
# -------------------------------------------------------
class JobPost(Base):
    __tablename__ = "jobposts"

    PostID = Column(Integer, primary_key=True, autoincrement=True)
    PlatformID = Column(Integer, ForeignKey("Platforms.PlatformID"), nullable=False)
    Title = Column(String(255))
    CompanyName = Column(String(255))
    JobCategoryID = Column(Integer, ForeignKey("JobCategories.CategoryID"), nullable=False)
    EmploymentType = Column(String(50))
    ExperienceRequirement = Column(String(10), nullable=False)
    MinExperienceYears = Column(Integer, default=0)
    EducationRequirement = Column(String(50))
    Location = Column(String(255))
    MainTasks = Column(Text)
    Qualifications = Column(Text)
    Preferences = Column(Text)
    Benefits = Column(Text)
    Process = Column(Text)
    Salary = Column(String(100))
    PostedDate = Column(Date)
    CloseDate = Column(Date)
    ViewCount = Column(Integer, default=0)
    Url = Column(String(500))
    IsActive = Column(Boolean, default=True)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("ExperienceRequirement IN ('신입','경력')",
                        name="chk_jobposts_experience_requirement"),
    )

    platform = relationship("Platform", back_populates="job_posts")
    job_category = relationship("JobCategory", back_populates="job_posts")
    skills = relationship("Skill", secondary="JobPostSkills", back_populates="job_posts")
    scraps = relationship("UserScrap", back_populates="job_post")


class JobPostSkill(Base):
    __tablename__ = "jobpostskills"

    PostID = Column(Integer, ForeignKey("JobPosts.PostID"), primary_key=True)
    SkillID = Column(Integer, ForeignKey("Skills.SkillID"), primary_key=True)


# -------------------------------------------------------
# BootcampPosts
# -------------------------------------------------------
class BootcampPost(Base):
    __tablename__ = "bootcampposts"

    BootcampID = Column(Integer, primary_key=True, autoincrement=True)
    Title = Column(String(255), nullable=False)
    InstituteName = Column(String(255), nullable=False)
    JobCategoryID = Column(Integer, ForeignKey("JobCategories.CategoryID"), nullable=False)
    Location = Column(String(255))
    OnlineOffline = Column(String(10), default="온라인")
    CostSupportType = Column(String(10), default="본인부담")
    EducationContent = Column(Text)
    Qualification = Column(Text)
    Benefits = Column(Text)
    StartDate = Column(Date)
    RegistrationDate = Column(Date)
    CloseDate = Column(Date)
    DetailUrl = Column(String(500))
    ViewCount = Column(Integer, default=0)
    CreatedAt = Column(DateTime(timezone=True), server_default=func.now())
    UpdatedAt = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        CheckConstraint("OnlineOffline IN ('온라인','오프라인','혼합형')"),
        CheckConstraint("CostSupportType IN ('국비지원','본인부담')"),
    )

    job_category = relationship("JobCategory", back_populates="bootcamp_posts")
    scraps = relationship("UserScrap", back_populates="bootcamp_post")


# -------------------------------------------------------
# UserScraps
# -------------------------------------------------------
class UserScrap(Base):
    __tablename__ = "userScraps"

    ScrapID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(Integer, ForeignKey("Users.UserID"), nullable=False)
    PostType = Column(String(20), nullable=False)
    JobPostID = Column(Integer, ForeignKey("JobPosts.PostID"))
    BootcampPostID = Column(Integer, ForeignKey("BootcampPosts.BootcampID"))
    ScrappedAt = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        CheckConstraint(
            "(PostType = 'Job' AND JobPostID IS NOT NULL AND BootcampPostID IS NULL) "
            "OR (PostType = 'Bootcamp' AND BootcampPostID IS NOT NULL AND JobPostID IS NULL)",
            name="chk_userscraps_only_one_ref"
        ),
        CheckConstraint("PostType IN ('Job','Bootcamp')"),
        Index("uq_userscraps_job", "UserID", "JobPostID", unique=True,
              postgresql_where=(PostType == 'Job')),
        Index("uq_userscraps_bootcamp", "UserID", "BootcampPostID", unique=True,
              postgresql_where=(PostType == 'Bootcamp')),
    )

    user = relationship("User", back_populates="scraps")
    job_post = relationship("JobPost", back_populates="scraps")
    bootcamp_post = relationship("BootcampPost", back_populates="scraps")