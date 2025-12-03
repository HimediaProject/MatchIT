# 백엔드 Dockerfile - FastAPI + PostgreSQL 연결
FROM python:3.11-slim

# 작업 디렉토리 설정
# Set workdir
WORKDIR /app

# System dependencies: installing common build libs and dev headers
# - build-essential (gcc/g++/make)
# - libpq-dev (Postgres client libs for psycopg* / asyncpg builds)
# - libssl-dev / libffi-dev (often required by cryptography or other libraries)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libpq-dev \
    libssl-dev \
    libffi-dev \
    curl \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy only requirements first to take advantage of Docker layer caching
COPY requirements.txt ./

# Python 패키지 설치
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY . .

# static 디렉토리 생성 (이미지 저장용)
RUN mkdir -p static/images

# 포트 노출
EXPOSE 8000

# 환경변수 설정
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# 헬스체크 추가
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 애플리케이션 시작
# 실행 방법: uvicorn을 사용해 ASGI 앱을 노출
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
