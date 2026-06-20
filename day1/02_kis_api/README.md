# 📁 Day 1 · 02 · KIS OpenAPI — 현재가·잔고 조회

## 이 실습에서 배우는 것
- 한국투자증권 OpenAPI 구조 이해
- Access Token 발급 원리
- 현재가·잔고 API 호출 방법
- Claude Code로 API 연동 코드 생성하기

---

## 🖥 실습 명령어 (순서대로)

### ① 폴더 이동
```bash
cd day1/02_kis_api
```

### ② 파일 목록 확인
```bash
ls
# kis_client.py  app.py  README.md  가 보여야 합니다
```

### ③ KIS API 연결 테스트 (Token 발급 확인)
```bash
python kis_client.py
# 출력 예:
# ✅ Token 발급 성공: eyJ0...
# ✅ 삼성전자 현재가: 78,500원
```


### ④ Streamlit 앱 실행

```bash
claude
```

### ⑤ (실습) Claude Code로 기능 추가

```
day1/app.py  만들어줘
한국투자증권 KIS OpenAPI 모의투자를 사용해서
주식 현재가를 조회하는 Streamlit 웹앱을 만들어줘.

조건:
- .env 파일에서 KIS_APP_KEY, KIS_APP_SECRET, KIS_ACCOUNT_NO 를 읽어와
- 모의투자 Base URL: https://openapivts.koreainvestment.com:29443
- Access Token 발급 후 현재가 조회 (TR: FHKST01010100)
- 종목코드 입력창과 조회 버튼을 만들어줘
- 현재가, 전일대비, 시가, 고가, 저가, 거래량을 화면에 보여줘
- 파일명은 app.py 로 저장해줘

### ④ Streamlit 앱 실행
```bash
streamlit run app.py

# 출력 예:
# ✅ Token 발급 성공: eyJ0...
# ✅ 삼성전자 현재가: 78,500원


```
> app.py에 호가(매수호가/매도호가 10단계)를 테이블로 보여주는 기능을 추가해줘
```
### ④ Streamlit 앱 실행
```bash
streamlit run app.py

# 출력 예:
`````

--- 각자 실습


---

## 🔍 KIS API 핵심 구조 설명

```
[내 앱] → (App Key + Secret) → [KIS 서버] → Access Token 발급
[내 앱] → (Token + TR_ID)   → [KIS 서버] → 데이터 응답
```

### 모의투자 Base URL
```
https://openapivts.koreainvestment.com:9443
```

### 주요 TR ID
```
TR ID            설명
─────────────────────────────
FHKST01010100   현재가 조회
FHKST01010200   호가 조회  
FHKST03010100   일봉/주봉/월봉
VTTC8434R       잔고 조회 (모의)
VTTC0802U       매수 주문 (모의)
VTTC0801U       매도 주문 (모의)
```

---

## 💡 Claude Code 활용 예시

```bash
claude

# 예시 1: 특정 기능 추가
> app.py에 종목명으로도 검색할 수 있게 해줘.
  예를 들어 "삼성전자" 를 입력하면 005930 코드로 조회되게

# 예시 2: 오류 해결
> 이 오류를 해결해줘:
  requests.exceptions.SSLError: HTTPSConnectionPool ...

# 예시 3: 코드 이해
> kis_client.py의 get_token 함수가 어떻게 동작하는지 설명해줘
```

---

## ❓ 자주 발생하는 오류

**Token 발급 실패 (401 오류)**
```
원인: App Key 또는 App Secret 오류
해결: .env 파일의 KIS_APP_KEY, KIS_APP_SECRET 재확인
     모의투자 앱인지 확인 (실전투자 Key는 다름)
```

**SSL 오류**
```bash
pip install --upgrade certifi
```

**계좌 조회 실패**
```
원인: 계좌번호 오류 또는 모의투자 미신청
해결: HTS/MTS에서 모의투자 계좌 확인
     KIS_ACCOUNT_NO 는 숫자 8자리
```
