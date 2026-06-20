"""
투자 AI 어시스턴트 — KIS 대시보드 + RAG 챗봇 통합 앱
실행: streamlit run app.py
"""

import sys
import os
from pathlib import Path
from datetime import datetime, timedelta

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from dotenv import load_dotenv

# ── 환경 변수 ─────────────────────────────────────
load_dotenv(Path(__file__).parent / "../../.env")

# ── 모듈 경로 추가 ────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent / "../../day1/02_kis_api"))
sys.path.insert(0, str(Path(__file__).parent / "../05_rag"))

from kis_client import get_token, get_price, get_balance, make_headers, BASE_URL

# ── 페이지 설정 ───────────────────────────────────
st.set_page_config(
    page_title="📈 투자 AI 어시스턴트",
    page_icon="📈",
    layout="wide",
)

# ── 사이드바 메뉴 ──────────────────────────────────
with st.sidebar:
    st.title("📈 투자 AI 어시스턴트")
    page = st.radio(
        "메뉴",
        ["🏠 대시보드", "💹 주식 조회", "🤖 AI 챗봇"],
        label_visibility="collapsed",
    )

# ── 공통: KIS 토큰 캐시 ───────────────────────────
@st.cache_resource(show_spinner=False)
def init_token():
    try:
        return get_token(), None
    except Exception as e:
        return None, str(e)


def get_cached_token():
    if "kis_token" not in st.session_state:
        token, err = init_token()
        st.session_state.kis_token = token
        st.session_state.kis_token_err = err
    return st.session_state.kis_token, st.session_state.get("kis_token_err")


# ── 일봉 데이터 조회 (캔들차트용) ─────────────────
def get_daily_candles(token: str, ticker: str, days: int = 30) -> pd.DataFrame:
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-daily-price"

    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": ticker,
        "FID_PERIOD_DIV_CODE": "D",
        "FID_ORG_ADJ_PRC": "0",
    }
    resp = requests.get(
        url,
        headers=make_headers(token, "FHKST01010400"),
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if data.get("rt_cd") != "0":
        raise ValueError(data.get("msg1", "일봉 조회 실패"))

    rows = data.get("output2", [])
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = df[["stck_bsop_date", "stck_oprc", "stck_hgpr", "stck_lwpr", "stck_clpr", "acml_vol"]].copy()
    df.columns = ["date", "open", "high", "low", "close", "volume"]
    df = df[df["date"] != ""].dropna()
    for col in ["open", "high", "low", "close", "volume"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    df = df.sort_values("date").tail(days).reset_index(drop=True)
    return df


# ════════════════════════════════════════════════
# 🏠 대시보드
# ════════════════════════════════════════════════
if page == "🏠 대시보드":
    st.title("🏠 대시보드")

    token, token_err = get_cached_token()
    if token_err or token is None:
        st.warning(f"KIS API에 연결할 수 없습니다. .env 파일의 API 키를 확인하세요.\n\n오류: {token_err}")
        st.stop()

    with st.spinner("계좌 잔고 조회 중..."):
        try:
            bal = get_balance(token)
        except Exception as e:
            st.warning(f"잔고 조회 실패: {e}")
            st.stop()

    if bal.get("rt_cd") != "0":
        st.warning(f"잔고 조회 실패: {bal.get('msg1', '알 수 없는 오류')}")
        st.stop()

    summary = bal.get("output2", [{}])[0] if bal.get("output2") else {}
    holdings = bal.get("output1", [])

    total_eval = int(summary.get("tot_evlu_amt", 0))
    deposit    = int(summary.get("dnca_tot_amt", 0))
    profit     = int(summary.get("evlu_pfls_smtl_amt", 0))

    # ── 상단 지표 카드 3개 ────────────────────────
    c1, c2, c3 = st.columns(3)
    c1.metric("총 평가금액", f"{total_eval:,}원")
    c2.metric("예수금",      f"{deposit:,}원")
    c3.metric("평가손익",    f"{profit:+,}원", delta=f"{profit:+,}원")

    st.markdown("---")

    # ── 보유 종목 테이블 ──────────────────────────
    st.subheader("보유 종목")
    if holdings:
        rows = []
        for h in holdings:
            if not h.get("pdno"):
                continue
            rows.append({
                "종목명":   h.get("prdt_name", ""),
                "보유수량": int(float(h.get("hldg_qty", 0))),
                "평균단가": int(float(h.get("pchs_avg_pric", 0))),
                "현재가":   int(float(h.get("prpr", 0))),
                "평가손익": int(float(h.get("evlu_pfls_amt", 0))),
                "수익률":   float(h.get("evlu_erng_rt", 0)),
            })
        if rows:
            df_holdings = pd.DataFrame(rows)
            st.dataframe(
                df_holdings.style.format({
                    "보유수량": "{:,}",
                    "평균단가": "{:,}원",
                    "현재가":   "{:,}원",
                    "평가손익": "{:+,}원",
                    "수익률":   "{:.2f}%",
                }),
                use_container_width=True,
            )

            # ── 자산 배분 파이차트 ─────────────────
            st.subheader("자산 배분")
            labels = [r["종목명"] for r in rows]
            values = [r["현재가"] * r["보유수량"] for r in rows]
            if deposit > 0:
                labels.append("예수금")
                values.append(deposit)

            fig = go.Figure(go.Pie(labels=labels, values=values, hole=0.4))
            fig.update_layout(height=400, margin=dict(t=30, b=30))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("보유 중인 종목이 없습니다.")
    else:
        st.info("보유 중인 종목이 없습니다.")


# ════════════════════════════════════════════════
# 💹 주식 조회
# ════════════════════════════════════════════════
elif page == "💹 주식 조회":
    st.title("💹 주식 조회")

    POPULAR = {
        "삼성전자":  "005930",
        "SK하이닉스": "000660",
        "NAVER":     "035420",
        "카카오":    "035720",
        "현대차":    "005380",
    }

    if "stock_ticker" not in st.session_state:
        st.session_state.stock_ticker = "005930"

    # ── 인기 종목 버튼 ────────────────────────────
    st.markdown("**인기 종목 바로가기**")
    cols = st.columns(len(POPULAR))
    for col, (name, code) in zip(cols, POPULAR.items()):
        if col.button(f"{name}\n({code})"):
            st.session_state.stock_ticker = code

    # ── 종목코드 입력창 ───────────────────────────
    with st.form("stock_form"):
        ticker_input = st.text_input(
            "종목코드",
            value=st.session_state.stock_ticker,
            max_chars=6,
            placeholder="예: 005930",
        )
        submitted = st.form_submit_button("조회", use_container_width=True)

    if submitted:
        st.session_state.stock_ticker = ticker_input.strip()

    ticker = st.session_state.stock_ticker
    if not ticker:
        st.info("종목코드를 입력하세요.")
        st.stop()

    token, token_err = get_cached_token()
    if token_err or token is None:
        st.warning(f"KIS API 연결 실패: {token_err}")
        st.stop()

    # ── 현재가 조회 ───────────────────────────────
    with st.spinner(f"{ticker} 현재가 조회 중..."):
        try:
            price_data = get_price(token, ticker)
        except Exception as e:
            st.error(f"현재가 조회 실패: {e}")
            st.stop()

    cur_price  = int(price_data.get("stck_prpr", 0))
    change     = int(price_data.get("prdy_vrss", 0))
    chg_pct    = float(price_data.get("prdy_ctrt", 0))
    open_price = int(price_data.get("stck_oprc", 0))
    high_price = int(price_data.get("stck_hgpr", 0))
    low_price  = int(price_data.get("stck_lwpr", 0))
    volume     = int(price_data.get("acml_vol", 0))
    name_disp  = price_data.get("hts_kor_isnm", ticker)

    sign  = "▲" if change > 0 else ("▼" if change < 0 else "-")
    color = "red" if change > 0 else ("blue" if change < 0 else "gray")

    st.markdown(f"### {name_disp} ({ticker})")
    st.markdown(
        f"<h2 style='color:{color}'>{cur_price:,}원 "
        f"<span style='font-size:1rem'>{sign} {abs(change):,}원 ({chg_pct:+.2f}%)</span></h2>",
        unsafe_allow_html=True,
    )

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("시가",   f"{open_price:,}원")
    m2.metric("고가",   f"{high_price:,}원")
    m3.metric("저가",   f"{low_price:,}원")
    m4.metric("거래량", f"{volume:,}주")

    # ── 30일 캔들차트 ─────────────────────────────
    st.markdown("---")
    st.subheader("최근 30일 캔들차트")
    with st.spinner("일봉 데이터 조회 중..."):
        try:
            df_candle = get_daily_candles(token, ticker, days=30)
        except Exception as e:
            st.error(f"일봉 데이터 조회 실패: {e}")
            df_candle = pd.DataFrame()

    if not df_candle.empty:
        fig = go.Figure(go.Candlestick(
            x=df_candle["date"],
            open=df_candle["open"],
            high=df_candle["high"],
            low=df_candle["low"],
            close=df_candle["close"],
            increasing_line_color="red",
            decreasing_line_color="blue",
        ))
        fig.update_layout(
            title=f"{name_disp} 일봉 (최근 30일)",
            xaxis_title="날짜",
            yaxis_title="가격 (원)",
            xaxis_rangeslider_visible=False,
            height=450,
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("일봉 데이터를 가져올 수 없습니다.")


# ════════════════════════════════════════════════
# 🤖 AI 챗봇
# ════════════════════════════════════════════════
elif page == "🤖 AI 챗봇":
    st.title("🤖 AI 챗봇")

    TEST_QUESTIONS = [
        "삼성전자 최근 주가 흐름은?",
        "거래량이 가장 많았던 날은?",
        "SK하이닉스가 오른 날은?",
        "가장 많이 상승한 종목은?",
        "12월 삼성전자 주가는?",
    ]

    # ── 사이드바: 테스트 질문 & 초기화 ──────────
    with st.sidebar:
        st.markdown("---")
        st.markdown("**테스트 질문**")
        for q in TEST_QUESTIONS:
            if st.button(q, key=f"tq_{q}"):
                st.session_state.setdefault("messages", [])
                st.session_state["pending_question"] = q

        st.markdown("---")
        if st.button("🗑️ 대화 초기화"):
            st.session_state["messages"] = []
            st.session_state.pop("pending_question", None)
            st.rerun()

    # ── RAG 체인 로딩 ─────────────────────────────
    @st.cache_resource(show_spinner=False)
    def load_chain():
        try:
            from rag_chain import load_rag_chain
            chain, retriever = load_rag_chain()
            return chain, retriever, None
        except Exception as e:
            return None, None, str(e)

    with st.spinner("RAG 체인 초기화 중..."):
        chain, retriever, chain_err = load_chain()

    if chain_err or chain is None:
        st.error(f"RAG 체인 로딩 실패: {chain_err}")
        st.stop()

    # ── 대화 이력 초기화 ─────────────────────────
    if "messages" not in st.session_state:
        st.session_state["messages"] = []

    # ── 대화 이력 출력 ───────────────────────────
    for msg in st.session_state["messages"]:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg["role"] == "assistant" and msg.get("sources"):
                with st.expander("📄 참고 데이터 출처"):
                    for i, src in enumerate(msg["sources"], 1):
                        meta = src.metadata
                        date = meta.get("date", "날짜 없음")
                        name = meta.get("name", "종목 없음")
                        code = meta.get("code", "코드 없음")
                        preview = src.page_content[:80].replace("\n", " ")
                        st.markdown(f"**{i}.** [{date}] {name}({code}): {preview}...")

    # ── 사용자 입력 처리 ─────────────────────────
    pending = st.session_state.pop("pending_question", None)
    user_input = pending or st.chat_input("질문을 입력하세요...")

    if user_input:
        st.session_state["messages"].append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("답변 생성 중..."):
                try:
                    source_docs = retriever.invoke(user_input)
                    answer = chain.invoke(user_input)
                except Exception as e:
                    st.error(f"답변 생성 실패: {e}")
                    st.stop()

            st.markdown(answer)

            if source_docs:
                with st.expander("📄 참고 데이터 출처"):
                    for i, src in enumerate(source_docs, 1):
                        meta = src.metadata
                        date = meta.get("date", "날짜 없음")
                        name = meta.get("name", "종목 없음")
                        code = meta.get("code", "코드 없음")
                        preview = src.page_content[:80].replace("\n", " ")
                        st.markdown(f"**{i}.** [{date}] {name}({code}): {preview}...")

        st.session_state["messages"].append({
            "role": "assistant",
            "content": answer,
            "sources": source_docs,
        })
