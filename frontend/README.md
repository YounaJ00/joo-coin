# Joo Coin Frontend

React + TypeScript + Vite 기반의 암호화폐 거래소 프론트엔드 애플리케이션입니다.

## 기술 스택

- **React 19** - UI 라이브러리
- **TypeScript** - 타입 안정성
- **Vite** - 빌드 도구
- **TailwindCSS** - 스타일링
- **shadcn/ui** - UI 컴포넌트
- **Recharts** - 차트 라이브러리
- **Axios** - HTTP 클라이언트

## 주요 기능

### 1. 코인 관리

[x] 내 거래 코인 목록 조회
[x] 코인 추가/삭제
[x] 코인 검색

### 2. 차트 조회

[x] 선택한 코인의 OHLCV 데이터 시각화
[x] 캔들스틱 차트 및 라인 차트 전환
[x] 거래량 차트

### 3. 거래 내역

[x] 거래 내역 조회 (페이지네이션)
[x] 즉시 거래 실행
[x] 거래 상태 및 상세 정보 표시

## 프로젝트 구조

```
src/
├── components/          # React 컴포넌트
│   ├── ui/             # shadcn/ui 컴포넌트
│   ├── CoinList.tsx   # 코인 목록 컴포넌트
│   ├── CoinChart.tsx  # 차트 컴포넌트
│   ├── TransactionHistory.tsx  # 거래 내역 컴포넌트
│   └── Toaster.tsx    # 토스트 알림 컴포넌트
├── contexts/          # React Context
│   └── ToastContext.tsx  # 토스트 컨텍스트
├── lib/               # 유틸리티 및 API
│   ├── api.ts         # API 클라이언트
│   └── utils.ts      # 유틸리티 함수
├── hooks/             # 커스텀 훅
│   └── use-toast.ts   # 토스트 훅 (재export)
├── App.tsx            # 메인 앱 컴포넌트
└── main.tsx           # 진입점
```


