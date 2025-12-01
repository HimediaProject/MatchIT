import os
import httpx
from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse, HTMLResponse
from sqlalchemy.orm import Session
from src.database import get_db
from datetime import datetime, timedelta
from src.models import User, SocialLogin

ENV_PATH = Path(__file__).parent.parent.parent / '.env'    # .env 절대 경로
print("####",ENV_PATH)
load_dotenv(ENV_PATH)   # 인자: .env 경로

KAKAO_CLIENT_ID = os.getenv('KAKAO_CLIENT_ID')
KAKAO_CLIENT_SECRET = os.getenv('KAKAO_CLIENT_SECRET')
KAKAO_REDIRECT_URI = os.getenv('KAKAO_REDIRECT_URI')

router = APIRouter(prefix='/auth/kakao', tags=['카카오'])

@router.get('/login')
async def kakao_login():
    """
    사용자에게 카카오 로그인 허용 요청을 하는 엔드포인트
    """

    # 1. 카카오 서버에 로그인 허용 요청
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?response_type=code"                 # 응답으로 인가 코드 요청 (엑세스 토큰으로 교환하기 위한 코드)
        f"&client_id={KAKAO_CLIENT_ID}"
        f'&redirect_uri={KAKAO_REDIRECT_URI}'
    )
    print("####",KAKAO_REDIRECT_URI)
    # 2. 엑세스 토근을 발급받을 수 있도록 요청하는 FastAPI의 엔드포인트로 redirect
    return RedirectResponse(url=kakao_auth_url)

# 인증 코드를 받아서 엑세스 토큰으로 교환해주는 엔드포인트
@router.get('/callback')
async def kakao_callback(code: str,
                         db: Session = Depends(get_db)): # 인증코드 code, 데이터베이스 연결 객체
    
    # 1. 엑세스 토큰으로 교환하기 위한 요청

    # 1-1. 토큰 요청 URL & 토큰 교환에 필요한 데이터를 준비
    token_url = "https://kauth.kakao.com/oauth/token"

    token_data = {
        "grant_type": 'authorization_code',
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "client_secret": KAKAO_CLIENT_SECRET,
        "code": code
    }

    # 2. post 요청으로 토큰 교환 api 요청
    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
    
    # 2-1. 토큰 응답 파싱 (값을 가져올 때)
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    refresh_token = token_json.get('refresh_token')
    expires_in = token_json.get('expires_in', 60*60*6)                  # 만료시간 -> 카카오가 정해준 만료시간을 따라야 함 6시간
    token_expired_at = datetime.now() + timedelta(seconds=expires_in)   # 현재 시간을 기준으로 설정한 만료시간

    # 만약 토큰 응답을 못했을 때
    if not access_token:
        return {'error': '토큰 발급 실패', 'details': token_json}

    # 3. 엑세스 토큰으로 사용자 정보 가져오기
    user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {'Authorization': f"Bearer {access_token}"}   # 토큰으로 인증 요청을 할 때 표준으로 사용하는 방식

    async with httpx.AsyncClient() as Client:
        user_response = await Client.get(user_info_url, headers=headers)
    
    # 사용자 응답에서 사용자 정보 파싱
    user_json = user_response.json()

    kakao_id = user_json.get('id')
    kakao_email = user_json.get('kakao_account', {}).get('email', 'email')
    kakao_nickname = user_json.get('properties', {}).get('nickname', 'nickname')
    kakao_gender = user_json.get('kakao_account', {}).get('gender', 'gender')
    kakao_thumnail = user_json.get('properties', {}).get('thumnail_image', 'image.png')

    # 4. 우리 서버에 사용자 정보를 저장시키기
    oauth_account = db.query(SocialLogin)\
                      .filter(SocialLogin.provider == 'kakao',\
                              SocialLogin.provider_user_id == str(kakao_id)).first()
    
    # 4-1. 존재하면 저장 X -> 엑세스 토큰, 리프레시 토큰 업데이트
    if oauth_account:
        try:
            oauth_account.refresh_token = refresh_token
            oauth_account.token_expired_at = token_expired_at

            # 변경사항 저장
            db.commit()
            user = oauth_account.user
        except Exception as e:
            db.rollback()
            return {'error': '로그인 실패', 'details': str(e)}
         
    # 4-2. 우리 서버에 있는 사용자인가 확인하고 존재하지 않으면 저장
    else:
        try:
            user = User(
                email = kakao_email,
                name = kakao_nickname,
                login_type = 'oauth',
                password = None
            )

            db.add(user)
            db.commit() # 확정
            db.flush()  # user 테이블에 저장하면서 user의 id를 가져오기 위해서

            oauth_account = SocialLogin(
                user_id = user.id,
                provider = 'kakao',
                provider_user_id = str(kakao_id),    # 문자열로 바꿔서 저장
                refresh_token = refresh_token,
                token_expired_at = token_expired_at
            )

            db.add(oauth_account)
            db.commit()

        except Exception as e:
            db.rollback()
            return {'error': '회원가입 실패', 'details': str(e)}
    
    db.refresh(user)    # 응답 페이지에 사용자 정보를 표시하기 위해 새로고침

    # 5. 쿠키에 토큰 저장하기
    html_content = f"""
                    <!DOCTYPE html>
                    <html>
                        <body>
                            <h3>성공</h3>
                            <span>이름: {user.name}</span>
                            <span>이메일: {user.email}</span>
                            <span>성별: {kakao_gender}</span>
                            <br>
                            <a href="/auth/kakao/logout?user_id={user.id}">로그아웃</a>
                            <br>
                            <a href='/'>홈으로</a>
                        </body>
                    </html>
                    """
    response = HTMLResponse(html_content)

    # access_token
    response.set_cookie(
        key = 'kakao_access_token',
        value = access_token,
        max_age = expires_in,
        httponly = True,
        secure = False,
        samesite = 'lax'
    )

    # refresh_token
    response.set_cookie(
        key = 'kakao_refresh_token',
        value = refresh_token,
        max_age = 60*60*24*30,
        httponly = True,
        secure = False,
        samesite = 'lax'
    )

    # 6. 응답
    return response