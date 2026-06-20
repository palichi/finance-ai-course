# 📁 Day 2 · 06 · 최종 통합 — 투자 AI 어시스턴트

## 이 실습에서 배우는 것
- KIS 모의투자 대시보드 + RAG 챗봇 통합
- Streamlit 멀티페이지 앱 구성
- 대화 메모리로 이전 질문 맥락 유지
- 답변 출처 표시로 신뢰성 확보
- GitHub에 배포하기

---

## 📂 이 폴더의 파일 구성

```
day2/06_integration/
└── app.py      ← 실습에서 Claude Code로 직접 만들기
```

> `app.py` 는 **이 실습에서 직접 만듭니다.**
> 아래 순서대로 따라오세요.

---

## 사전 확인 — 아래 3가지가 모두 준비되어 있어야 합니다

### ① KIS API 연결 확인
```bash
cd day1/02_kis_api
python kis_client.py
# ✅ Token 발급 성공 이 나오면 OK
cd ../../day2/06_integration
```

### ② ChromaDB 구축 확인
```bash
python -c "
import chromadb
db  = chromadb.PersistentClient(path='../04_chromadb/chroma_db')
col = db.get_collection('stock_data')
print(f'✅ 벡터 DB 연결됨: {col.count():,}건')
"
# ✅ 벡터 DB 연결됨: 2,450건 이 나오면 OK
```

### ③ RAG 체인 확인
```bash
cd ../05_rag
python rag_chain.py
# 질문에 답변이 나오면 OK
cd ../06_integration
```

> 셋 중 하나라도 안 되면 해당 폴더의 README 를 다시 확인하세요.

---

## 🖥 실습 순서

---

### STEP 1 · 폴더 이동

```bash
cd day2/06_integration
```

```bash
ls
# README.md 만 있으면 정상
```

---

### STEP 2 · Claude Code 실행

**새 터미널 탭 열기** (Ctrl + Shift + `)

```bash
claude
```

---

### STEP 3 · [Claude Code 실습] app.py 만들기

아래 프롬프트를 **그대로 복사해서 붙여넣기** 하세요:

```
day2/06_integration/app.py 파일을 만들어줘.

KIS 모의투자 대시보드와 RAG 챗봇을 하나로 합친
Streamlit 통합 앱이야.

기본 설정:
  페이지 제목: "📈 투자 AI 어시스턴트"
  레이아웃: wide
  .env 파일: ../../.env 경로에서 읽기

사이드바 메뉴 구성 (st.radio 로 페이지 전환):
  🏠 대시보드
  💹 주식 조회
  🤖 AI 챗봇

─── 🏠 대시보드 페이지 ───
KIS API 로 계좌 잔고를 조회해서 아래를 표시해줘:
  1. 상단 지표 카드 3개
     - 총 평가금액
     - 예수금
     - 평가손익
  2. 보유 종목 테이블
     종목명, 보유수량, 평균단가, 현재가, 평가손익, 수익률
  3. 자산 배분 파이차트 (plotly)
  4. KIS API 연결 실패 시 st.warning 으로 안내

─── 💹 주식 조회 페이지 ───
1. 종목코드 입력창 + 조회 버튼
2. 인기 종목 바로가기 버튼 5개
   삼성전자(005930), SK하이닉스(000660),
   NAVER(035420), 카카오(035720), 현대차(005380)
3. 현재가, 전일대비, 시가, 고가, 저가, 거래량 표시
4. KIS API 로 최근 30일 일봉 데이터를 가져와서
   Plotly 캔들차트로 표시

─── 🤖 AI 챗봇 페이지 ───
RAG 챗봇 + 대화 메모리 기능:
  1. ../05_rag/rag_chain.py 의 load_rag_chain() 을 import 해서 사용
  2. st.chat_input / st.chat_message 로 채팅 UI 구성
  3. st.session_state 로 대화 이력 유지 (멀티턴)
  4. 답변 아래 st.expander 로 참고 데이터 출처 표시
  5. 사이드바에 테스트 질문 버튼 5개:
     "삼성전자 최근 주가 흐름은?"
     "거래량이 가장 많았던 날은?"
     "SK하이닉스가 오른 날은?"
     "가장 많이 상승한 종목은?"
     "12월 삼성전자 주가는?"
  6. 대화 초기화 버튼

공통:
  모든 API 오류는 st.error 또는 st.warning 으로 표시
  KIS API 는 ../day1/02_kis_api/kis_client.py 의 함수를 import 해서 사용
  파일명: app.py
```

---

### STEP 4 · app.py 실행 확인

Claude Code가 파일을 만들면 **기존 터미널로 돌아가서** 실행:

```bash
streamlit run app.py
```

브라우저가 열리면:

```
사이드바에서 메뉴 클릭해서 확인
  🏠 대시보드  → 계좌 잔고·보유 종목·파이차트
  💹 주식 조회 → 종목 검색·현재가·캔들차트
  🤖 AI 챗봇  → RAG 기반 주식 Q&A
```

---

### STEP 5 · 테스트 질문으로 확인

**💹 주식 조회 페이지:**
```
005930 입력 → 조회 버튼 클릭
→ 삼성전자 현재가와 캔들차트가 나오면 성공
```

**🤖 AI 챗봇 페이지:**
```
수집 데이터 기반 질문 (RAG 가 정확하게 답함)
  "삼성전자 지난달 주가 흐름은?"
  "거래량이 가장 많았던 날은 언제야?"
  "SK하이닉스가 많이 오른 날은?"

실시간 데이터 질문 (KIS API 연동 필요)
  "삼성전자 지금 주가 얼마야?"
  "내 포트폴리오 현황 알려줘"

AI 분석 질문
  "삼성전자 지금 매수해도 될까?"
  "RSI 30 이하인 종목이 있어?"
```

---

### STEP 6 · 오류가 나면 Claude Code 에 요청

각 기능별로 오류가 나면 그대로 붙여넣기:

```
app.py 실행 중 아래 오류가 났어, 고쳐줘:
(오류 메시지 전체 붙여넣기)
```

---

### STEP 7 · 추가 실습 — 기능 더 넣어보기

**미션 1 · 주간 리포트 자동화**
```
app.py 에 매주 월요일 아침에
지난 주 포트폴리오 수익률 요약을
이메일로 보내는 기능을 추가해줘.
schedule 라이브러리와 smtplib 를 사용해줘.
```

**미션 2 · 나만의 기능 추가**
```
내가 원하는 기능을 추가해줘:
[원하는 기능을 자유롭게 설명]
```

---

### STEP 8 · GitHub 배포

#### ① 최종 코드 GitHub 에 올리기

```bash
# finance-ai-course 최상위 폴더로 이동
cd ../../..

# 변경 사항 확인
git status

# 전체 올리기
git add .
git commit -m "최종 통합 앱 완성"
git push origin main
```

#### ② Streamlit Cloud 배포

```
1. https://share.streamlit.io 접속
2. GitHub 계정으로 로그인
3. "New app" 클릭
4. 아래 정보 입력:
   저장소: 본인ID/finance-ai-course
   브랜치: main
   메인파일: day2/06_integration/app.py
5. "Advanced settings" → "Secrets" 클릭
   아래 내용 입력 (API Key 는 여기서만 입력, GitHub X)
```

```toml
KIS_APP_KEY    = "PSxxxxxxxxxx"
KIS_APP_SECRET = "xxxxxxxxxx"
KIS_ACCOUNT_NO = "12345678"
OPENAI_API_KEY = "sk-xxxxxxxxxx"
FSS_API_KEY    = "xxxxxxxxxx"
```

```
6. "Deploy" 클릭
7. 배포 완료 → 공개 URL 생성
   https://본인이름-finance-ai.streamlit.app
```

> ⚠️ ChromaDB 는 로컬 파일이라 클라우드 배포 시 작동하지 않습니다.
> 배포용으로는 Pinecone 같은 클라우드 벡터 DB 로 교체가 필요합니다.
> 이 부분은 강사에게 문의하세요.

---

### STEP 9 · 포트폴리오 정리

#### GitHub README 업데이트

```bash
claude
```

```
이 프로젝트의 README.md 를 포트폴리오용으로 멋지게 만들어줘.

포함할 내용:
1. 프로젝트 소개 (한 줄 요약)
2. 주요 기능 목록
3. 기술 스택 배지
   Python, Streamlit, LangChain, ChromaDB,
   OpenAI, KIS OpenAPI, 금융위 공공데이터 API
4. 실행 방법 (설치 → 설정 → 실행)
5. 스크린샷 삽입 위치 안내
```

#### 스크린샷 찍기

```
앱 실행 후 각 페이지 스크린샷:
  1. 대시보드 화면
  2. 주식 조회 + 캔들차트
  3. AI 챗봇 답변 화면

저장 위치: assets/ 폴더
```

```bash
mkdir assets
# 스크린샷 파일을 assets/ 폴더에 넣기
git add assets/
git commit -m "스크린샷 추가"
git push origin main
```

---

## 💡 이 실습의 핵심 포인트

```
지금까지 만든 모든 것을 하나로 합칩니다.

Day 1: KIS API → 실시간 주가·잔고·캔들차트
Day 2: RAG    → 수집 데이터 기반 AI 답변

"코딩 없이 AI 와 대화만으로
 실제 금융 서비스 수준의 앱을 만들었다"
는 것을 체감하는 것이 목표입니다.
```

---

## ❓ 자주 묻는 질문

**Q. 대시보드에 보유 종목이 안 나와요**
```
KIS 모의투자 계좌에 예수금과 보유 종목이 있어야 합니다.
장 시간(09:00~15:30) 이후에는 잔고 조회가 안 될 수 있습니다.
```

**Q. AI 챗봇이 "데이터에 없다" 고만 해요**
```
수집한 10개 종목과 최근 1년 기간 안에서 질문해보세요.
"테슬라 주가", "5년 전 삼성전자" 같은 질문은 답 못합니다.
```

**Q. 캔들차트가 안 나와요**
```
KIS API 에서 일봉 데이터를 못 가져온 경우입니다.
Claude Code 에 요청:
"app.py 의 캔들차트 부분에서 오류 처리를 추가해줘.
 데이터가 없으면 st.info 로 안내 메시지를 표시해줘."
```

**Q. Streamlit Cloud 배포 후 RAG 가 안 돼요**
```
ChromaDB 는 로컬 파일 저장 방식이라
클라우드에서는 작동하지 않습니다.
로컬에서 실행할 때는 정상입니다.
클라우드 배포용 RAG 는 강사에게 문의하세요.
```
