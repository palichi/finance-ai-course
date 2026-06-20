# 🔑 API Key 발급 가이드

> 본 과정에서 사용하는 3가지 API의 발급 방법을 단계별로 설명합니다.

---

## 1. 한국투자증권 OpenAPI (KIS)

### 발급 순서
```
1. https://apiportal.koreainvestment.com 접속
2. 회원가입 → 로그인
3. 상단 메뉴 "앱 등록" 클릭
4. 앱 이름 입력 (예: my-trading-app)
5. ⚠️ "모의투자" 선택 (실전투자 X)
6. 등록 버튼 클릭
7. App Key / App Secret 복사 → .env에 붙여넣기
```

### 모의투자 계좌번호 확인
```
HTS(eFriend Plus) 또는 MTS(한국투자증권 앱) 실행
→ 계좌 목록에서 "모의투자" 계좌 확인
→ 계좌번호 8자리 확인 후 .env에 입력
```

### Base URL (중요!)
```
모의투자: https://openapivts.koreainvestment.com:29443
실전투자: https://openapi.koreainvestment.com:9443  ← 본 과정에서 사용 안 함
```

---

## 2. OpenAI API

### 발급 순서
```
1. https://platform.openai.com 접속
2. 회원가입 → 로그인
3. 우측 상단 계정 클릭 → API Keys
4. "+ Create new secret key" 클릭
5. 이름 입력 (예: finance-ai-course)
6. Create secret key 클릭
7. 키 복사 (이 화면 이후 다시 볼 수 없음!)
   → .env 파일에 즉시 붙여넣기
```

### 크레딧 충전 (강사가 제공하는 경우 불필요)
```
Settings → Billing → Add payment method
최소 $5 충전 (실습에 충분한 금액)
```

### 모델별 비용 (참고)
```
gpt-4o-mini:  입력 $0.150/1M 토큰  (저렴, 실습 권장)
gpt-4o:       입력 $2.500/1M 토큰
```

---

## 3. 금융위원회 공공데이터 API

### 발급 순서
```
1. https://www.data.go.kr 접속 (공공데이터포털)
2. 회원가입 → 로그인
3. 검색창에 "주식시세" 검색
4. "금융위원회_주식시세" 클릭
5. "활용신청" 버튼 클릭
6. 신청 목적 입력 후 신청 완료
7. 마이페이지 → 인증키 복사 → .env에 입력
```

> ⏱ 승인까지 최대 1~2시간 소요될 수 있습니다.  
> 강의 당일 사용 예정이라면 **전날 미리 발급** 받으세요.

### 주요 서비스 URL
```
기본 URL: https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService

주식시세 조회:    /getStockPriceInfo
종목 기본정보:    /getItemInfo
```

---

## ⚠️ Key 보안 주의사항

```
✅ DO     - .env 파일에만 저장
✅ DO     - .gitignore에 .env 포함 확인
❌ DON'T  - 코드 파일에 직접 입력 (github에 올라감!)
❌ DON'T  - 카카오톡, 이메일 등으로 공유
❌ DON'T  - github에 올리기 (자동 탐지되어 무효화됨)
```

### 실수로 Key를 github에 올렸다면
```
1. 즉시 해당 API 포털에서 Key 삭제
2. 새로운 Key 재발급
3. .env 파일에 새 Key 입력
4. git 이력에서 제거: git filter-branch (강사에게 도움 요청)
```
