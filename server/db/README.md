pgvector + PostgreSQL 18 설정 안내
==================================

이 디렉토리의 Dockerfile은 PostgreSQL 18에서 pgvector를 빌드하여 설치합니다. 주요 포인트:

- PostgreSQL 이미지 버전: `postgres:18` (Dockerfile에서 설정)
- pgvector: 저장소에서 소스를 내려받아 `make install`로 설치
- 데이터베이스 초기화 시 `server/db/init.sql`에 `CREATE EXTENSION IF NOT EXISTS vector;`를 추가해서 벡터 확장을 활성화

주의사항 (데이터 마이그레이션):

- Postgres의 메이저 버전(예: 15 → 16)을 변경하는 경우 기존 데이터 디렉토리는 호환되지 않습니다. 기존 데이터를 보존하려면 아래 절차 중 하나를 사용하세요:
  - (권장) 데이터 백업: `pg_dumpall` 또는 특정 DB 덤프 → 컨테이너 중지 → 볼륨 제거 → 새 컨테이너에서 복원
  - `pg_upgrade` 사용: 직접 이미지에서 실행하거나 별도 컨테이너에서 마이그레이션 수행
  - 개발용으로 데이터가 필요 없으면 볼륨 삭제 후 새로 생성

개발/실행 예시 (Windows cmd):
```
docker compose down
docker volume rm matchit_postgres_data
docker compose up --build -d
```

테스트 확인: `init.sql`이 실행되어 `matchit_db`에 `vector` 확장이 설치되었는지 확인하려면:
```
docker compose exec postgres psql -U postgres -d matchit_db -c "\dx" | findstr vector
```

이미지 사용 방법 및 빌드/푸시 예시:

- 로컬 빌드 후 태깅 및 푸시:
```
docker build -t himediaproject/matchit_postgres:18-pgvector ./server/db
docker push himediaproject/matchit_postgres:18-pgvector
```

- `docker-compose.yml`에서 `build` 대신 `image`만 사용하려면 다음처럼 설정하세요:
```
postgres:
  image: himediaproject/matchit_postgres:18-pgvector
  container_name: matchit_postgres
  # ... 나머지 설정
```

위처럼 하면 Registry에서 `himediaproject/matchit_postgres:18-pgvector` 이미지를 가져와 컨테이너를 실행합니다.

필요 시 백엔드에서 `pgvector` 패키지를 사용하려면 `server/requirements.txt`에 `pgvector`가 추가되어 있어야 합니다.
