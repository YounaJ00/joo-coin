## 설계 

- 현재 구조의 문제점 : coin name이 하드코딩 되있어서 다른 코인 거래 불가
- 개선 방안 : coin name을 파라미터로 받아서 처리

## 화면 설계 

### 메인화면

- 왼쪽 화면 : 
  - 거래 코인 목록 페이지로 가기 버튼
  - 계좌 잔액 변동 그래프 : 
    - 시간에 따른 잔액 변동 표시
- 오른쪽 화면 :
  - 거래 내역 표시 : 
    - 날짜, 거래 코인 ID, 거래 종류(매수/매도), 수량, 가격, 총액, AI 의견

### 거래 코인 목록 페이지

- 왼쪽 화면 :
  - 코인 선택 바 :
    - 거래 가능한 코인 목록 표시 (이거 프론트에 하드코딩)
    - 선택된 코인에 따라 우측 화면 내용 변경
  - 거래 중인 코인 목록 :
    - 현재 거래 중인 코인들의 목록 표시
    - 각 코인 클릭 시 코인 삭제 가능
- 오른쪽 화면 :
  - 해당 해당 코인에 대한 정보 표시

## Schema 설계 

> {} 비어있는건 아무런 값도 없음을 의미

```json
{
  "/api/v1/my/coins": {
    "get": {
      "description": "내 거래 코인 조회",
      "request": {},
      "response": {
        "items": [
          {
            "id": 1,
            "name": "Bitcoin"
          },
          {
            "id": 2,
            "name": "Ethereum"
          }
        ]
      }
    },
    "post": {
      "description": "거래 코인 추가",
      "request": {
        "name": "string"
      },
      "response": {}
    }
  },
  "/api/v1/my/coins/{id}": {
    "delete": {
      "description": "내 코인 정보 삭제",
      "request": {},
      "response": {}
    }
  },
  "/api/v1/coins/{name}": {
    "get": {
      "description": "해당 코인 시세 정보",
      "request": {},
      "response": {
        "items": [
          {
            "timestamp": "2025-11-21 09:00:00",
            "open": 129896000,
            "high": 131000000,
            "low": 125010000,
            "close": 125032000,
            "volume": 3501.43075285,
            "value": 446851623318.24550
          },
          {
            "timestamp": "2025-11-20 09:00:00",
            "open": 136500000,
            "high": 138621000,
            "low": 129800000,
            "close": 129896000,
            "volume": 4303.83230626,
            "value": 575824585241.20450
          }
        ]
      }
    }
  },
  "/api/v1/transactions": {
    "get": {
      "description": "내 거래 내역 조회",
      "request": {},
      "response": {
        "items": [
          {
            "id": 1,
            "coin_id": 1,
            "coin_name": "Bitcoin",
            "type": "buy",
            "price": 125032000,
            "amount": 0.5,
            "riskLevel": "high",
            "timestamp": "2025-11-21 10:00:00",
            "aiReason": "This transaction indicates a purchase of 0.5 Bitcoin at a price of 125,032,000 KRW on November 21, 2025. Given the market trends, this could be a strategic buy considering the recent price fluctuations."
          },
          {
            "id": 2,
            "coin_id": 2,
            "coin_name": "Ethereum",
            "type": "sell",
            "price": 3500000,
            "amount": 2,
            "riskLevel": "medium",
            "timestamp": "2025-11-20 14:30:00",
            "aiReason": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua."
          }
        ]
      }
    }
  }
}
```