from typing import List

import os
import httpx
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import select

from src.database import get_db
from src.models import JobPost, BootcampPost
from src.schemas import RecommendationRequest, RecommendationResponse, SimilarItem
from sentence_transformers import SentenceTransformer
from ai.ai_models import get_embedding_model

router = APIRouter(prefix="/recommendations", tags=["추천"])

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "google/gemma-3-27b-it:free")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1/chat/completions"


@router.post("/", response_model=RecommendationResponse)
async def recommend(request: RecommendationRequest,
                    db: Session = Depends(get_db),
                    model: SentenceTransformer = Depends(get_embedding_model)):
    if not OPENROUTER_API_KEY:
        raise HTTPException(status_code=500, detail="OpenRouter API 키가 설정되지 않았습니다.")

    query_embedding = model.encode(request.query).tolist()

    job_stmt = (
        select(
            JobPost.PostID,
            JobPost.Title,
            JobPost.Url,
            (1 - JobPost.Embedding.cosine_distance(query_embedding)).label("similarity"),
        )
        .where(JobPost.Embedding.isnot(None))
        .order_by(JobPost.Embedding.cosine_distance(query_embedding))
        .limit(request.top_k_jobs)
    )
    job_rows = db.execute(job_stmt).all()

    bootcamp_stmt = (
        select(
            BootcampPost.BootcampID,
            BootcampPost.Title,
            BootcampPost.DetailUrl,
            (1 - BootcampPost.Embedding.cosine_distance(query_embedding)).label("similarity"),
        )
        .where(BootcampPost.Embedding.isnot(None))
        .order_by(BootcampPost.Embedding.cosine_distance(query_embedding))
        .limit(request.top_k_bootcamps)
    )
    bootcamp_rows = db.execute(bootcamp_stmt).all()

    items: List[SimilarItem] = []

    for row in job_rows:
        items.append(
            SimilarItem(
                id=row.PostID,
                source="job",
                title=row.Title,
                description=None,
                url=row.Url,
                similarity=float(row.similarity),
            )
        )

    for row in bootcamp_rows:
        items.append(
            SimilarItem(
                id=row.BootcampID,
                source="bootcamp",
                title=row.Title,
                description=None,
                url=row.DetailUrl,
                similarity=float(row.similarity),
            )
        )

    items.sort(key=lambda x: x.similarity, reverse=True)

    if not items:
        return RecommendationResponse(items=[], llm_message="관련된 채용공고나 부트캠프를 찾지 못했습니다.")

    context_lines = []
    for item in items:
        prefix = "[채용]" if item.source == "job" else "[부트캠프]"
        line = f"{prefix} 제목: {item.title} (유사도: {item.similarity:.3f})"
        if item.url:
            line += f"\n  링크: {item.url}"
        context_lines.append(line)

    context_text = "\n".join(context_lines)

    prompt_system = {
        "role": "system",
        "content": (
            "당신은 커리어 추천 도우미입니다. "
            "아래에 제공된 채용공고와 부트캠프 후보 리스트는 모두 이 서비스(우리 사이트)의 데이터입니다. "
            "사용자 입력과 이 후보 리스트만을 참고하여, 사용자에게 적합해 보이는 채용공고와 부트캠프를 한국어로 친절하게 요약해서 추천해주세요. "
            "반드시 리스트에 있는 항목만 사용하고, 각 항목을 간단히 설명하면서 왜 추천하는지도 함께 알려주세요. "
            "원티드, 사람인, 잡코리아 등 다른 채용 플랫폼이나 외부 사이트는 언급하거나 추천하지 마세요."
        ),
    }

    prompt_user = {
        "role": "user",
        "content": (
            f"사용자 입력: {request.query}\n\n"
            f"후보 리스트:\n{context_text}"
        ),
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        response = await client.post(
            OPENROUTER_BASE_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": OPENROUTER_MODEL,
                "messages": [prompt_system, prompt_user],
                "temperature": 0.7,
                "max_tokens": 800,
            },
        )

        response.raise_for_status()
        data = response.json()

        if "choices" in data and len(data["choices"]) > 0:
            llm_message = data["choices"][0]["message"]["content"]
        else:
            llm_message = None

    return RecommendationResponse(items=items, llm_message=llm_message)
