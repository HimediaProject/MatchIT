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
docker-compose up client -d
```