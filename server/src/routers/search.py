from fastapi import APIRouter
import logging

router = APIRouter(prefix="/search", tags=["검색 기능"])

logger = logging.getLogger(__name__)