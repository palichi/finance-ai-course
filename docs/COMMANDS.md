# 📋 전체 명령어 모음 — 빠른 참조

> 강의 중 필요한 명령어를 한 곳에 모았습니다.  
> 복사해서 터미널에 바로 붙여넣으세요.

---

## 🔧 기본 터미널 명령어

```bash
# 현재 위치 확인
pwd

# 폴더 이동
cd finance-ai-course          # 최상위 폴더로
cd day1/02_kis_api            # 특정 실습 폴더로
cd ..                         # 상위 폴더로
cd ../..                      # 두 단계 위로

# 파일 목록 보기
ls                            # Mac/Linux
dir                           # Windows

# 파일 내용 보기
cat 파일명.py                  # Mac/Linux
type 파일명.py                 # Windows

# 파일 생성 (.env)
cp .env.example .env          # Mac/Linux
copy .env.example .env        # Windows
```

---

## 🐍 Python 관련

```bash
# 버전 확인
python --version

# 패키지 설치
pip install -r requirements.txt

# 개별 패키지 설치
pip install streamlit
pip install openai
pip install langchain chromadb

# 패키지 업그레이드
pip install --upgrade pip
pip install --upgrade openai

# 설치 확인
python -c "import streamlit; print(streamlit.__version__)"
python -c "import openai; print(openai.__version__)"
python -c "import chromadb; print(chromadb.__version__)"

# 설치된 패키지 목록
pip list
```

---

## 🤖 Claude Code

```bash
# 실행
claude

# 프로젝트 폴더에서 실행 (코드 컨텍스트 포함)
cd day1/02_kis_api && claude

# 주요 내부 명령어 (claude 실행 중)
/help          # 도움말
/clear         # 대화 초기화
/exit          # 종료
/status        # 현재 상태 확인

# 파일을 읽으며 대화
# claude 안에서:
# > @app.py 를 읽고 버그를 찾아줘
```

---

## 📺 Streamlit

```bash
# 기본 실행
streamlit run app.py

# 포트 지정 (기본: 8501)
streamlit run app.py --server.port 8502

# 브라우저 자동 열기 끄기
streamlit run app.py --server.headless true

# 외부 접속 허용 (같은 Wi-Fi 다른 PC에서 접속)
streamlit run app.py --server.address 0.0.0.0

# 종료
Ctrl+C

# 로컬 접속 URL
http://localhost:8501
```

---

## 🗂 Git / GitHub

```bash
# 설정 (최초 1회)
git config --global user.name "본인이름"
git config --global user.email "이메일@gmail.com"

# 저장소 복사
git clone https://github.com/본인ID/finance-ai-course.git

# 현재 상태 확인
git status

# 변경 파일 스테이징
git add .                     # 전체 파일
git add app.py                # 특정 파일만

# 커밋 (저장)
git commit -m "기능: 현재가 조회 추가"

# GitHub에 올리기
git push origin main

# 최신 코드 가져오기 (강사 업데이트 시)
git pull origin main

# 커밋 이력 보기
git log --oneline
```

---

## 🔑 API 테스트

```bash
# KIS API Token 발급 확인
cd day1/02_kis_api
python kis_client.py

# OpenAI API 확인
cd day2/01_openai
python hello_openai.py

# 금융위 API 확인
cd day2/03_fss_api
python fss_client.py

# ChromaDB 구축
cd day2/04_chromadb
python build_db.py

# 환경 전체 점검
cd day1/01_setup
streamlit run check.py
```

---

## 🆘 오류 해결

```bash
# ModuleNotFoundError (패키지 없음)
pip install 패키지명

# Port already in use (포트 충돌)
streamlit run app.py --server.port 8502

# Permission denied (권한 오류, Mac)
chmod +x 파일명.py

# SSL Certificate Error
pip install --upgrade certifi

# pip 자체 오류
python -m pip install --upgrade pip

# claude 명령 없음 (재설치)
npm install -g @anthropic-ai/claude-code

# .env 파일이 적용 안 됨
python -c "from dotenv import load_dotenv; load_dotenv('.env'); import os; print(os.getenv('KIS_APP_KEY','없음'))"
```

---

## 📌 실습별 빠른 실행 명령

```bash
# Day 1
cd day1/01_setup  && streamlit run check.py         # 환경 점검
cd day1/02_kis_api && python kis_client.py           # KIS API 테스트
cd day1/02_kis_api && streamlit run app.py           # 현재가 조회 앱
cd day1/04_chart   && streamlit run app.py           # 차트 분석
cd day1/05_trading && streamlit run app.py           # 매수/매도 주문
cd day1/06_backtest && streamlit run backtest.py     # 백테스팅

# Day 2
cd day2/01_openai  && python hello_openai.py         # OpenAI 테스트
cd day2/02_chatbot && streamlit run chatbot.py       # 투자 챗봇
cd day2/03_fss_api && python fss_client.py           # 금융위 API
cd day2/03_fss_api && python collect_data.py         # 대량 수집
cd day2/04_chromadb && python build_db.py            # 벡터 DB 구축
cd day2/05_rag     && streamlit run rag_app.py       # RAG 챗봇
cd day2/06_integration && streamlit run app.py       # 최종 통합
```
