from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from .routers import jwt_login, kakao 

app = FastAPI(title="MatchIT Backend")

# 개발용 CORS 설정
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(jwt_login.router)
app.include_router(kakao.router)

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
