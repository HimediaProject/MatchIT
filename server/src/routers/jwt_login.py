from fastapi import APIRouter, \
                    Depends, \
                    Response, \
                    Request, \
                    HTTPException,\
                    Form, Cookie
from fastapi.responses import HTMLResponse, RedirectResponse # 해당 페이지로 바로 이동 시켜줌
from sqlalchemy.orm import Session
from datetime import datetime

from src.database import get_db
from src.jwt_token import create_token, create_refresh_token, verify_token
from src.models import User

router = APIRouter(prefix='/jwt')

retoken = {}

@router.post('/login')
def login(
    response: Response,
    username: str = Form(...), 
    password: str = Form(...),
    db: Session = Depends(get_db)
):  # 아이디, 비밀번호 입력 받기, 쿠키에 저장시키기 위해서 response 객체 받기
    
    # 1. 사용자 조회 
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=401, detail="존재하지 않는 사용자")  
    
    if user.password != password:
        raise HTTPException(status_code=401, detail="비밀번호 오류")
    
    # 2. JWT 토큰 생성
    user_info = {
        "user_id": user.UserID,
        "email": user.Email,
        "role": user.role.Name.lower()
    }

    # 3. 토큰 생성
    access_token = create_token(user_info)
    refresh_token = create_refresh_token(user_info)

    # refresh token을 서버에 저장 
    retoken[refresh_token] = {
        "user_id": user.UserID,
        'created_at': datetime.now()
    }

    # 4. 쿠키 저장
    response = RedirectResponse(url='/jwt/profile', status_code=302) 

    response.set_cookie(
        key='access_token',
        value=access_token,
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=60*30,
    )
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite='lax',
        max_age=24*60*60*7
    )

    # 5. 응답 
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
