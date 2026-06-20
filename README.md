# 📈 바이브코딩으로 만드는 금융 AI 시스템

> **VS Code + Claude Code**로 코딩 지식 없이  
> 한국투자증권 모의투자 대시보드 · AI 챗봇 · RAG 주식분석 시스템을 만드는 **2일 실습 과정**

---

## 🛠 사용하는 도구

| 도구 | 역할 | 다운로드 |
|------|------|---------|
| **Git** | 코드 버전 관리 · GitHub 업로드 | [git-scm.com](https://git-scm.com/downloads) |
| **Python 3.11** | 프로그래밍 언어 | [python.org/downloads](https://www.python.org/downloads/) |
| **VS Code** | 코드 편집기 (무료) | [code.visualstudio.com](https://code.visualstudio.com) |
| **Node.js** | Claude Code 실행 환경 | [nodejs.org](https://nodejs.org) (LTS 버전) |
| **Claude Code** | AI 코딩 어시스턴트 | `npm install -g @anthropic-ai/claude-code` |

---

## ⚡ 처음부터 끝까지 — 세팅 명령어 전체

> 아래 순서대로 **한 줄씩** 터미널에 입력하세요.  
> 자세한 설명은 [`docs/SETUP.md`](docs/SETUP.md) 를 참고하세요.

### 1단계 · 설치 확인
```bash
git --version      # git version 2.x.x 가 나와야 함
python --version   # Python 3.11.x 가 나와야 함
node --version     # v18.x.x 이상이 나와야 함
```

> 설치가 안 되어 있으면 위 표의 링크에서 먼저 설치하세요.

### 2단계 · Claude Code 설치
```bash
npm install -g @anthropic-ai/claude-code
claude --version   # 설치 확인
claude             # 로그인 (브라우저 팝업 → Anthropic 계정 로그인)
# 로그인 완료 후 Ctrl+C 로 종료
```

### 3단계 · 저장소 복사
```bash
# GitHub에서 Fork 후 clone (본인ID를 본인 GitHub 아이디로 변경)
git clone https://github.com/본인ID/finance-ai-course.git
cd finance-ai-course
code .             # VS Code로 열기
```

### 4단계 · 가상환경 생성 및 활성화
```bash
# 가상환경 생성
python -m venv .venv

# 활성화 (Windows)
.venv\Scripts\activate

# 활성화 (Mac / Linux)
source .venv/bin/activate

# 활성화 확인: 터미널 앞에 (.venv) 가 붙으면 성공
```

### 5단계 · 패키지 설치 (이것 하나로 전부!)
```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 전체 패키지 한 번에 설치
pip install -r requirements.txt
```

### 6단계 · API Key 설정
```bash
# Windows
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

`.env` 파일을 열어 본인 API Key 입력 후 저장 (`Ctrl+S`):
```ini
KIS_APP_KEY=PSxxxxxxxxxxxxxxxxxxxxxxxxx
KIS_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
KIS_ACCOUNT_NO=12345678
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxx
FSS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> API Key 발급 방법 → [`docs/API_KEYS.md`](docs/API_KEYS.md)

### 7단계 · 환경 점검 (모든 항목 초록색이면 완료!)
```bash
cd day1/01_setup
streamlit run check.py
# 브라우저가 자동으로 열립니다
# http://localhost:8501
```

---

## 📅 커리큘럼

### Day 1 · 바이브코딩 + 모의투자 대시보드

| 시간 | 폴더 | 내용 | 명령어 |
|------|------|------|--------|
| 09:00 | `day1/01_setup` | 환경 세팅 · Claude Code 입문 | `streamlit run check.py` |
| 09:40 | `day1/02_kis_api` | KIS OpenAPI · 현재가·잔고 조회 | `python kis_client.py` |
| 11:00 | `day1/03_streamlit` | Streamlit 기초 UI | `streamlit run app.py` |
| 11:40 | `day1/04_chart` | 캔들차트 · MA · RSI · MACD | `streamlit run app.py` |
| 13:20 | `day1/05_trading` | 매수/매도/취소 주문 | `streamlit run app.py` |
| 16:00 | `day1/06_backtest` | 백테스팅 · 자동매매 전략 | `streamlit run backtest.py` |

### Day 2 · AI 챗봇 + RAG 주식데이터 분석

| 시간 | 폴더 | 내용 | 명령어 |
|------|------|------|--------|
| 09:00 | `day2/01_openai` | OpenAI API 기초 · 토큰·비용 | `python hello_openai.py` |
| 09:40 | `day2/02_chatbot` | 투자 상담 AI 챗봇 | `streamlit run chatbot.py` |
| 11:00 | `day2/03_fss_api` | 금융위 주식시세 API 수집 | `python fss_client.py` |
| 13:20 | `day2/04_chromadb` | ChromaDB 벡터 DB 구축 | `python build_db.py` |
| 14:40 | `day2/05_rag` | LangChain RAG 체인 | `streamlit run rag_app.py` |
| 16:00 | `day2/06_integration` | 최종 통합 어시스턴트 | `streamlit run app.py` |

---

## 🗂 폴더 구조

```
finance-ai-course/
│
├── 📄 README.md            ← 지금 보고 있는 파일
├── 📄 requirements.txt     ← 패키지 목록 (pip install -r로 전부 설치)
├── 📄 .env.example         ← API Key 템플릿
├── 📄 .env                 ← 본인 API Key 입력 (git에 올리면 안 됨!)
├── 📄 .gitignore           ← .env 등 민감 파일 제외 설정
│
├── 📁 day1/                ← Day 1 실습 폴더
│   ├── 01_setup/           # 환경 점검 앱
│   ├── 02_kis_api/         # KIS OpenAPI 연동
│   ├── 03_streamlit/       # Streamlit 기초
│   ├── 04_chart/           # 캔들차트 + 기술지표
│   ├── 05_trading/         # 매수/매도 주문
│   └── 06_backtest/        # 백테스팅 + 자동매매
│
├── 📁 day2/                ← Day 2 실습 폴더
│   ├── 01_openai/          # OpenAI API 기초
│   ├── 02_chatbot/         # 투자 상담 챗봇
│   ├── 03_fss_api/         # 금융위 주식시세 API
│   ├── 04_chromadb/        # ChromaDB 벡터 DB
│   ├── 05_rag/             # LangChain RAG
│   └── 06_integration/     # 최종 통합 시스템
│
└── 📁 docs/                ← 참고 문서
    ├── SETUP.md            # 환경 세팅 상세 가이드
    ├── API_KEYS.md         # API Key 발급 방법
    └── COMMANDS.md         # 전체 명령어 모음
```

---

## 📦 설치되는 패키지 (requirements.txt)

```
streamlit       웹앱 UI 프레임워크
requests        HTTP API 호출
pandas          데이터 처리
numpy           수치 계산
plotly          인터랙티브 차트
openai          OpenAI GPT API
langchain       LLM 오케스트레이션
langchain-openai  LangChain OpenAI 연동
langchain-community  LangChain 커뮤니티 패키지
chromadb        벡터 데이터베이스
python-dotenv   .env 파일 환경변수 로딩
yfinance        야후 파이낸스 (백테스팅용)
```

---

## 🔑 필요한 API Key 3가지

| API | 용도 | 발급 URL | 비용 |
|-----|------|---------|------|
| **KIS OpenAPI** | 모의투자 주가·주문 | [apiportal.koreainvestment.com](https://apiportal.koreainvestment.com) | 무료 |
| **OpenAI API** | GPT 챗봇·임베딩 | [platform.openai.com/api-keys](https://platform.openai.com/api-keys) | 소액 (실습 기준 $0.1 미만) |
| **금융위 공공API** | 주식시세 데이터 수집 | [data.go.kr](https://www.data.go.kr) → "주식시세" 검색 | 무료 |

> 발급 방법 상세 안내 → [`docs/API_KEYS.md`](docs/API_KEYS.md)

---

## 🚀 수료 후 손에 남는 것

```
✅ KIS 모의투자 대시보드    — Streamlit 웹앱 (캔들차트·매매·포트폴리오)
✅ 투자 AI 챗봇             — OpenAI 연동 멀티턴 챗봇
✅ RAG 주식분석 시스템      — 금융위 데이터 기반 AI Q&A
✅ GitHub 공개 포트폴리오   — 배포된 공개 URL
✅ 실전 재사용 코드         — KIS + FSS + LangChain 코드베이스
```

---

## ⚠️ 주의사항

- 본 과정은 **모의투자 전용**입니다. 실전 투자와 무관합니다.
- `.env` 파일은 절대 GitHub에 올리지 마세요 (`.gitignore`에 포함됨).
- 투자 AI 답변은 참고용이며 실제 투자 결정은 본인 판단으로 하세요.

---

## 📞 문의

강사: 이상목  
과정: 바이브코딩 × 금융 AI (2일 16시간)

---

## 🆘 막혔을 때

```bash
# 환경 점검 먼저
cd day1/01_setup
streamlit run check.py

# 명령어 전체 모음
# docs/COMMANDS.md 참고

# 가상환경 재활성화 (.venv 표시가 없을 때)
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Mac/Linux
```
