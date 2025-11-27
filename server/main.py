import uvicorn
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True, # 쿠키 포함 허용
    allow_methods=["*"], # 모든 method 허용 
    allow_headers=["*"]
)

@app.get('/', response_class=HTMLResponse)
def home():
    return"""
    <html>
        <body>
            <div>
                <h3>카카오 로그인</h3>
                <a href='/auth/kakao/login'>
                    <img src='images/kakao_login.png'
                    alt='카카오 로그인' style='width: 123px; cursor: pointer;'></img>
                </a>
            </div>
        </body>
    </html>
    """

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1",
                port=8000, reload=True)