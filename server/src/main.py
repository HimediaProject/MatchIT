from fastapi import FastAPI
import time
import logging
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from .routers import jwt_login, google, kakao, naver, comparison, users, users_test, bootcamper, search, skills, meta, jobposts

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
    allow_origins=["*"],
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
app.include_router(users_test.router)
app.include_router(bootcamper.router)
app.include_router(jobposts.router)
app.include_router(search.router)
app.include_router(skills.router)
app.include_router(meta.router)

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

# 로그인 페이지
@app.get('/login', response_class=HTMLResponse)
def login():
    return"""
    <html>
        <body>
            <div>
                <h3>구글 로그인</h3>
                <a href='/auth/google'>
                    <img src='images/google_login.png'
                    alt='구글 로그인' style='width: 123px; cursor: pointer;'></img>
                </a>
            </div>
            <div>
                <h3>카카오 로그인</h3>
                <a href='/auth/kakao'>
                    <img src='images/kakao_login.png'
                    alt='카카오 로그인' style='width: 123px; cursor: pointer;'></img>
                </a>
            </div>
            <div>
                <h3>네이버 로그인</h3>
                <a href='/auth/naver'>
                    <img src='images/naver_login.png'
                    alt='네이버 로그인' style='width: 123px; cursor: pointer;'></img>
                </a>
            </div>
        </body>
    </html>
    """

@app.get("/auth/kakao/callback")
async def kakao_callback(code: str | None = None, error: str | None = None):
    print("kakao_callback:", code, error)
