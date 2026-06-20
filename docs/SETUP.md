# ⚙️ 개발환경 세팅 완전 가이드

> 강의 시작 전 반드시 완료해야 하는 환경 세팅 가이드입니다.  
> **처음 설치하는 분도 이 문서만 보면 혼자 완료할 수 있습니다.**  
> 막히는 부분은 강사에게 바로 질문하세요.

---

## 📋 설치 순서 한눈에 보기

```
STEP 1 · Git 설치
STEP 2 · Python 3.11 설치
STEP 3 · VS Code 설치
STEP 4 · Node.js 설치
STEP 5 · Claude Code 설치
STEP 6 · 저장소 복사 (git clone)
STEP 7 · 가상환경 생성 + 패키지 설치
STEP 8 · API Key 설정
STEP 9 · 동작 확인
```

---

## STEP 1 · Git 설치

Git은 코드를 버전 관리하고 GitHub에 올리는 도구입니다.

### 설치 전 확인
```bash
git --version
# git version 2.x.x 가 나오면 이미 설치됨 → STEP 2로 이동
```

### Windows 설치
```
1. https://git-scm.com/download/win 접속
2. "Click here to download" 클릭 (64-bit 자동 선택)
3. 설치 파일 실행
4. 모든 옵션 기본값 그대로 → Next 계속 → Install
5. 설치 완료 후 터미널(명령 프롬프트) 재실행
```

### Mac 설치
```bash
# 터미널에서 실행
xcode-select --install
# 팝업이 뜨면 "설치" 클릭 → 완료까지 5~10분 소요
```

### 설치 확인
```bash
git --version
# git version 2.x.x 출력되면 성공
```

### Git 사용자 정보 설정 (최초 1회)
```bash
git config --global user.name "본인이름"
git config --global user.email "본인이메일@gmail.com"

# 설정 확인
git config --global --list
```

---

## STEP 2 · Python 3.11 설치

Python은 본 과정에서 사용하는 프로그래밍 언어입니다.

### 설치 전 확인
```bash
python --version
# Python 3.11.x 가 나오면 이미 설치됨 → STEP 3으로 이동
# Python 3.12, 3.13도 사용 가능하지만 3.11 권장
```

### Windows 설치

```
1. https://www.python.org/downloads/ 접속
2. "Download Python 3.11.x" 버튼 클릭
   (3.11.x 버전을 직접 받으려면)
   → https://www.python.org/downloads/release/python-3119/
   → 페이지 하단 "Windows installer (64-bit)" 클릭
3. 설치 파일 실행
   ⚠️ 반드시! "Add Python 3.11 to PATH" 체크박스 선택
4. "Install Now" 클릭
5. 설치 완료 후 "Close"
6. 터미널(명령 프롬프트) 완전히 닫고 새로 열기
```

> ❗ PATH 체크를 빠뜨리면 python 명령이 인식되지 않습니다.  
> 실수했다면 제어판 → 프로그램 제거 → Python 제거 후 재설치하세요.

### Mac 설치
```bash
# 방법 1: 공식 설치 파일 (권장)
# https://www.python.org/downloads/macos/ 에서
# "macOS 64-bit universal2 installer" 다운로드 후 설치

# 방법 2: Homebrew로 설치
brew install python@3.11
```

### 설치 확인
```bash
python --version
# Python 3.11.x 출력되면 성공

pip --version
# pip 24.x.x ... python 3.11 출력되면 성공
```

> Windows에서 `python` 대신 `py` 를 입력해야 하는 경우:
> ```bash
> py --version   # 이것도 OK
> py -m pip --version
> ```

---

## STEP 3 · VS Code 설치

VS Code(Visual Studio Code)는 코드를 작성하고 실행하는 편집기입니다.  
무료이며 AI 코딩 도구와 연동이 가장 잘 됩니다.

### 다운로드 및 설치

```
1. https://code.visualstudio.com 접속
2. 운영체제에 맞는 버튼 클릭하여 다운로드
   - Windows: "Download for Windows" 클릭
   - Mac: "Download for macOS" 클릭
3. 설치 파일 실행
   Windows 옵션 중 아래 두 가지 체크 권장:
   ✅ "Add 'Open with Code' action to Windows Explorer file context menu"
   ✅ "Add to PATH (requires shell restart)"
4. Install 클릭 → 완료
```

### VS Code 첫 실행

```
1. VS Code 실행
2. 한국어 팩 설치 (선택 사항)
   왼쪽 아이콘 중 퍼즐 모양 (Extensions) 클릭
   → 검색창에 "Korean" 입력
   → "Korean Language Pack for VS Code" → Install
   → VS Code 재시작
```

### 필수 확장 설치

VS Code 왼쪽 아이콘 중 퍼즐 모양(Extensions, `Ctrl+Shift+X`)을 클릭합니다.

```
검색 → 설치 목록:

① Python
   검색: "Python"
   제작: Microsoft
   → Install 클릭

② Pylance
   검색: "Pylance"
   제작: Microsoft
   → Install 클릭 (Python 설치 시 자동으로 함께 설치됨)
```

### VS Code에서 터미널 열기

이 과정에서 가장 많이 사용하는 기능입니다.

```
방법 1: 단축키  Ctrl + `  (백틱 — 키보드 왼쪽 위 숫자 1 왼쪽 키)
방법 2: 메뉴 → Terminal → New Terminal
방법 3: 메뉴 → 보기 → 터미널 (한국어 팩 설치 시)
```

터미널이 VS Code 하단에 열리면 성공입니다.  
이후 모든 명령어는 이 터미널에서 입력합니다.

---

## STEP 4 · Node.js 설치

Node.js는 Claude Code를 실행하는 데 필요한 런타임입니다.

### 설치 전 확인
```bash
node --version
# v18.x.x 이상이면 이미 설치됨 → STEP 5로 이동
```

### Windows / Mac 설치
```
1. https://nodejs.org 접속
2. "LTS" 버튼 클릭 (안정 버전, 권장)
   현재 버전: v20.x.x LTS
3. 설치 파일 실행 → 기본값으로 설치
4. 터미널 재실행
```

### 설치 확인
```bash
node --version
# v20.x.x 출력되면 성공

npm --version
# 10.x.x 출력되면 성공
```

---

## STEP 5 · Claude Code 설치

Claude Code는 VS Code 터미널에서 AI와 대화하며 코드를 작성하는 도구입니다.  
`claude` 명령을 입력하면 AI가 코드 생성, 수정, 오류 해결을 도와줍니다.

### 설치

VS Code 터미널에서 아래 명령어를 입력합니다:

```bash
npm install -g @anthropic-ai/claude-code
```

### 설치 확인
```bash
claude --version
# claude-code/x.x.x 출력되면 성공
```

### 로그인 (Anthropic 계정 필요)

```bash
claude
# 처음 실행 시 브라우저가 자동으로 열립니다
# Anthropic 계정으로 로그인 (없으면 무료 회원가입)
# 로그인 완료 후 터미널로 자동 돌아옴
# ">" 프롬프트가 보이면 성공
# 종료: /exit 또는 Ctrl+C
```

> 💡 Claude Code 사용 요금:
> - Claude.ai Pro 구독자: 포함 (별도 요금 없음)
> - 무료 플랜: 일정 한도 내 무료 사용 가능

---

## STEP 6 · 저장소 복사 (git clone)

### GitHub 계정 만들기 (없는 경우)
```
1. https://github.com 접속
2. Sign up 클릭
3. 이메일, 비밀번호, 사용자명 입력 후 가입
```

### 저장소 Fork (내 계정에 복사본 생성)
```
1. https://github.com/강사계정/finance-ai-course 접속
   (강사가 강의 당일 URL 공유)
2. 우측 상단 "Fork" 버튼 클릭
3. "Create fork" 클릭
4. 내 계정에 복사본이 생성됨
```

### 내 컴퓨터로 다운로드 (clone)

VS Code 터미널에서:

```bash
# 1. 원하는 위치로 이동 (예: 바탕화면)
cd Desktop                              # Windows
cd ~/Desktop                            # Mac

# 2. 저장소 복사 ("본인ID"를 본인 GitHub 아이디로 변경)
git clone https://github.com/본인ID/finance-ai-course.git

# 3. 폴더로 이동
cd finance-ai-course

# 4. VS Code로 열기
code .
# VS Code가 이 폴더를 열면서 새 창이 뜹니다
```

> VS Code가 열리면 좌측 탐색기에 파일 목록이 보입니다.  
> `README.md`, `requirements.txt`, `.env.example` 등이 보이면 성공입니다.

---

## STEP 7 · 가상환경 생성 + 패키지 설치

가상환경(venv)은 이 프로젝트 전용 Python 공간입니다.  
다른 프로젝트와 패키지가 충돌하지 않도록 격리합니다.

### 가상환경 생성

VS Code에서 `finance-ai-course` 폴더가 열린 상태에서  
터미널(`Ctrl+\``)을 열고 아래를 입력합니다:

```bash
# 현재 위치 확인 (finance-ai-course 폴더 안이어야 함)
pwd
# /Users/.../finance-ai-course  또는
# C:\Users\...\finance-ai-course  가 나와야 함

# 가상환경 생성 (.venv 라는 이름으로)
python -m venv .venv
```

### 가상환경 활성화

```bash
# Windows
.venv\Scripts\activate

# Mac / Linux
source .venv/bin/activate
```

활성화 성공 시 터미널 앞에 `(.venv)` 가 붙습니다:
```
(.venv) C:\Users\홈\finance-ai-course>    ← Windows
(.venv) 홈@MacBook finance-ai-course %   ← Mac
```

> ⚠️ VS Code를 새로 열거나 터미널을 새로 열 때마다  
> 가상환경을 다시 활성화해야 합니다.

### VS Code에서 Python 인터프리터 설정 (가상환경 자동 활성화)

```
1. Ctrl+Shift+P 입력
2. "Python: Select Interpreter" 검색 후 클릭
3. ".venv" 가 포함된 항목 선택
   예: Python 3.11.x ('.venv': venv)
4. 이후 VS Code 터미널을 새로 열면 자동으로 (.venv) 활성화
```

### 패키지 설치

가상환경이 활성화된 상태에서:

```bash
# pip 최신 버전으로 업그레이드 (권장)
python -m pip install --upgrade pip

# 전체 패키지 한 번에 설치
pip install -r requirements.txt

# 설치 완료까지 5~10분 소요
# 마지막에 "Successfully installed ..." 가 나오면 성공
```

### 패키지 설치 확인

```bash
python -c "import streamlit;   print('✅ streamlit  ', streamlit.__version__)"
python -c "import openai;      print('✅ openai     ', openai.__version__)"
python -c "import langchain;   print('✅ langchain  ', langchain.__version__)"
python -c "import chromadb;    print('✅ chromadb   ', chromadb.__version__)"
python -c "import pandas;      print('✅ pandas     ', pandas.__version__)"
python -c "import plotly;      print('✅ plotly     ', plotly.__version__)"
# 모두 ✅ 가 출력되면 성공
```

### 가상환경 비활성화 (강의 종료 후)

```bash
deactivate
# (.venv) 표시가 사라지면 비활성화 완료
```

---

## STEP 8 · API Key 설정

### .env 파일 생성

```bash
# Windows
copy .env.example .env

# Mac / Linux
cp .env.example .env
```

### VS Code에서 .env 편집

```
VS Code 좌측 파일 탐색기에서 .env 파일 클릭
(점(.)으로 시작하는 파일이 안 보이면: 탐색기 상단 필터 → 숨김 파일 표시)

아래 형식으로 각 값 입력:
```

```ini
# 한국투자증권 (모의투자)
KIS_APP_KEY=PSxxxxxxxxxxxxxxxxxxxxxxxxx
KIS_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxx
KIS_ACCOUNT_NO=12345678

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxx

# 금융위원회 공공데이터
FSS_API_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

`Ctrl+S` 로 저장

> ⚠️ "여기에_XXX_입력" 문자를 그대로 두면 오류가 납니다.  
> API Key 발급 방법은 `docs/API_KEYS.md` 를 참고하세요.

---

## STEP 9 · 동작 확인

### 전체 환경 자동 점검

```bash
cd day1/01_setup
streamlit run check.py
```

브라우저가 자동으로 열리고 점검 화면이 나타납니다.  
모든 항목이 ✅ 초록색이면 강의 시작 준비 완료입니다!

항목이 ❌ 빨간색이면 해당 항목의 💡 안내를 따라 수정 후 새로고침하세요.

---

## ✅ 최종 체크리스트

아래 명령어를 터미널에 하나씩 입력하여 모두 성공하는지 확인하세요:

```bash
# 1. Git
git --version
# ✅ git version 2.x.x

# 2. Python
python --version
# ✅ Python 3.11.x

# 3. 가상환경 활성화 확인
# 터미널 앞에 (.venv) 가 붙어 있어야 함

# 4. Streamlit
python -c "import streamlit; print('✅ Streamlit', streamlit.__version__)"

# 5. OpenAI
python -c "import openai; print('✅ OpenAI', openai.__version__)"

# 6. Claude Code
claude --version
# ✅ claude-code/x.x.x

# 7. .env 확인
python -c "
from dotenv import load_dotenv
import os
load_dotenv('.env')
key = os.getenv('KIS_APP_KEY','미입력')
print('✅ KIS_APP_KEY:', key[:6]+'...' if len(key)>6 else '❌ 미입력')
"

# 8. 환경 점검 앱
cd day1/01_setup && streamlit run check.py
# 브라우저에서 모두 초록색 확인
```

---

## 🆘 자주 발생하는 오류

### `python` 명령이 없음 (Windows)
```bash
# 대안 1
py --version

# 대안 2: PATH 재설정 후 터미널 재시작
# 제어판 → 시스템 → 고급 → 환경 변수 → Path에 Python 경로 추가
# 기본 경로: C:\Users\본인이름\AppData\Local\Programs\Python\Python311\
```

### `(.venv)` 가 사라짐 (터미널 재시작 후)
```bash
# 매번 활성화 필요
.venv\Scripts\activate    # Windows
source .venv/bin/activate # Mac/Linux
```

### `pip install` 중 오류
```bash
# pip 업그레이드 후 재시도
python -m pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### `claude` 명령이 없음
```bash
# 재설치
npm install -g @anthropic-ai/claude-code
# 또는 경로 재로딩
source ~/.bashrc   # Mac/Linux
# Windows: 터미널 완전히 닫고 새로 열기
```

### `streamlit` 포트 충돌
```bash
streamlit run app.py --server.port 8502
```

### SSL 오류
```bash
pip install --upgrade certifi
```
