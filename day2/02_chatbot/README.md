# 📁 Day 2 · 02 · 투자 상담 AI 챗봇

## 이 실습에서 배우는 것
- Streamlit 채팅 UI (st.chat_input, st.chat_message)
- 멀티턴 대화 (대화 이력 유지)
- 스트리밍 응답 (글자가 하나씩 실시간 출력)
- 투자 전문가 페르소나 설정

---

## 📂 이 폴더의 파일 구성

```
day2/02_chatbot/
└── chatbot.py      ← 실습에서 Claude Code로 직접 만들기
```

> `chatbot.py` 는 **이 실습에서 직접 만듭니다.**
> 아래 순서대로 따라오세요.

---

## 사전 확인 — OpenAI API 연결이 되어 있어야 합니다

```bash
cd day2/01_openai
python hello_openai.py
# ✅ 답변이 출력되면 OK
cd ../02_chatbot
```

---

## 🖥 실습 순서

---

### STEP 1 · 폴더 이동

```bash
cd day2/02_chatbot
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

### STEP 3 · [Claude Code 실습] chatbot.py 만들기

아래 프롬프트를 **그대로 복사해서 붙여넣기** 하세요:

```
day2/02_chatbot/chatbot.py 파일을 만들어줘.

한국 주식 투자 상담 AI 챗봇 Streamlit 웹앱이야.

기본 설정:
  페이지 제목: "🤖 투자 AI 상담사"
  .env 파일: ../../.env 경로에서 읽기
  OpenAI 모델: gpt-4o-mini

시스템 프롬프트 설정:
  "당신은 한국 주식 투자 전문 AI 어시스턴트입니다.
   20년 이상의 한국 주식시장 분석 경험을 가지고 있습니다.
   구체적인 수치와 근거를 제시하며 답변하세요.
   전문 용어 사용 시 괄호 안에 설명을 추가하세요.
   모든 답변 마지막에 아래 문구를 추가하세요:
   ⚠️ 본 답변은 AI가 생성한 참고 정보이며
   실제 투자 결정은 본인 판단 및 전문가 상담을 통해 하세요."

기능 1 · 채팅 UI
  st.chat_input 으로 질문 입력창 만들기
  st.chat_message 로 대화 표시
    사용자: 👤 아이콘
    AI:     🤖 아이콘
  스트리밍 응답: st.write_stream 사용
    글자가 하나씩 실시간으로 출력되게 해줘

기능 2 · 멀티턴 대화 (대화 이력 유지)
  st.session_state.messages 로 대화 이력 저장
  API 호출 시 전체 이력을 함께 전달해줘
  이전 대화 맥락을 기억해서 답변하게 해줘

기능 3 · 사이드바
  모델 선택 (gpt-4o-mini / gpt-4o)
  답변 스타일 슬라이더 (temperature: 0.0 ~ 1.0, 기본값 0.3)
  대화 초기화 버튼
  예시 질문 버튼 5개 (클릭하면 자동 입력):
    "RSI 지표란 무엇인가요?"
    "이동평균선 골든크로스란?"
    "삼성전자 투자 시 주의사항은?"
    "ETF 투자 방법을 알려주세요"
    "PER, PBR 지표 설명해줘"

기타 조건:
  OPENAI_API_KEY 없으면 st.error 로 안내 후 st.stop()
  파일명: chatbot.py
```

---

### STEP 4 · chatbot.py 실행 확인

Claude Code가 파일을 만들면 **기존 터미널로 돌아가서** 실행:

```bash
streamlit run chatbot.py
```

브라우저에서 확인:

```
1. 입력창에 "안녕하세요! 당신은 누구인가요?" 입력 → 엔터
   → AI 자기소개가 스트리밍으로 출력되면 성공

2. "RSI 지표란 무엇인가요?" 입력
   → 투자 용어 설명 확인

3. "방금 설명한 RSI를 어떻게 실전에서 활용하나요?" 입력
   → 이전 대화(RSI 설명)를 기억하고 답변하면 멀티턴 성공

4. 사이드바 예시 질문 버튼 클릭
   → 자동으로 입력창에 질문이 입력되면 성공
```

---

### STEP 5 · 추가 실습 — 기능 더 넣어보기

**미션 1 · 대화 저장 기능**
```
chatbot.py 에 대화 내용을 텍스트 파일로 저장하는
"💾 대화 저장" 버튼을 사이드바에 추가해줘.
파일명: chat_YYYYMMDD_HHMMSS.txt
```

**미션 2 · 오늘의 투자 격언**
```
chatbot.py 사이드바에 오늘의 투자 격언을 추가해줘.
아래 목록에서 날짜 기준으로 하나씩 돌아가며 표시해줘:
"주식 시장은 성급한 사람에게서 인내심 있는 사람에게 돈을 이전하는 장치다 - 워런 버핏"
"위험은 자신이 무엇을 하는지 모를 때 온다 - 워런 버핏"
"시장을 이기려 하지 말고 시장에 참여하라 - 존 보글"
"분산투자는 무지에 대한 방어책이다 - 워런 버핏"
"쌀 때 사서 비쌀 때 파는 것이 전부다 - 앙드레 코스톨라니"
```

**미션 3 · 질문 카테고리 분류**
```
chatbot.py 에서 사용자 질문을 자동으로 분류해줘.
질문 왼쪽에 태그를 표시해줘:
  📈 기술적 분석  (RSI, MACD, 이동평균 관련)
  📊 기본적 분석  (PER, PBR, 재무제표 관련)
  💡 투자 전략    (포트폴리오, ETF 관련)
  ❓ 기타
```

---

## 📝 핵심 코드 패턴 (강의 참고)

### 멀티턴 대화 핵심 구조
```python
# 세션에 대화 이력 저장
if "messages" not in st.session_state:
    st.session_state.messages = []

# 새 메시지 추가
st.session_state.messages.append(
    {"role": "user", "content": 사용자입력}
)

# API 호출 시 전체 이력 전달
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[시스템프롬프트] + st.session_state.messages,
    stream=True
)
```

### 스트리밍 핵심 구조
```python
with st.chat_message("assistant"):
    # write_stream 이 스트리밍 자동 처리
    response = st.write_stream(stream)

# 스트리밍 완료 후 이력에 저장
st.session_state.messages.append(
    {"role": "assistant", "content": response}
)
```

---

## ❓ 자주 묻는 질문

**Q. 챗봇이 이전 대화를 기억 못해요**
```
st.session_state.messages 가 API 호출에 포함되지 않은 경우입니다.
Claude Code 에 요청:
"chatbot.py 에서 API 호출 시
 시스템 프롬프트 + 전체 대화 이력을 함께 전달하고 있는지 확인해줘."
```

**Q. 글자가 한꺼번에 출력돼요 (스트리밍이 안 돼요)**
```
stream=True 옵션과 st.write_stream 이 사용됐는지 확인하세요.
Claude Code 에 요청:
"chatbot.py 에서 스트리밍 응답이 되도록 수정해줘.
 client.chat.completions.create 에 stream=True 를 추가하고
 st.write_stream 으로 출력해줘."
```

**Q. 답변이 너무 길어요**
```
사이드바 슬라이더에서 temperature 를 낮추거나
Claude Code 에 요청:
"chatbot.py 시스템 프롬프트에
 '답변은 300자 이내로 간결하게 해줘' 를 추가해줘."
```

**Q. AuthenticationError 오류가 나요**
```
.env 파일의 OPENAI_API_KEY 확인
sk- 로 시작하는 전체 키가 올바른지 확인
```
