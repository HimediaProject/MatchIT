import os
import httpx
import uuid
from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter, Depends, Cookie, Response, Request
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from sqlalchemy.orm import Session
from src.database import get_db
from datetime import datetime, timedelta
from src.models import User, SocialLogin, UserSession
from typing import Optional

ENV_PATH = Path(__file__).parent.parent.parent / '.env'    
load_dotenv(ENV_PATH)

KAKAO_CLIENT_ID = os.getenv('KAKAO_CLIENT_ID')
KAKAO_CLIENT_SECRET = os.getenv('KAKAO_CLIENT_SECRET')
KAKAO_REDIRECT_URI = os.getenv('KAKAO_REDIRECT_URI')
FRONTEND_URL = os.getenv('FRONTEND_URL', 'http://localhost:3000') # Docker 환경 변수 주의

router = APIRouter(prefix='/auth/kakao', tags=['카카오 소셜로그인 기능'])

@router.get('/login')
async def kakao_login():
    """카카오 로그인 페이지로 리다이렉트"""
    kakao_auth_url = (
        f"https://kauth.kakao.com/oauth/authorize"
        f"?response_type=code"
        f"&client_id={KAKAO_CLIENT_ID}"
        f'&redirect_uri={KAKAO_REDIRECT_URI}'
    )
    return RedirectResponse(url=kakao_auth_url)

@router.get('/callback')
async def kakao_callback(code: str, db: Session = Depends(get_db)): 
    
    # 1. 토큰 교환
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        "grant_type": 'authorization_code',
        "client_id": KAKAO_CLIENT_ID,
        "redirect_uri": KAKAO_REDIRECT_URI,
        "client_secret": KAKAO_CLIENT_SECRET,
        "code": code
    }

    async with httpx.AsyncClient() as client:
        token_response = await client.post(token_url, data=token_data)
    
    token_json = token_response.json()
    access_token = token_json.get('access_token')
    refresh_token = token_json.get('refresh_token')
    expires_in = token_json.get('expires_in', 60*60*6)

    if not access_token:
        return JSONResponse(status_code=400, content={'error': '토큰 발급 실패', 'details': token_json})

    # 2. 사용자 정보 가져오기
    user_info_url = "https://kapi.kakao.com/v2/user/me"
    headers = {'Authorization': f"Bearer {access_token}"}

    async with httpx.AsyncClient() as Client:
        user_response = await Client.get(user_info_url, headers=headers)
    
    user_json = user_response.json()
    kakao_id = user_json.get('id')
    kakao_account = user_json.get('kakao_account', {})
    kakao_email = kakao_account.get('email')
    kakao_nickname = user_json.get('properties', {}).get('nickname', 'Unknown')
    kakao_gender = kakao_account.get('gender')

    # 3. [요구사항: DB 저장] 회원가입 및 로그인 처리
    try:
        # 3-1. 소셜 계정 확인
        oauth_account = db.query(SocialLogin)\
            .filter(SocialLogin.Provider == 'Kakao', SocialLogin.ProviderUserID == str(kakao_id))\
            .first()
        
        user = None
        newly_created = False
        if oauth_account:
            # 이미 가입된 계정 -> 재연결 처리
            oauth_account.UnlinkedAt = None
            user = oauth_account.user # 관계 설정된 User 객체 가져오기
        else:
            # 신규 가입
            # 이메일 중복 체크 (소셜로그인이 아닌 일반 가입이 있을 수 있으므로)
            if kakao_email:
                user = db.query(User).filter(User.Email == kakao_email).first()
            
            if not user:
                user = User(
                    Email = kakao_email if kakao_email else f"kakao_{kakao_id}@no-email.com", # 이메일 없을 경우 대비
                    Name = kakao_nickname
                )
                db.add(user)
                db.flush() # UserID 생성
                newly_created = True

            new_oauth = SocialLogin(
                UserID = user.UserID,
                Provider = 'Kakao',
                ProviderUserID = str(kakao_id),
                LinkedAt = datetime.now(),
                UnlinkedAt = None
            )
            db.add(new_oauth)
        
        db.commit()
        db.refresh(user)

    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={'error': 'DB 처리 실패', 'details': str(e)})

    # 4. [요구사항: 세션 DB 저장] UserSessions 테이블에 세션 정보 저장
    try:
        session_id = uuid.uuid4()
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        user_session = UserSession(
            SessionID=session_id,
            UserID=user.UserID,
            AccessToken=access_token,
            RefreshToken=refresh_token,
            ExpiresAt=expires_at
        )
        db.add(user_session)
        db.commit()
    except Exception as e:
        db.rollback()
        return JSONResponse(status_code=500, content={'error': '세션 저장 실패', 'details': str(e)})

    # 4. [요구사항: 세션 저장] 쿠키 설정 및 프론트엔드 이동
    # HTML 응답 생성 (프론트엔드 리다이렉트용)
    # 신규 가입인 경우만 팝업을 띄우고, 기존 사용자는 바로 프로필 페이지로 이동합니다.
    if newly_created:
        html_content = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <script>
                    // 1. 로컬 스토리지에 플래그 설정 (프론트엔드 UI 즉시 반영용)
                    try {{ localStorage.setItem('isLogin', 'true'); }} catch(e){{}}
                    // 2. 회원가입 완료 팝업
                    alert('회원가입 완료되었습니다.');
                    // 3. 프로필 페이지로 이동
                    window.location.href = '{FRONTEND_URL}/profile';
                </script>
            </head>
            <body></body>
        </html>
        """
    else:
        # 기존 사용자는 팝업 없이 바로 이동
        html_content = f"""
        <!DOCTYPE html>
        <html>
            <head>
                <script>
                    // 1. 로컬 스토리지에 플래그 설정
                    try {{ localStorage.setItem('isLogin', 'true'); }} catch(e){{}}
                    // 2. 바로 프로필 페이지로 이동 (팝업 없음)
                    window.location.href = '{FRONTEND_URL}/profile';
                </script>
            </head>
            <body></body>
        </html>
        """
    response = HTMLResponse(html_content)

    # 쿠키 보안 설정 (Docker/배포 환경 고려)
    # Secure=False는 로컬 개발용(http), https 적용 시 True로 변경 필요
    cookie_options = {
        "httponly": True,  # 자바스크립트 접근 불가 (보안)
        "secure": False,   # HTTPS가 아니면 False (로컬 Docker 환경)
        "samesite": "lax",
        "path": "/"
    }

    # 핵심 인증 정보 (HttpOnly)
    # SessionID 쿠키 추가 (DB에 저장된 세션 ID 참조)
    response.set_cookie(key='session_id', value=str(session_id), max_age=60*60*24*30, **cookie_options)
    response.set_cookie(key='user_id', value=str(user.UserID), max_age=60*60*24*30, **cookie_options)
    response.set_cookie(key='kakao_access_token', value=access_token, max_age=expires_in, **cookie_options)
    response.set_cookie(key='kakao_refresh_token', value=refresh_token, max_age=60*60*24*30, **cookie_options)
    
    # UI 제어용 비보안 쿠키 (자바스크립트 접근 가능 -> 버튼 변경용)
    response.set_cookie(
        key='is_login', 
        value='true', 
        httponly=False, # JS에서 document.cookie로 읽을 수 있음
        secure=False, 
        samesite="lax",
        path='/'
    )

    return response


# [요구사항: 로그인/로그아웃 버튼 변경]을 위한 상태 확인 API
@router.get('/me')
async def get_current_user(
    # Query Parameter가 아니라 Cookie에서 user_id를 읽어옵니다.
    user_id: Optional[str] = Cookie(None), 
    db: Session = Depends(get_db)
):
    """
    프론트엔드가 이 API를 호출하여 로그인 상태를 확인하고
    로그인 상태면 '로그아웃' 버튼을, 아니면 '로그인' 버튼을 렌더링합니다.
    """
    if not user_id:
        return {'isLoggedIn': False, 'user': None}
    
    try:
        user = db.query(User).filter(User.UserID == int(user_id)).first()
        if not user:
            return {'isLoggedIn': False, 'user': None}
        
        return {
            'isLoggedIn': True,
            'user': {
                'id': user.UserID,
                'name': user.Name,
                'email': user.Email
            }
        }
    except Exception:
        return {'isLoggedIn': False, 'user': None}


@router.get('/logout')
async def kakao_logout(
    request: Request,
    session_id: Optional[str] = Cookie(None),  # 세션 ID
    user_id: Optional[str] = Cookie(None), # 쿠키에서 자동 추출
    db: Session = Depends(get_db)
):
    # 기본적으로는 이동 및 alert을 제공하는 HTML 응답을 반환합니다.
    # 그러나 AJAX/Fetch 요청으로 호출되는 경우 JSON 응답을 반환합니다.

    # 쿠키 삭제를 위한 응답 객체 선택
    accept_header = request.headers.get('accept', '')

    # 공통적으로 삭제할 쿠키들 (path를 명시)
    def clear_cookies(resp):
        resp.delete_cookie('session_id', path='/')
        resp.delete_cookie('user_id', path='/')
        resp.delete_cookie('kakao_access_token', path='/')
        resp.delete_cookie('kakao_refresh_token', path='/')
        resp.delete_cookie('is_login', path='/')
        return resp

    # DB에서 세션 삭제 및 UnlinkedAt 업데이트
    if session_id:
        try:
            # 세션 삭제
            db.query(UserSession).filter(UserSession.SessionID == session_id).delete()
            db.commit()
        except:
            db.rollback()
    
    if user_id:
        try:
            oauth_accounts = db.query(SocialLogin)\
                .filter(SocialLogin.UserID == int(user_id), SocialLogin.Provider == 'Kakao')\
                .all()
            for account in oauth_accounts:
                account.UnlinkedAt = datetime.now()
            db.commit()
        except:
            pass # 로그아웃은 DB 에러가 나도 사용자 입장에선 진행되어야 함

    # JSON 요청 (대부분 AJAX) -> JSONResponse
    if 'application/json' in accept_header or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        resp = JSONResponse({'ok': True, 'message': '로그아웃 되었습니다.'})
        clear_cookies(resp)
        return resp

    # 브라우저 직접 접근 -> HTML + JS로 로컬스토리지 삭제 후 리다이렉트
    html = f"""
        <script>
            try {{ localStorage.removeItem('isLogin'); }} catch(e){{}}
            alert('로그아웃 되었습니다.');
            window.location.href = '{FRONTEND_URL}';
        </script>
    """
    resp = HTMLResponse(html)
    clear_cookies(resp)
    return resp