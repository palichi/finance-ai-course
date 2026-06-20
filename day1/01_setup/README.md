# 📁 Day 1 · 01 · 개발환경 세팅

## 이 실습에서 배우는 것
- VS Code 터미널 사용법
- Claude Code로 AI에게 코드 요청하는 방법
- Python 가상환경 개념
- `.env` 파일로 API Key 안전하게 관리하는 법

---

## 🖥 실습 명령어 (하나씩 따라하기)

### ① VS Code 터미널 열기
```
단축키: Ctrl + ` (백틱 — 키보드 왼쪽 위 숫자 1 왼쪽)
또는: 메뉴 → Terminal → New Terminal
```

### ② 현재 위치 확인
```bash
pwd
# 출력 예: /Users/홈/finance-ai-course  (Mac/Linux)
# 출력 예: C:\Users\홈\finance-ai-course  (Windows)
```

### ③ 폴더 내용 확인
```bash
ls          # Mac/Linux
dir         # Windows
# README.md, requirements.txt, .env.example 등이 보이면 OK
```

### ④ Python 버전 확인
```bash
python --version
# Python 3.11.x  ← 이 숫자가 나오면 성공
```

### ⑤ 패키지 설치
```bash
pip install -r requirements.txt
# 설치 중 진행 상황이 출력됩니다 (5~10분 소요)
# 마지막에 "Successfully installed ..." 가 나오면 성공
```

### ⑥ .env 파일 생성
```bash
# Mac/Linux
cp .env.example .env

# Windows
copy .env.example .env
```

### ⑦ .env 파일에 Key 입력
```
VS Code 좌측 파일 탐색기에서 .env 클릭
각 항목의 "여기에_XXX_입력" 부분을 본인 Key로 교체
Ctrl+S 로 저장
```

### ⑧ Claude Code 실행 해보기
```bash
claude
# Claude가 반응하면 성공!
# 아래 메시지를 입력해보세요:
```
```
> 파이썬으로 "안녕하세요!" 를 출력하는 코드를 만들어줘
```
```bash
# Claude가 코드를 만들어줍니다
# 종료: /exit 또는 Ctrl+C
```

### ⑨ 환경 점검 실행
```bash
cd day1/01_setup
streamlit run check.py
# 브라우저가 자동으로 열립니다
# 모든 항목이 초록색이면 준비 완료!
# 종료: 터미널에서 Ctrl+C
```

---

## 💡 Claude Code 사용법 핵심

```bash
# 1. 터미널에서 실행
claude

# 2. 프로젝트 폴더에서 실행하면 해당 코드를 이해함
cd day1/02_kis_api
claude

# 3. 주요 명령어
/help    # 도움말
/clear   # 대화 초기화
/exit    # 종료

# 4. 파일 생성 요청 예시
> app.py 파일을 만들어서 KIS API로 삼성전자 현재가를 조회해줘

# 5. 오류 해결 요청 예시
> 아래 오류가 났어, 해결해줘:
> ModuleNotFoundError: No module named 'requests'
```

---

## ❓ Q&A

**Q. `pip install` 중 오류가 나요**
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

**Q. `claude` 명령어를 인식 못해요**
```bash
# 터미널을 완전히 닫고 다시 열기
# 또는
npx @anthropic-ai/claude-code
```

**Q. `.env` 파일이 안 보여요**
```
VS Code 좌측 탐색기에서 점(.)으로 시작하는 파일이 숨겨진 경우
탐색기 상단 필터 아이콘 → "숨김 파일 표시" 체크
```
