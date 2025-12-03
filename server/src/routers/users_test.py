from fastapi import APIRouter, Depends, HTTPException, FastAPI
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# -----------------------------
# FastAPI 앱과 라우터 설정
# -----------------------------
router = APIRouter(prefix="/users_test")

# -----------------------------
# Pydantic 모델
# -----------------------------
class ProfileOut(BaseModel):
    user_id: int
    name: Optional[str]
    email: str
    career_level: Optional[Dict[str, Any]] = None
    skills: List[str] = []
    desired_jobs: List[str] = []

    class Config:
        orm_mode = True


class ProfileUpdate(BaseModel):
    name: Optional[str] = None
    career_level_id: Optional[int] = None
    skills: Optional[List[str]] = None
    desired_jobs: Optional[List[str]] = None
    employment_type: Optional[str] = None
    work_type: Optional[str] = None

# -----------------------------
# 임시 DB (메모리상)
# -----------------------------
class TempUser:
    def __init__(self, UserID, Name, Email, CareerLevelID=None):
        self.UserID = UserID
        self.Name = Name
        self.Email = Email
        self.CareerLevelID = CareerLevelID
        self.skills = []
        self.desired_jobs = []

class TempSkill:
    def __init__(self, SkillName):
        self.SkillName = SkillName

class TempJob:
    def __init__(self, JobName):
        self.JobName = JobName

class TempCareerLevel:
    def __init__(self, CareerLevelID, CareerName):
        self.CareerLevelID = CareerLevelID
        self.CareerName = CareerName

# 임시 데이터 생성
temp_users = {
    1: TempUser(1, "홍길동", "hong@example.com", CareerLevelID=1),
    2: TempUser(2, "주영희", "joo@example.com", CareerLevelID=2)
    
}

temp_careers = {
    1: TempCareerLevel(1, "주니어"),
    2: TempCareerLevel(2, "시니어")
}

# 임시 스킬/직무 샘플
temp_users[1].skills = [TempSkill("Python"), TempSkill("FastAPI")]
temp_users[1].desired_jobs = [TempJob("Backend Developer"), TempJob("Data Engineer")]
temp_users[2].skills = [TempSkill("Java"), TempSkill("FastAPI"), TempSkill("React")]
temp_users[2].desired_jobs = [TempJob("Backend Developer"), TempJob("web designer")]

# -----------------------------
# 임시 DB용 함수
# -----------------------------
def get_user_data(user_id: int):
    user = temp_users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    return user

# -----------------------------
# GET 프로필
# -----------------------------
@router.get("/{user_id}", response_model=ProfileOut)
def read_profile(user_id: int):
    user = get_user_data(user_id)
    career_name = None
    if user.CareerLevelID:
        career = temp_careers.get(user.CareerLevelID)
        if career:
            career_name = career.CareerName

    user_skills = [s.SkillName for s in user.skills]
    user_desired_jobs = [j.JobName for j in user.desired_jobs]

    return ProfileOut(
        user_id=user.UserID,
        name=user.Name,
        email=user.Email,
        career_level={"id": user.CareerLevelID, "name": career_name} if career_name else None,
        skills=user_skills,
        desired_jobs=user_desired_jobs
    )

# -----------------------------
# PUT 프로필 수정
# -----------------------------
@router.put("/{user_id}", response_model=ProfileOut)
def update_profile(user_id: int, data: ProfileUpdate):
    user = get_user_data(user_id)

    if data.name:
        user.Name = data.name

    if data.career_level_id:
        if data.career_level_id not in temp_careers:
            raise HTTPException(400, "Invalid career_level_id")
        user.CareerLevelID = data.career_level_id

    if data.skills is not None:
        user.skills = [TempSkill(name) for name in data.skills]

    if data.desired_jobs is not None:
        user.desired_jobs = [TempJob(name) for name in data.desired_jobs]

    return read_profile(user_id)


# -----------------------------
# 서버 실행
# -----------------------------
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)
