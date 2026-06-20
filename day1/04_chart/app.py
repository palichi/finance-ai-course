"""
KIS OpenAPI 모의투자 — 주식 캔들차트 & 기술지표 Streamlit 앱
실행: streamlit run app.py
"""

import os
from datetime import datetime, timedelta

import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from dotenv import load_dotenv
from plotly.subplots import make_subplots

load_dotenv("../../.env")

BASE_URL   = "https://openapivts.koreainvestment.com:29443"
APP_KEY    = os.getenv("KIS_APP_KEY", "")
APP_SECRET = os.getenv("KIS_APP_SECRET", "")

POPULAR_STOCKS = {
    "삼성전자": "005930",
    "SK하이닉스": "000660",
    "NAVER": "035420",
    "카카오": "035720",
    "현대차": "005380",
}

# ── Token ──────────────────────────────────────────────────────────────────

@st.cache_data(ttl=3600 * 23)
def get_token() -> str:
    url  = f"{BASE_URL}/oauth2/tokenP"
    body = {"grant_type": "client_credentials", "appkey": APP_KEY, "appsecret": APP_SECRET}
    resp = requests.post(url, json=body, timeout=10)
    resp.raise_for_status()
    return resp.json()["access_token"]


def make_headers(token: str, tr_id: str) -> dict:
    return {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey":    APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id":     tr_id,
        "custtype":  "P",
    }


# ── 일봉 데이터 수집 ────────────────────────────────────────────────────────

@st.cache_data(ttl=600)
def fetch_ohlcv(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    token = get_token()
    url   = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice"
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD":         ticker,
        "FID_INPUT_DATE_1":       start_date,
        "FID_INPUT_DATE_2":       end_date,
        "FID_PERIOD_DIV_CODE":    "D",
        "FID_ORG_ADJ_PRC":        "0",
    }
    resp = requests.get(
        url,
        headers=make_headers(token, "FHKST03010100"),
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    if data.get("rt_cd") != "0":
        raise ValueError(data.get("msg1", "API 오류"))

    rows = data.get("output2", [])
    if not rows:
        return pd.DataFrame()

    df = pd.DataFrame(rows)
    df = df[df["stck_bsop_date"].str.strip() != ""]
    df["date"]   = pd.to_datetime(df["stck_bsop_date"], format="%Y%m%d")
    df["open"]   = pd.to_numeric(df["stck_oprc"],  errors="coerce")
    df["high"]   = pd.to_numeric(df["stck_hgpr"],  errors="coerce")
    df["low"]    = pd.to_numeric(df["stck_lwpr"],  errors="coerce")
    df["close"]  = pd.to_numeric(df["stck_clpr"],  errors="coerce")
    df["volume"] = pd.to_numeric(df["acml_vol"],   errors="coerce")
    df = df[["date", "open", "high", "low", "close", "volume"]].dropna()
    df = df.sort_values("date").reset_index(drop=True)
    return df


# ── 기술지표 계산 ──────────────────────────────────────────────────────────

def calc_ma(df: pd.DataFrame, periods: list[int]) -> pd.DataFrame:
    for p in periods:
        df[f"MA{p}"] = df["close"].rolling(p).mean()
    return df


def calc_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain  = delta.clip(lower=0).rolling(period).mean()
    loss  = (-delta.clip(upper=0)).rolling(period).mean()
    rs    = gain / loss.replace(0, float("nan"))
    return 100 - 100 / (1 + rs)


def calc_macd(series: pd.Series, fast=12, slow=26, signal=9):
    ema_fast   = series.ewm(span=fast, adjust=False).mean()
    ema_slow   = series.ewm(span=slow, adjust=False).mean()
    macd_line  = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    histogram  = macd_line - signal_line
    return macd_line, signal_line, histogram


# ── 차트 빌더 ──────────────────────────────────────────────────────────────

def build_chart(df: pd.DataFrame, show_ma: dict, indicator: str) -> go.Figure:
    n_rows    = 3 if indicator != "없음" else 2
    row_heights = [0.55, 0.15, 0.30] if n_rows == 3 else [0.70, 0.30]

    fig = make_subplots(
        rows=n_rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        row_heights=row_heights,
    )

    # 캔들 색상
    up_color   = "#FF3B3B"
    down_color = "#0066FF"
    candle_colors = [up_color if c >= o else down_color for o, c in zip(df["open"], df["close"])]

    # 캔들차트
    fig.add_trace(
        go.Candlestick(
            x=df["date"],
            open=df["open"], high=df["high"],
            low=df["low"],   close=df["close"],
            increasing_line_color=up_color,
            decreasing_line_color=down_color,
            increasing_fillcolor=up_color,
            decreasing_fillcolor=down_color,
            name="캔들",
            showlegend=False,
        ),
        row=1, col=1,
    )

    # 이동평균선
    ma_styles = {"MA5": ("MA5", "#FFD700"), "MA20": ("MA20", "#00CC44"), "MA60": ("MA60", "#9B59B6")}
    for key, (col, color) in ma_styles.items():
        if show_ma.get(key) and col in df.columns:
            fig.add_trace(
                go.Scatter(x=df["date"], y=df[col], name=key, line=dict(color=color, width=1.2)),
                row=1, col=1,
            )

    # 거래량
    fig.add_trace(
        go.Bar(
            x=df["date"], y=df["volume"],
            marker_color=candle_colors,
            name="거래량", showlegend=False,
        ),
        row=2, col=1,
    )

    # 보조지표
    if indicator == "RSI" and n_rows == 3:
        rsi = calc_rsi(df["close"])
        fig.add_trace(
            go.Scatter(x=df["date"], y=rsi, name="RSI(14)", line=dict(color="#F39C12", width=1.5)),
            row=3, col=1,
        )
        for level, color in [(70, "rgba(255,59,59,0.4)"), (30, "rgba(0,102,255,0.4)")]:
            fig.add_hline(y=level, line_dash="dash", line_color=color, row=3, col=1)

    elif indicator == "MACD" and n_rows == 3:
        macd_line, signal_line, histogram = calc_macd(df["close"])
        hist_colors = [up_color if v >= 0 else down_color for v in histogram]
        fig.add_trace(
            go.Bar(x=df["date"], y=histogram, name="히스토그램",
                   marker_color=hist_colors, showlegend=False),
            row=3, col=1,
        )
        fig.add_trace(
            go.Scatter(x=df["date"], y=macd_line, name="MACD", line=dict(color="#F39C12", width=1.3)),
            row=3, col=1,
        )
        fig.add_trace(
            go.Scatter(x=df["date"], y=signal_line, name="Signal", line=dict(color="#E74C3C", width=1.3)),
            row=3, col=1,
        )

    fig.update_layout(
        height=700,
        plot_bgcolor="#0E1117",
        paper_bgcolor="#0E1117",
        font=dict(color="#FAFAFA"),
        xaxis_rangeslider_visible=False,
        legend=dict(orientation="h", y=1.01, x=0),
        margin=dict(l=10, r=10, t=30, b=10),
    )
    for i in range(1, n_rows + 1):
        fig.update_yaxes(gridcolor="#2A2A2A", row=i, col=1)
        fig.update_xaxes(gridcolor="#2A2A2A", row=i, col=1)

    return fig


# ── 기술적 분석 요약 ────────────────────────────────────────────────────────

def show_summary(df: pd.DataFrame) -> None:
    rsi = calc_rsi(df["close"]).iloc[-1]
    macd_line, signal_line, _ = calc_macd(df["close"])
    last_macd   = macd_line.iloc[-1]
    last_signal = signal_line.iloc[-1]
    prev_macd   = macd_line.iloc[-2] if len(macd_line) > 1 else last_macd
    prev_signal = signal_line.iloc[-2] if len(signal_line) > 1 else last_signal

    close = df["close"].iloc[-1]
    ma5   = df["MA5"].iloc[-1]  if "MA5"  in df.columns else None
    ma20  = df["MA20"].iloc[-1] if "MA20" in df.columns else None
    ma60  = df["MA60"].iloc[-1] if "MA60" in df.columns else None

    # RSI 신호
    if rsi >= 70:
        rsi_signal, rsi_color = "과매수 ⚠️", "#FF3B3B"
    elif rsi <= 30:
        rsi_signal, rsi_color = "과매도 ⚠️", "#0066FF"
    else:
        rsi_signal, rsi_color = "중립", "#888888"

    # MA 배열
    valid_mas = {k: v for k, v in {"MA5": ma5, "MA20": ma20, "MA60": ma60}.items() if v is not None}
    if len(valid_mas) >= 2:
        values = list(valid_mas.values())
        if all(values[i] > values[i+1] for i in range(len(values)-1)):
            ma_signal, ma_color = "정배열 📈", "#FF3B3B"
        elif all(values[i] < values[i+1] for i in range(len(values)-1)):
            ma_signal, ma_color = "역배열 📉", "#0066FF"
        else:
            ma_signal, ma_color = "혼조", "#888888"
    else:
        ma_signal, ma_color = "-", "#888888"

    # MACD 신호 (골든/데드 크로스)
    golden = (prev_macd <= prev_signal) and (last_macd > last_signal)
    dead   = (prev_macd >= prev_signal) and (last_macd < last_signal)
    if golden:
        macd_signal, macd_color = "골든크로스 🌟", "#FF3B3B"
    elif dead:
        macd_signal, macd_color = "데드크로스 ☠️", "#0066FF"
    elif last_macd > last_signal:
        macd_signal, macd_color = "MACD > Signal", "#FF8C00"
    else:
        macd_signal, macd_color = "MACD < Signal", "#888888"

    st.markdown("### 기술적 분석 요약")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("RSI (14일)", f"{rsi:.1f}")
        st.markdown(f"<span style='color:{rsi_color};font-weight:bold'>{rsi_signal}</span>",
                    unsafe_allow_html=True)
    with c2:
        st.metric("이동평균 배열", "")
        st.markdown(f"<span style='color:{ma_color};font-weight:bold'>{ma_signal}</span>",
                    unsafe_allow_html=True)
    with c3:
        st.metric("MACD 방향", "")
        st.markdown(f"<span style='color:{macd_color};font-weight:bold'>{macd_signal}</span>",
                    unsafe_allow_html=True)


# ── Streamlit UI ───────────────────────────────────────────────────────────

st.set_page_config(page_title="📊 주식 차트 분석", layout="wide")
st.title("📊 주식 차트 분석")

# ── 사이드바 ─────────────────────────────────────────────────────────────

with st.sidebar:
    st.header("종목 선택")

    if "ticker" not in st.session_state:
        st.session_state["ticker"] = "005930"

    ticker_input = st.text_input("종목코드", value=st.session_state["ticker"], max_chars=6)

    st.markdown("**인기 종목**")
    cols = st.columns(2)
    buttons = list(POPULAR_STOCKS.items())
    for i, (name, code) in enumerate(buttons):
        if cols[i % 2].button(name, key=f"btn_{code}", use_container_width=True):
            st.session_state["ticker"] = code
            st.rerun()

    st.divider()

    period_map = {"60일": 60, "120일": 120, "250일": 250}
    period_label = st.selectbox("조회 기간", list(period_map.keys()), index=1)
    period_days  = period_map[period_label]

    st.divider()

    st.subheader("이동평균선")
    show_ma5  = st.checkbox("MA5  (노란색)", value=True)
    show_ma20 = st.checkbox("MA20 (초록색)", value=True)
    show_ma60 = st.checkbox("MA60 (보라색)", value=False)

    st.divider()

    st.subheader("보조지표")
    indicator = st.radio("보조지표 선택", ["없음", "RSI", "MACD"], index=0)

# ── 데이터 조회 & 렌더링 ──────────────────────────────────────────────────

ticker = st.session_state.get("ticker", ticker_input) or ticker_input
if ticker_input != st.session_state.get("ticker"):
    ticker = ticker_input

today      = datetime.today()
start_date = (today - timedelta(days=period_days + 60)).strftime("%Y%m%d")
end_date   = today.strftime("%Y%m%d")

if not APP_KEY or not APP_SECRET:
    st.error("❌ .env 파일에 KIS_APP_KEY / KIS_APP_SECRET 를 설정해 주세요.")
    st.stop()

with st.spinner(f"{ticker} 데이터 조회 중..."):
    try:
        df = fetch_ohlcv(ticker, start_date, end_date)
    except requests.HTTPError as e:
        st.error(f"API HTTP 오류: {e}")
        st.stop()
    except ValueError as e:
        st.error(f"API 오류: {e}")
        st.stop()
    except Exception as e:
        st.error(f"데이터 조회 실패: {e}")
        st.stop()

if df.empty:
    st.info("조회된 데이터가 없습니다. 종목코드와 기간을 확인해 주세요.")
    st.stop()

# 기간 필터 (MA 계산은 60일 여유분 포함한 전체 데이터로 수행)
df = calc_ma(df, [5, 20, 60])
df_display = df.tail(period_days).reset_index(drop=True)

st.caption(f"**{ticker}** | {df_display['date'].iloc[0].strftime('%Y-%m-%d')} ~ {df_display['date'].iloc[-1].strftime('%Y-%m-%d')} | {len(df_display)}거래일")

show_ma = {"MA5": show_ma5, "MA20": show_ma20, "MA60": show_ma60}
fig = build_chart(df_display, show_ma, indicator)
st.plotly_chart(fig, use_container_width=True)

st.divider()
show_summary(df_display)
