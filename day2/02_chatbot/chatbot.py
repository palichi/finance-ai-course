import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv("../../.env")

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    st.error("OPENAI_API_KEY가 설정되지 않았습니다. ../../.env 파일을 확인하세요.")
    st.stop()

client = OpenAI(api_key=api_key)

SYSTEM_PROMPT = """당신은 한국 주식 투자 전문 AI 어시스턴트입니다.
20년 이상의 한국 주식시장 분석 경험을 가지고 있습니다.
구체적인 수치와 근거를 제시하며 답변하세요.
전문 용어 사용 시 괄호 안에 설명을 추가하세요.
모든 답변 마지막에 아래 문구를 추가하세요:
⚠️ 본 답변은 AI가 생성한 참고 정보이며 실제 투자 결정은 본인 판단 및 전문가 상담을 통해 하세요."""

TAG_COLORS = {
    "📈 기술적 분석": "background:#fff3cd;color:#856404;",
    "📊 기본적 분석": "background:#cce5ff;color:#004085;",
    "💡 투자 전략":   "background:#d4edda;color:#155724;",
    "❓ 기타":        "background:#e2e3e5;color:#383d41;",
}

def classify_question(text):
    t = text.upper()
    if any(k in t for k in ["RSI", "MACD", "이동평균", "골든크로스", "데드크로스", "볼린저", "스토캐스틱", "기술적"]):
        return "📈 기술적 분석"
    if any(k in t for k in ["PER", "PBR", "EPS", "ROE", "재무제표", "순이익", "매출", "배당", "기본적"]):
        return "📊 기본적 분석"
    if any(k in t for k in ["ETF", "포트폴리오", "분산투자", "장기투자", "가치투자", "전략", "펀드"]):
        return "💡 투자 전략"
    return "❓ 기타"

def tag_badge(tag):
    style = TAG_COLORS.get(tag, "background:#e2e3e5;color:#383d41;")
    return f'<span style="font-size:0.78em;padding:2px 10px;border-radius:12px;font-weight:bold;{style}">{tag}</span>'


st.set_page_config(page_title="🤖 투자 AI 상담사", page_icon="🤖")
st.title("🤖 투자 AI 상담사")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 사이드바
with st.sidebar:
    st.header("설정")

    model = st.selectbox("모델 선택", ["gpt-4o-mini", "gpt-4o"])
    temperature = st.slider("답변 스타일 (Temperature)", 0.0, 1.0, 0.3, 0.1)

    if st.button("대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    has_messages = bool(st.session_state.messages)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    lines = []
    for msg in st.session_state.messages:
        role = "사용자" if msg["role"] == "user" else "AI"
        lines.append(f"[{role}]\n{msg['content']}\n")
    st.download_button(
        label="💾 대화 저장",
        data="\n".join(lines),
        file_name=f"chat_{timestamp}.txt",
        mime="text/plain",
        use_container_width=True,
        disabled=not has_messages,
    )

    st.divider()
    quotes = [
        "주식 시장은 성급한 사람에게서 인내심 있는 사람에게 돈을 이전하는 장치다 - 워런 버핏",
        "위험은 자신이 무엇을 하는지 모를 때 온다 - 워런 버핏",
        "시장을 이기려 하지 말고 시장에 참여하라 - 존 보글",
        "분산투자는 무지에 대한 방어책이다 - 워런 버핏",
        "쌀 때 사서 비쌀 때 파는 것이 전부다 - 앙드레 코스톨라니",
    ]
    today_quote = quotes[datetime.today().toordinal() % len(quotes)]
    st.subheader("💡 오늘의 투자 격언")
    st.info(today_quote)

    st.divider()
    st.subheader("예시 질문")
    example_questions = [
        "RSI 지표란 무엇인가요?",
        "이동평균선 골든크로스란?",
        "삼성전자 투자 시 주의사항은?",
        "ETF 투자 방법을 알려주세요",
        "PER, PBR 지표 설명해줘",
    ]
    for question in example_questions:
        if st.button(question, use_container_width=True):
            st.session_state.pending_input = question
            st.rerun()

# 이전 대화 표시
for message in st.session_state.messages:
    avatar = "👤" if message["role"] == "user" else "🤖"
    with st.chat_message(message["role"], avatar=avatar):
        if message["role"] == "user":
            tag = message.get("tag", classify_question(message["content"]))
            st.markdown(f"{tag_badge(tag)}<br>{message['content']}", unsafe_allow_html=True)
        else:
            st.markdown(message["content"])

# 예시 질문 버튼으로 입력된 경우 처리
pending = st.session_state.pop("pending_input", None)

user_input = st.chat_input("투자 관련 질문을 입력하세요...") or pending

if user_input:
    tag = classify_question(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input, "tag": tag})
    with st.chat_message("user", avatar="👤"):
        st.markdown(f"{tag_badge(tag)}<br>{user_input}", unsafe_allow_html=True)

    messages_for_api = [{"role": "system", "content": SYSTEM_PROMPT}] + [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]

    with st.chat_message("assistant", avatar="🤖"):
        stream = client.chat.completions.create(
            model=model,
            messages=messages_for_api,
            temperature=temperature,
            stream=True,
        )
        response = st.write_stream(stream)

    st.session_state.messages.append({"role": "assistant", "content": response})
    st.rerun()
