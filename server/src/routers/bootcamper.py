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
from typing import List, Dict, Tuple, Union, Optional

router = APIRouter(prefix = '/bootcamps')

@router.post('/')
def get_list(size,
             page: int = 1,
             keyword: str = Form(...),
             skill: str = Form(...),
             category_id: int =
            ):

get_db