from enum import Enum
from server.src.schemas import BaseModel, EmailStr, Field, HttpUrl
from sqlalchemy import Column, Enum as SQLEnum
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Tuple, Union, Literal, Optional

'''
각 Schema의 column에 입력되는 type을 지정

예시:
    pydantic: 1차관문 ->  DB까지 가지전에 걸러줌
    sql: 2차관문 -> 데이터 무결성 최종 보장

    datetime.now() = 사진 한 장 찍어서 복사
    default_factory=datetime.now = 필요할 때마다 새로 찍기
'''

##################################################################################
# Enums
##################################################################################
class Provider(str, Enum):
    KAKAO = 'kakao'
    NAVER = 'naver'
    GOOGLE = 'google'

class Post_type(str, Enum):
    JOB = 'job'
    BOOTCAMP = 'bootcamp'

class Online_offline(str, Enum):
    ONLINE = '온라인'
    OFFLINE = '오프라인'
    MIX = '혼합형'

class Cost_support_type(str, Enum):
    PAY_K = '국비지원'
    PAY_SELF = '본인부담'


##################################################################################
# Models
##################################################################################
class Users(BaseModel):
    UserID: int
    Name: str = Field(max_length = 500)
    Email: EmailStr
    CareerLevelID: int
    CreatedAt: datetime = Field(default_factory = datetime.now)
    UpdatedAt: datetime = Field(default_factory = datetime.now)
    
class SocialLogins(BaseModel):
    SocialLoginID: int
    UserID: int
    Provider: Provider
    ProviderUserID: str
    LinkedAt: datetime = Field(default_factory = datetime.now)
    UnlinkedAt: Optional[datetime] = None

    class Config:
        from_attributes = True

class DesiredJobs(BaseModel):
    DesiredJobID: int
    JobName: str

class UserDesiredJobs(BaseModel):
    UserID: int
    DesiredJobID: int

class UserSkills(BaseModel):
    UserID: int
    SkillID: int

class UserNotificationSettings(BaseModel):
    UserNotificationID: int
    UserID: int
    NotificationType: str
    IsEnabled: bool = True
    NotificationTime: str

class Skills(BaseModel):
    SkillID: int
    SkillName: str

class MemberSkills(BaseModel):
    MemberID: int
    SkillID: int

class platforms(BaseModel):
    PlatformID: int
    PlatformName: str

class JobPosts(BaseModel):
    PostID: int
    PlatformID: int
    Title: str = Field(max_length = 500)
    CompanyName: str
    JobCategoryID: str
    EmploymentType: str
    ExperienceRequirement: str
    EducationRequirement: str
    Location: str
    MainTasks: Optional[str] = Field(None, max_length = 10000)
    Qualifications: Optional[str] = Field(None, max_length = 10000)
    Preferences: Optional[str] = Field(None, max_length = 10000)
    Benefits: Optional[str] = Field(None, max_length = 10000)
    Process: Optional[str] = Field(None, max_length = 10000)
    Salary: str
    PostedDate: datetime = Field(default_factory = datetime.now)
    CloseDate: datetime = Field(default_factory = datetime.now)
    ViewCount: int = 0
    Url: HttpUrl
    IsActive: bool = True
    CreatedAt: datetime = Field(default_factory = datetime.now)
    UpdatedAt: datetime = Field(default_factory = datetime.now)

class JobPostSkills(BaseModel):
    PostID: int
    SkillID: int

class Notifications(BaseModel):
    NotificationID: int
    MemberID: int
    NotificationType: str
    IsEnabled: bool = True
    NotificationTime: str

class UserScraps(BaseModel):
    ScrapID: int
    UserID: int
    PostType: Post_type
    JobPostID: int
    BootcampPostID: int
    ScrappedAt: datetime = Field(default_factory = datetime.now)

class JobCategories(BaseModel):
    CategoryID: int
    CategoryName: str
    ParentCategoryID: int
    Depth: int = 1          # 계층 깊이(1 = 대분류, 2 = 중분류, 3 = 소분류)

class BootcampPosts(BaseModel):
    BootcampID: int
    Title: str = Field(max_length = 500)
    InstituteName: str
    JobCategoryID: int
    Location: str
    OnlineOffline: Online_offline = Online_offline.ONLINE
    CostSupportType: Cost_support_type = Cost_support_type.PAY_SELF
    EducationContent: Optional[str] = Field(None, max_length = 10000)
    Qualification: Optional[str] = Field(None, max_length = 10000)
    Benefits: Optional[str] = Field(None, max_length = 10000)
    StartDate: datetime
    RegistrationDate: datetime
    CloseDate: datetime
    DetailUrl: HttpUrl
    ViewCount: int = 0
    CreatedAt: datetime = Field(default_factory = datetime.now)
    UpdatedAt: datetime = Field(default_factory = datetime.now)

class CareerLevels(BaseModel):
    CareerLevelID: int
    CareerName: str