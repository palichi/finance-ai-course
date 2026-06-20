"""
KIS OpenAPI 모의투자 — 주식 현재가 조회 Streamlit 앱
실행: streamlit run app.py
"""

import streamlit as st
from kis_client import get_token, get_price

st.set_page_config(page_title="KIS 주식 현재가", page_icon="📈", layout="centered")
st.title("📈 KIS 모의투자 — 주식 현재가 조회")

# ── Access Token (세션 캐시) ──────────────────────
if "token" not in st.session_state:
    st.session_state.token = None

if st.session_state.token is None:
    with st.spinner("Access Token 발급 중..."):
        try:
            st.session_state.token = get_token()
            st.success("토큰 발급 완료")
        except Exception as e:
            st.error(f"토큰 발급 실패: {e}")
            st.stop()

# ── 종목코드 입력 ─────────────────────────────────
with st.form("price_form"):
    ticker = st.text_input(
        "종목코드",
        value="005930",
        placeholder="예: 005930 (삼성전자)",
        max_chars=6,
    )
    submitted = st.form_submit_button("조회", use_container_width=True)

# ── 현재가 조회 및 표시 ───────────────────────────
if submitted:
    if not ticker.strip():
        st.warning("종목코드를 입력하세요.")
    else:
        with st.spinner(f"{ticker} 조회 중..."):
            try:
                data = get_price(st.session_state.token, ticker.strip())
            except Exception as e:
                st.error(f"조회 실패: {e}")
                st.stop()

        cur_price  = int(data.get("stck_prpr", 0))
        change     = int(data.get("prdy_vrss", 0))
        chg_pct    = float(data.get("prdy_ctrt", 0))
        open_price = int(data.get("stck_oprc", 0))
        high_price = int(data.get("stck_hgpr", 0))
        low_price  = int(data.get("stck_lwpr", 0))
        volume     = int(data.get("acml_vol", 0))

        sign   = "▲" if change > 0 else ("▼" if change < 0 else "-")
        color  = "red" if change > 0 else ("blue" if change < 0 else "gray")

        st.markdown("---")
        st.markdown(f"### 현재가")
        st.markdown(
            f"<h2 style='color:{color}'>{cur_price:,}원 "
            f"<span style='font-size:1rem'>{sign} {abs(change):,}원 ({chg_pct:+.2f}%)</span></h2>",
            unsafe_allow_html=True,
        )

        col1, col2, col3 = st.columns(3)
        col1.metric("시가", f"{open_price:,}원")
        col2.metric("고가", f"{high_price:,}원")
        col3.metric("저가", f"{low_price:,}원")

        st.metric("거래량", f"{volume:,}주")

        with st.expander("원본 응답 데이터 보기"):
            st.json(data)
