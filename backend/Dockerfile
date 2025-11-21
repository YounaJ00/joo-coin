# Stage 1: Builder - 의존성 설치
FROM python:3.11-slim as builder

# 빌드 도구 설치 (C 확장 모듈 빌드용)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential \
        python3-dev \
        default-libmysqlclient-dev && \
    rm -rf /var/lib/apt/lists/*

# uv 설치
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# 작업 디렉토리 설정
WORKDIR /app

# Python 환경변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

# 의존성 파일 복사
COPY pyproject.toml uv.lock ./

# 의존성 설치 (가상환경에 설치)
RUN uv sync --frozen --no-dev

# Stage 2: Runtime - 실행 환경
FROM python:3.11-slim

# 런타임 라이브러리 설치 (C 확장 모듈 실행용)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libmariadb3 && \
    rm -rf /var/lib/apt/lists/*

# 작업 디렉토리 설정
WORKDIR /app

# Python 환경변수 설정
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# 비루트 사용자 생성
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# builder에서 가상환경 복사
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# 애플리케이션 코드 복사
COPY --chown=appuser:appuser . .

# 비루트 사용자로 전환
USER appuser

# 포트 노출
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health', timeout=5)"

# 애플리케이션 실행
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
