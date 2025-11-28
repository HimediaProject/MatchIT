from fastapi import APIRouter, \
                    Depends, \
                    Response, \
                    Request, \
                    HTTPException,\
                    Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse # 해당 페이지로 바로 이동 시켜줌
from sqlalchemy.orm import Session
from src.database import get_db
# from models import User
import uuid
from datetime import datetime
from jwt_token import create_token, create_refresh_token, verify_token

router = APIRouter(prefix='/jwt')

# 임시 데이터 저장 (나중에 DB로 대체)
fake_user = {
    'admin': '1234',
    'hj': '1234'
}
retoken = {}

@router.post('/login')
def login(response: Response,
        username: str = Form(...), 
        password: str = Form(...)):  # 아이디, 비밀번호 입력 받기, 쿠키에 저장시키기 위해서 response 객체 받기
    # 1. 사용자 로그인 정보 비교 
    if username not in fake_user or fake_user[username] != password: 
        # 1. DB에 없는 사용자면 로그인 거부, 로그인에 실패했다는 페이지 보여주기 또는 알림창
        raise HTTPException(status_code=401, detail='로그인 실패')  
    # 2. Access token을 발급
    access_token = create_token(username)
    
    # 3. Refresh token 발급 
    refresh_token = create_refresh_token(username)
    # refresh token을 서버에 저장 
    retoken[refresh_token] = {
        'username': username, 
        'created_at': datetime.now()
    }
    # 4. 프로필로 리다이렉트 또는 홈으로 가거나 (인증 절차 후 행동 결정)
    response = RedirectResponse(url='/jwt/profile', status_code=302) 
    # 5. 쿠키 토큰 저장 
    response.set_cookie(
        key='access_token',
        value=f'{access_token}',
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=60*1
    )
    response.set_cookie(
        key='refresh_token',
        value=f'{refresh_token}',
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=24*60*60*7
    )
    # 6. 응답 
    
    return response

@router.get('/refresh')
def refresh(response: Response,
            refresh_token: str = Cookie(None)): # 쿠키에서 refresh 토큰 가져오기 
    # 1. refresh token이 있는지 여부확인하고 
    if not refresh_token: 
        # 다시 로그인 해야한다고 홈으로 이동시키기 
        return RedirectResponse(url='/')
    # 2. 어떤 경우에 refresh token으로 재발급을 하지 않아도 문제가 되지 않을까?
    
    # 2.1 서버에 있는 refresh token과 일치하는지 확인 
    if refresh_token not in retoken:
        return RedirectResponse(url='/')

    # 2.2 refresh token 검증 
    payload, isvalid = verify_token(refresh_token)
    
    # 2.3 만료되었을 때 처리 
    if isvalid=='expired':
        # 서버에 있는 만료된 refresh token 제거 
        if refresh_token in retoken:
            del retoken[refresh_token]
        # 홈으로 가라
        return RedirectResponse(url='/')
    # 2.4 유효하지 않을 때 처리 
    if isvalid == 'invalid':
        # 홈으로 가라 
        return RedirectResponse(url='/')
    # 3. access token 재발급 
    new_access_token = create_token(payload)
    
    # 4. 쿠키에 새로 발급한 토큰 저장
    response = RedirectResponse(url='/jwt/profile', status_code=302)
    response.set_cookie(
        key='access_token',
        value=f"{str(new_access_token)}",
        httponly=True,
        max_age=10
    )
    
    # 5. 응답 -> 재발급 처리한 곳으로 보내기 
    return response
    
@router.post('/logout')
def logout(response: Response,
           refresh_token: str = Cookie(None)):
    # 서버, 쿠키에 있는 모든 토큰 삭제 

    # 서버에 refresh token 있는지 확인 후 삭제 
    if refresh_token and refresh_token in retoken:
        del retoken[refresh_token]
        
    # 쿠키 삭제 
    response.RedirectResponse(url='/', status_code=302)
    response.delete_cookie('access_token')
    response.delete_cookie('refresh_token')
    
    return response
    

@router.get('/profile', response_class=HTMLResponse)
def profile(access_token: str = Cookie(None),
            refresh_token: str = Cookie(None)): # request객체를 파라미터로 받거나, Cookie 클래스로 자동으로 받아 오거나
    # 1. 로그인 처리 X -> 쿠키에 access token 가져와서 인증된 사용자인지 확인
    # 1.1 access token 없으면 profile 리소스 접근 금지 
    if not access_token:
        return RedirectResponse(url='/')
    # access token 있을 때     
    # 2. 토큰 검증 (유효기간이 만료되었나, 시크릿 키로 검증이 가능한 유효한 토큰인가)
    payload, isvalid = verify_token(access_token)
    # 3. 토큰 유효하지 않을때 처리
    if isvalid == 'invalid':
        # 다시 로그인 유도
        return RedirectResponse(url='/') 
    
    # 4. 토큰 만료시 처리
    if isvalid == 'expired':
        if refresh_token:
            return RedirectResponse(url='/jwt/refresh', status_code=302)
        return RedirectResponse(url='/') 
    
    # 5. 성공 응답 (인증 완료) 프로필 페이지 HTML 응답
    return f"""
    <html>
        <body>
            <h1>프로필 페이지</h1>
            <p>{payload}</p>
        </body>
    </html>
    """
