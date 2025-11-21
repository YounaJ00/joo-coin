# JOO-COIN Backend

암호화폐 자동 거래 시스템 백엔드 API

## 목차

- [프로젝트 개요](#프로젝트-개요)
- [기술 스택](#기술-스택)
- [프로젝트 구조](#프로젝트-구조)
- [모듈별 상세 설명](#모듈별-상세-설명)
- [API 명세](#api-명세)
- [데이터베이스 스키마](#데이터베이스-스키마)
- [자동 거래 시스템](#자동-거래-시스템)
- [설치 및 실행](#설치-및-실행)
- [환경변수](#환경변수)

---

## 프로젝트 개요

JOO-COIN Backend는 Upbit 거래소와 OpenAI를 활용한 암호화폐 자동 거래 시스템입니다.

**주요 기능:**
- AI 기반 거래 의사결정 (OpenAI GPT)
- Upbit API를 통한 자동 매수/매도
- 거래 내역 관리 및 조회
- 5분 주기 자동 거래 스케줄러
- Cursor 기반 페이지네이션

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| Framework | FastAPI |
| Server | Uvicorn (ASGI) |
| ORM | SQLAlchemy 2.0+ |
| Database | MySQL |
| Migration | Alembic |
| Scheduler | APScheduler |
| AI | OpenAI API |
| Exchange | Upbit API (pyupbit) |
| Formatter | Ruff |
| Package Manager | uv |

---

## 프로젝트 구조

```
app/
├── ai/                      # AI 분석 모듈
│   ├── client/
│   │   └── open_ai_client.py    # OpenAI API 클라이언트
│   ├── const/
│   │   └── constans.py          # AI 프롬프트 상수
│   └── dto/
│       └── ai_analysis_response.py  # AI 응답 DTO
│
├── ballance/                # 잔고 관리 모듈
│   ├── model/
│   │   └── balance.py           # Balance 엔티티
│   └── repository/
│       └── balance_repository.py
│
├── coin/                    # 코인 관리 모듈
│   ├── controller/
│   │   └── my_coin_controller.py  # 코인 API 라우터
│   ├── dto/
│   │   └── coin_dto.py          # 코인 DTO
│   ├── model/
│   │   └── coin.py              # Coin 엔티티
│   ├── repository/
│   │   └── coin_repository.py
│   └── service/
│       └── coin_service.py      # 코인 비즈니스 로직
│
├── common/                  # 공통 모듈
│   ├── api/v1/
│   │   └── v1_router.py         # API v1 라우터 통합
│   ├── model/
│   │   └── base.py              # Base 모델
│   └── repository/
│       └── base_repository.py   # 제네릭 CRUD Repository
│
├── configs/                 # 설정
│   ├── app.py                   # FastAPI 앱 설정, 스케줄러
│   └── config.py                # 환경변수 설정
│
├── trade/                   # 거래 모듈
│   ├── controller/
│   │   └── trade_controller.py  # 거래 API 라우터
│   ├── dto/
│   │   └── transaction_response.py  # 거래 DTO
│   ├── model/
│   │   ├── enums.py             # TradeType, RiskLevel, TradeStatus
│   │   └── trade.py             # Trade 엔티티
│   ├── repository/
│   │   └── trade_repository.py
│   └── service/
│       └── trade_service.py     # 거래 비즈니스 로직
│
├── upbit/                   # Upbit API 통합
│   ├── client/
│   │   └── upbit_client.py      # Upbit API 클라이언트
│   ├── controller/
│   │   └── upbit_controller.py  # Upbit API 라우터
│   ├── di/
│   │   └── upbit_di.py          # 의존성 주입
│   └── dto/
│       ├── coin_balance.py
│       ├── my_ballance_response.py
│       └── ohlcv_dto.py
│
└── main.py                  # 애플리케이션 진입점
```

---

## 모듈별 상세 설명

### AI 모듈 (`app/ai/`)

**OpenAIClient** (`app/ai/client/open_ai_client.py`)

OHLCV 데이터를 분석하여 거래 의사결정을 제공합니다.

```python
async def get_bitcoin_trading_decision(df: pd.DataFrame) -> AiAnalysisResponse
```

**응답 형식:**
```json
{
  "decision": "buy/sell/hold",
  "confidence": 0.88,
  "reason": "기술적 분석 근거",
  "risk_level": "none/low/medium/high",
  "timestamp": "2025-11-22T10:30:00+09:00"
}
```

---

### Coin 모듈 (`app/coin/`)

**CoinService** (`app/coin/service/coin_service.py`)

| 메서드 | 설명 |
|--------|------|
| `get_all_active()` | 활성화된 거래 코인 목록 조회 |
| `create_coin(name)` | 코인 생성 또는 soft delete된 코인 복구 |
| `delete_coin(coin_id)` | 코인 soft delete (잔고 확인 후 삭제) |

**삭제 제약조건:** 코인 삭제 시 Upbit 잔고를 확인하여 잔고가 남아있으면 삭제 불가

---

### Trade 모듈 (`app/trade/`)

**TradeService** (`app/trade/service/trade_service.py`)

| 메서드 | 설명 |
|--------|------|
| `execute()` | 모든 활성 코인에 대해 AI 분석 후 자동 거래 실행 |
| `get_transactions(cursor, limit)` | 거래 내역 조회 (Cursor 기반 페이지네이션) |

**거래 실행 흐름:**
1. 활성화된 모든 코인 조회
2. 현재 KRW 잔고 확인
3. 각 코인별 OHLCV 데이터 조회 및 AI 분석
4. BUY/SELL/HOLD 결정에 따라 거래 실행
5. 거래 결과 DB 저장
6. 최종 잔고 기록

---

### Upbit 모듈 (`app/upbit/`)

**UpbitClient** (`app/upbit/client/upbit_client.py`)

| 메서드 | 설명 |
|--------|------|
| `get_ohlcv(coin_name)` | OHLCV 데이터 조회 (DTO 반환) |
| `get_ohlcv_raw(coin_name)` | OHLCV 데이터 조회 (DataFrame 반환) |
| `get_current_price(coin_name)` | 현재 가격 조회 |
| `buy(coin_name, amount)` | 시장가 매수 |
| `sell(coin_name, amount)` | 시장가 매도 |
| `get_coin_balance(coin_name)` | 특정 코인 잔고 조회 |
| `get_krw_balance()` | KRW 잔고 조회 |
| `get_my_balance(coin_names)` | 여러 코인의 잔고 조회 |

---

## API 명세

### Base URL
- 개발: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`

---

### Coin API

#### 활성화된 코인 목록 조회

```http
GET /api/v1/my/coins
```

**Response:**
```json
{
  "items": [
    {"id": 1, "name": "BTC"},
    {"id": 2, "name": "ETH"}
  ]
}
```

---

#### 거래 코인 추가

```http
POST /api/v1/my/coins
Content-Type: application/json

{
  "name": "BTC"
}
```

**Response:**
```json
{
  "id": 1,
  "name": "BTC"
}
```

---

#### 코인 삭제 (Soft Delete)

```http
DELETE /api/v1/my/coins/{coin_id}
```

**에러 케이스:**
- `400 Bad Request`: 코인에 잔고가 남아있는 경우

---

### Trade API

#### 즉시 거래 실행

```http
POST /api/v1/trade
```

모든 활성 코인에 대해 AI 분석 및 자동 거래를 실행합니다.

---

#### 거래 내역 조회 (Cursor 기반 페이지네이션)

```http
GET /api/v1/trade/transactions?cursor={cursor}&limit={limit}
```

**Query Parameters:**
| 파라미터 | 타입 | 필수 | 설명 | 기본값 |
|----------|------|------|------|--------|
| cursor | integer | X | 이전 페이지의 마지막 거래 ID | - |
| limit | integer | X | 페이지당 항목 수 (1-100) | 20 |

**Response:**
```json
{
  "items": [
    {
      "id": 123,
      "coin_id": 1,
      "coin_name": "BTC",
      "type": "buy",
      "price": 50000000.0,
      "amount": 0.001,
      "risk_level": "medium",
      "status": "success",
      "timestamp": "2025-11-22 10:30:45",
      "ai_reason": "상승 추세 예상",
      "execution_reason": "매수 주문 실행 완료"
    }
  ],
  "next_cursor": 100,
  "has_next": true
}
```

**페이지네이션 로직:**
- `has_next`가 `true`이면 다음 페이지 존재
- `next_cursor` 값을 다음 요청의 `cursor` 파라미터로 사용
- `has_next`가 `false`이면 마지막 페이지

**사용 예시:**
```bash
# 첫 페이지 조회
curl "http://localhost:8000/api/v1/trade/transactions?limit=20"

# 다음 페이지 조회
curl "http://localhost:8000/api/v1/trade/transactions?cursor=100&limit=20"
```

---

### Upbit API

#### 코인 OHLCV 데이터 조회

```http
GET /api/v1/coins/{coin_name}
```

**Response:**
```json
{
  "items": [
    {
      "timestamp": "2025-11-22T10:00:00",
      "open": 50000000.0,
      "high": 50500000.0,
      "low": 49500000.0,
      "close": 50200000.0,
      "volume": 123.45,
      "value": 6174900000.0
    }
  ]
}
```

---

## 데이터베이스 스키마

### Coin 테이블

```sql
CREATE TABLE coins (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  created_at DATETIME DEFAULT UTC_TIMESTAMP,
  is_deleted BOOLEAN DEFAULT FALSE
);
```

---

### Trade 테이블

```sql
CREATE TABLE trades (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  coin_id BIGINT NULL,
  trade_type VARCHAR(10) NULL,           -- BUY/SELL/HOLD
  price DECIMAL(20, 8) DEFAULT 0,
  amount DECIMAL(20, 8) DEFAULT 0,
  risk_level VARCHAR(10) NOT NULL,       -- NONE/LOW/MEDIUM/HIGH
  status VARCHAR(20) NOT NULL,           -- PENDING/SUCCESS/PARTIAL_SUCCESS/FAILED/NO_ACTION
  ai_reason TEXT NULL,
  execution_reason TEXT NULL,
  created_at DATETIME DEFAULT UTC_TIMESTAMP,
  FOREIGN KEY (coin_id) REFERENCES coins(id)
);
```

---

### Balance 테이블

```sql
CREATE TABLE balances (
  id BIGINT AUTO_INCREMENT PRIMARY KEY,
  amount DECIMAL(20, 8) NOT NULL,        -- KRW 잔고
  coin_amount DECIMAL(20, 8) DEFAULT 0,  -- 보유 코인의 KRW 가치
  created_at DATETIME DEFAULT UTC_TIMESTAMP
);
```

---

### Enum 정의

**TradeType (거래 유형)**
- `BUY`: 매수
- `SELL`: 매도
- `HOLD`: 보유

**RiskLevel (위험 수준)**
- `NONE`: 없음
- `LOW`: 낮음
- `MEDIUM`: 중간
- `HIGH`: 높음

**TradeStatus (거래 상태)**
- `PENDING`: 진행 중
- `SUCCESS`: 성공
- `PARTIAL_SUCCESS`: 부분 성공
- `FAILED`: 실패
- `NO_ACTION`: 거래 없음

---

## 자동 거래 시스템

### 스케줄러 설정

**실행 주기:** 5분 (300초)

**설정 위치:** `app/configs/app.py`

### 실행 흐름

```
스케줄러 (5분마다)
  ↓
TradeService.execute()
  ↓
1. 활성 코인 목록 조회
  ↓
2. KRW 잔고 확인
  ↓
3. 각 코인에 대해:
   ├─ OHLCV 데이터 조회 (Upbit)
   ├─ AI 분석 (OpenAI)
   └─ BUY/SELL/HOLD 결정에 따라 거래 실행
  ↓
4. 거래 결과 DB 저장
  ↓
5. 최종 잔고 기록
```

### 에러 처리

| 케이스 | 상태 | 설명 |
|--------|------|------|
| 활성 코인 없음 | NO_ACTION | 거래 가능한 코인이 없음 |
| KRW 잔고 없음 | NO_ACTION | KRW 잔고 부족 |
| AI 분석 실패 | FAILED | OpenAI API 오류 |
| 매수 잔액 부족 | FAILED | KRW 잔고 5000원 미만 |
| 매도 코인 없음 | FAILED | 보유 코인 없음 |
| 매도 금액 부족 | FAILED | 매도 예상 금액 5000원 미만 |

---

## 설치 및 실행

### 사전 준비

1. `.env` 파일 생성:
```bash
cp .env.example .env
```

2. `.env` 파일에서 필수 환경변수 설정

### 로컬 실행

```bash
# 의존성 설치
uv sync

# 마이그레이션 적용
uv run alembic upgrade head

# 서버 실행
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker Compose로 실행

```bash
# 서비스 빌드 및 시작
docker-compose up -d

# 로그 확인
docker-compose logs -f joo-coin-backend

# 서비스 중지
docker-compose down

# 컨테이너 재빌드
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### 접속 정보

- **Backend API:** http://localhost:8000
- **Swagger 문서:** http://localhost:8000/docs
- **MySQL:** localhost:3306

---

## 환경변수

| 변수 | 설명 | 필수 |
|------|------|------|
| `DATABASE_URL` | 데이터베이스 연결 URL | O |
| `UPBIT_ACCESS_KEY` | Upbit API 액세스 키 | O |
| `UPBIT_SECRET_KEY` | Upbit API 시크릿 키 | O |
| `OPENAI_API_KEY` | OpenAI API 키 | O |
| `DB_POOL_SIZE` | DB 커넥션 풀 크기 | X (기본값: 5) |
| `DB_MAX_OVERFLOW` | DB 오버플로우 크기 | X (기본값: 10) |
| `CORS_ORIGINS` | CORS 허용 오리진 | X (기본값: *) |

---

## Alembic 마이그레이션

### 마이그레이션 적용
```bash
uv run alembic upgrade head
```

### 마이그레이션 롤백
```bash
uv run alembic downgrade -1
```

### 새 마이그레이션 생성
```bash
uv run alembic revision --autogenerate -m "설명"
```

### Docker 환경에서 마이그레이션

```bash
# 마이그레이션 적용
docker-compose exec joo-coin-backend alembic upgrade head

# 새 마이그레이션 생성
docker-compose exec joo-coin-backend alembic revision --autogenerate -m "설명"
```

> 마이그레이션은 컨테이너 시작 시 자동으로 실행됩니다.

---

## 트러블슈팅

### 데이터베이스 연결 오류

```bash
# DB 컨테이너 상태 확인
docker-compose ps joo-coin-db

# DB 로그 확인
docker-compose logs joo-coin-db
```

### 컨테이너 재빌드

```bash
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```
