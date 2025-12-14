import time
import logging
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# .env는 라우터 모듈 import 이전에 로드되어야 import-time 환경변수 접근이 안정적입니다.
_possible_env_paths = [
    Path(__file__).resolve().parents[1] / ".env",  # server/.env
    Path(__file__).resolve().parents[2] / ".env",  # 프로젝트 루트/.env
]
for _env_path in _possible_env_paths:
    if _env_path.exists():
        load_dotenv(_env_path)
        break

from .routers import jwt_login, google, kakao, naver, comparison, users, bootcamper, search, skills, meta, jobposts, job_categories

app = FastAPI(title="MatchIT Backend")

# 개발용 CORS 설정
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://frontend:3000",
    "http://0.0.0.0:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jwt_login.router)
app.include_router(google.router)
app.include_router(kakao.router)
app.include_router(naver.router)
app.include_router(comparison.router)
app.include_router(users.router)
app.include_router(bootcamper.router)
app.include_router(jobposts.router)
app.include_router(search.router)
app.include_router(skills.router)
app.include_router(meta.router)
app.include_router(job_categories.router)

logger = logging.getLogger(__name__)


@app.on_event("startup")
def on_startup():
    # Wait for DB to be ready (simple retry loop). This prevents immediate
    # OperationalError when the DB container is still initializing.
    from src.database import engine
    max_retries = 10
    delay = 1  # seconds
    for attempt in range(1, max_retries + 1):
        try:
            with engine.connect():
                logger.info("DB connection established on startup (attempt %s)", attempt)
                return
        except Exception as e:
            logger.warning("DB connection attempt %s failed: %s", attempt, e)
            time.sleep(delay)
    logger.error("DB did not become ready after %s attempts", max_retries)

@app.get("/")
def root():
    return {"message": "MatchIT Backend is running"}
