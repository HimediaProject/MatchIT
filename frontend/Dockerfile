# 개발 환경용 Dockerfile
FROM node:18-alpine

WORKDIR /app

# 환경 변수 설정
ENV NODE_ENV=development
ENV CHOKIDAR_USEPOLLING=true
ENV WDS_SOCKET_PORT=0

# 패키지 파일 복사
COPY package*.json ./

# 의존성 설치 (개발 의존성 포함)
RUN npm install

# 소스 코드 복사
COPY . .

# 개발 서버 실행 (포트 3000)
EXPOSE 3000

# 헬스 체크
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD wget --quiet --tries=1 --spider http://localhost:3000/ || exit 1

# 개발 서버 실행
CMD ["npm", "start"]
