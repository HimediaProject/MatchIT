### 🚀 프로젝트 초기 설정
#### 환경 변수 설정
```bash
# 환경 변수 파일 복사 (프로젝트 루트에서)
cp env.example .env

# .env 파일 편집 (텍스트 에디터 사용)
# Windows: notepad .env
# macOS: open -e .env
# Linux: nano .env 또는 vim .env
```

### 🐳 Docker를 사용한 실행 (권장)

#### 1. Docker 컨테이너 빌드
```bash
# 프로젝트 루트 디렉토리에서
npm run docker:build

# 또는 직접 실행
docker-compose build
```

#### 2. 컨테이너 실행
```bash
# 백그라운드에서 실행
npm run docker:up

# 또는 직접 실행
docker-compose up -d
```

#### 3. 실행 상태 확인
```bash
# 컨테이너 상태 확인
docker-compose ps

# 로그 확인
npm run docker:logs

# 또는 직접 확인
docker-compose logs -f
```

#### 4. 개별 서비스 실행 (선택사항)
```bash
# 데이터베이스만 실행
docker-compose up postgres mongodb redis rabbitmq -d

# 백엔드만 실행
docker-compose up server -d

# 프론트엔드만 실행
docker-compose up frontend -d
```

#### 5. 컨테이너 정리
```bash
# 컨테이너 중지 및 제거, 네트워크도 함께 삭제
docker-compose down

# 2. 컨테이너, 네트워크, 그리고 데이터 볼륨까지 삭제
docker-compose down -v
```

#### 6. 컨테이너 재시작
```bash
# 실행 중인 컨테이너 재시작
docker-compose restart server
docker-compose restart fontend
```

### 🐳 Docker를 사용한 alembic 방법 (# upgrade에 있는 sh -c cd src && 도 추가)
#### 1. DB 시작
```bash
docker compose up -d
```

#### 2. 컨테이너에서 Alembic 초기화:
```bash
docker compose run --rm server alembic init alembic
```

#### 3. 마이그레이션 파일 생성
```bash
docker compose run --rm server alembic revision --autogenerate -m "create table"
```

#### 4. 마이그레이션 실행
```bash
# Upgrade (적용): 
docker compose run --rm server sh -c "cd src && alembic upgrade head"

# py파일 Upgrade (적용): 
docker compose run --rm server sh -c "cd data && python 8_import_preprocessed_to_db.py"

# Upgrade 특정 버전: 
docker compose run --rm server alembic upgrade +1 또는 alembic upgrade xxxx

#Downgrade (롤백): 
docker compose run --rm server alembic downgrade -1

#현재 상태 확인: 
docker compose run --rm server alembic current

#히스토리 확인: 
docker compose run --rm server alembic history
```

### 🐳 docker volume 삭제 후 다시 생성하면 pg admin에서 server 생성하는 방법
#### 1. Servers 우클릭 > create > Server Group > name: (아무거나 상관 없음) > save
#### 2. 생성한 server group 우클릭 > Register > Server > name: (아무거나 상관 없음)
#### 3. Connection > Host name/address: matchit_postgres > password: password > save password 체크 후 save