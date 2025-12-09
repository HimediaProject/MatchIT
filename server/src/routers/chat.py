import os
import httpx
import logging
from pathlib import Path
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional

ENV_PATH = Path(__file__).parent.parent.parent / '.env'
load_dotenv(ENV_PATH)

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemma-3-27b-it:free")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"

router = APIRouter(prefix="/chat", tags=["챗봇 기능"])
logger = logging.getLogger(__name__)


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant" or "system"
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    model: Optional[str] = None  # 기본값은 환경변수에서 가져옴


class ChatResponse(BaseModel):
    message: str
    model: str


@router.post("/", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    OpenRouter API를 사용하여 챗봇과 대화합니다.
    
    요청:
    - messages: 대화 메시지 배열 (role: "user" 또는 "assistant", content: 메시지 내용)
    - model: 사용할 모델 (선택적, 기본값: google/gemma-3-27b-it:free)
    
    응답:
    - message: 챗봇의 응답 메시지
    - model: 사용된 모델명
    """
    if not OPENROUTER_API_KEY:
        logger.error("OPENROUTER_API_KEY가 설정되지 않았습니다.")
        raise HTTPException(
            status_code=500,
            detail="OpenRouter API 키가 설정되지 않았습니다. 환경변수를 확인해주세요."
        )
    
    # 사용할 모델 결정 (요청에서 오면 사용, 아니면 환경변수 기본값)
    model = request.model or OPENROUTER_MODEL
    
    # OpenRouter API 요청 형식에 맞게 메시지 변환
    openrouter_messages = [
        {"role": msg.role, "content": msg.content}
        for msg in request.messages
    ]
    
    # 시스템 프롬프트 추가 (한국어 챗봇으로 설정)
    system_prompt = {
        "role": "system",
        "content": "당신은 친절하고 도움이 되는 AI 어시스턴트입니다. 사용자의 질문에 한국어로 명확하고 정확하게 답변해주세요."
    }
    
    # 시스템 메시지가 없으면 맨 앞에 추가
    if not any(msg.get("role") == "system" for msg in openrouter_messages):
        openrouter_messages.insert(0, system_prompt)
    
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                OPENROUTER_BASE_URL,
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": os.getenv("FRONTEND_URL", "http://localhost:3000"),  # 선택적
                    "X-Title": "MatchIT Chatbot",  # 선택적
                },
                json={
                    "model": model,
                    "messages": openrouter_messages,
                    "temperature": 0.7,
                    "max_tokens": 1000,
                }
            )
            
            response.raise_for_status()
            data = response.json()
            
            # OpenRouter 응답에서 메시지 추출
            if "choices" in data and len(data["choices"]) > 0:
                assistant_message = data["choices"][0]["message"]["content"]
                return ChatResponse(
                    message=assistant_message,
                    model=data.get("model", model)
                )
            else:
                logger.error(f"OpenRouter 응답 형식 오류: {data}")
                raise HTTPException(
                    status_code=500,
                    detail="OpenRouter API 응답 형식이 올바르지 않습니다."
                )
                
    except httpx.HTTPStatusError as e:
        logger.error(f"OpenRouter API HTTP 오류: {e.response.status_code} - {e.response.text}")
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"OpenRouter API 오류: {e.response.text}"
        )
    except httpx.TimeoutException:
        logger.error("OpenRouter API 요청 시간 초과")
        raise HTTPException(
            status_code=504,
            detail="OpenRouter API 요청 시간이 초과되었습니다."
        )
    except Exception as e:
        logger.exception(f"챗봇 요청 처리 중 오류 발생: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"챗봇 요청 처리 중 오류가 발생했습니다: {str(e)}"
        )


@router.get("/health")
async def chat_health():
    """
    챗봇 서비스 상태 확인
    """
    return {
        "status": "ok",
        "api_key_configured": bool(OPENROUTER_API_KEY),
        "default_model": OPENROUTER_MODEL
    }

