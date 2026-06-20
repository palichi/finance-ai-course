import os
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from dotenv import load_dotenv

load_dotenv("../../.env")

st.set_page_config(page_title="백테스팅", page_icon="📈", layout="wide")
st.title("📈 주식 백테스팅 시스템")

# --- 사이드바 ---
with st.sidebar:
    st.header("설정")
    ticker_input = st.text_input("종목코드", value="005930")
    period_map = {"1년": 365, "2년": 730, "3년": 1095}
    period_label = st.selectbox("분석 기간", list(period_map.keys()))
    strategy = st.selectbox("전략 선택", ["이동평균 골든크로스", "RSI"])

    if strategy == "이동평균 골든크로스":
        short_window = st.number_input("단기 MA (일)", min_value=2, max_value=50, value=5)
        long_window = st.number_input("장기 MA (일)", min_value=10, max_value=200, value=20)
    else:
        rsi_period = st.number_input("RSI 기간 (일)", min_value=5, max_value=30, value=14)
        rsi_buy = st.number_input("매수 기준 RSI", min_value=10, max_value=40, value=30)
        rsi_sell = st.number_input("매도 기준 RSI", min_value=60, max_value=90, value=70)

    initial_capital = st.number_input(
        "초기 자본금 (원)", min_value=100_000, value=10_000_000, step=100_000
    )
    commission = st.number_input(
        "수수료율", min_value=0.0, max_value=0.01, value=0.00015, format="%.5f"
    )
    run_btn = st.button("백테스팅 실행", type="primary", use_container_width=True)


def compute_rsi(series: pd.Series, period: int) -> pd.Series:
    delta = series.diff()
    gain = delta.clip(lower=0).rolling(period).mean()
    loss = (-delta.clip(upper=0)).rolling(period).mean()
    rs = gain / loss.replace(0, np.nan)
    return 100 - 100 / (1 + rs)


def run_backtest(df: pd.DataFrame, strategy: str, params: dict, initial_capital: float, commission: float):
    close = df["Close"].squeeze()
    signals = pd.Series(0, index=close.index)

    if strategy == "이동평균 골든크로스":
        short_ma = close.rolling(params["short"]).mean()
        long_ma = close.rolling(params["long"]).mean()
        above = short_ma > long_ma
        signals[above & ~above.shift(1).fillna(False)] = 1   # 골든크로스 → 매수
        signals[~above & above.shift(1).fillna(False)] = -1  # 데드크로스 → 매도
        df = df.copy()
        df["short_ma"] = short_ma
        df["long_ma"] = long_ma
    else:
        rsi = compute_rsi(close, params["period"])
        below_buy = rsi < params["buy"]
        buy_cross = ~below_buy & below_buy.shift(1).fillna(False)
        above_sell = rsi > params["sell"]
        sell_cross = ~above_sell & above_sell.shift(1).fillna(False)
        signals[buy_cross] = 1
        signals[sell_cross] = -1
        df = df.copy()
        df["rsi"] = rsi

    capital = initial_capital
    shares = 0
    portfolio = []
    trades = []

    for date, sig in signals.items():
        price = float(close.loc[date])
        if sig == 1 and shares == 0 and capital > 0:
            cost = price * (1 + commission)
            qty = int(capital / cost)
            if qty > 0:
                shares = qty
                capital -= qty * cost
                trades.append({"날짜": date, "구분": "매수", "가격": price, "수량": qty, "손익": 0, "잔고": capital + shares * price})
        elif sig == -1 and shares > 0:
            revenue = shares * price * (1 - commission)
            buy_price = trades[-1]["가격"] if trades else price
            pnl = (price - buy_price) * shares
            capital += revenue
            trades.append({"날짜": date, "구분": "매도", "가격": price, "수량": shares, "손익": round(pnl), "잔고": round(capital)})
            shares = 0

        portfolio.append(capital + shares * price)

    portfolio_series = pd.Series(portfolio, index=close.index)
    return portfolio_series, pd.DataFrame(trades), df


def calc_mdd(series: pd.Series) -> float:
    roll_max = series.cummax()
    drawdown = (series - roll_max) / roll_max
    return float(drawdown.min() * 100)


def win_rate(trades_df: pd.DataFrame) -> float:
    sells = trades_df[trades_df["구분"] == "매도"]
    if len(sells) == 0:
        return 0.0
    return round(len(sells[sells["손익"] > 0]) / len(sells) * 100, 1)


if run_btn:
    ticker = ticker_input.strip() + ".KS"
    days = period_map[period_label]
    end = datetime.today()
    start = end - timedelta(days=days + 60)  # 지표 계산 여유분

    with st.spinner("데이터 수집 중..."):
        raw = yf.download(ticker, start=start.strftime("%Y-%m-%d"), end=end.strftime("%Y-%m-%d"), auto_adjust=True, progress=False)

    if raw.empty:
        st.error(f"종목 데이터를 가져올 수 없습니다: {ticker}")
        st.stop()

    # 실제 분석 기간만 사용
    cutoff = end - timedelta(days=days)
    df_full = raw.copy()

    params = (
        {"short": int(short_window), "long": int(long_window)}
        if strategy == "이동평균 골든크로스"
        else {"period": int(rsi_period), "buy": float(rsi_buy), "sell": float(rsi_sell)}
    )

    portfolio_series, trades_df, df_ind = run_backtest(df_full, strategy, params, initial_capital, commission)

    # 분석 기간 자르기
    portfolio_series = portfolio_series[portfolio_series.index >= cutoff]
    df_plot = df_ind[df_ind.index >= cutoff]
    if not trades_df.empty:
        trades_df = trades_df[trades_df["날짜"] >= cutoff]

    close_plot = df_plot["Close"].squeeze()

    # --- 상단 지표 카드 ---
    final_return = (portfolio_series.iloc[-1] / initial_capital - 1) * 100
    mdd = calc_mdd(portfolio_series)
    total_trades = len(trades_df)
    wr = win_rate(trades_df)

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("최종 수익률", f"{final_return:.2f}%", delta=f"{final_return:.2f}%")
    c2.metric("최대낙폭 MDD", f"{mdd:.2f}%")
    c3.metric("총 거래 횟수", f"{total_trades}회")
    c4.metric("승률", f"{wr}%")

    st.divider()

    # --- 자산 곡선 ---
    st.subheader("자산 곡선")
    fig_port = go.Figure()
    fig_port.add_trace(go.Scatter(x=portfolio_series.index, y=portfolio_series.values, name="포트폴리오", line=dict(color="#1f77b4")))
    fig_port.add_hline(y=initial_capital, line_dash="dash", line_color="gray", annotation_text="초기자본")
    fig_port.update_layout(height=350, margin=dict(t=20, b=20), yaxis_tickformat=",")
    st.plotly_chart(fig_port, use_container_width=True)

    # --- 주가 + 매매 포인트 ---
    st.subheader("주가 & 매매 포인트")
    fig_price = go.Figure()
    fig_price.add_trace(go.Scatter(x=close_plot.index, y=close_plot.values, name="종가", line=dict(color="black", width=1)))

    if strategy == "이동평균 골든크로스" and "short_ma" in df_plot.columns:
        fig_price.add_trace(go.Scatter(x=df_plot.index, y=df_plot["short_ma"].squeeze(), name=f"단기MA({int(short_window)}일)", line=dict(color="orange", dash="dot")))
        fig_price.add_trace(go.Scatter(x=df_plot.index, y=df_plot["long_ma"].squeeze(), name=f"장기MA({int(long_window)}일)", line=dict(color="purple", dash="dot")))

    if not trades_df.empty:
        buys = trades_df[trades_df["구분"] == "매수"]
        sells = trades_df[trades_df["구분"] == "매도"]
        fig_price.add_trace(go.Scatter(
            x=buys["날짜"], y=buys["가격"],
            mode="markers", name="매수",
            marker=dict(symbol="triangle-up", size=12, color="red"),
        ))
        fig_price.add_trace(go.Scatter(
            x=sells["날짜"], y=sells["가격"],
            mode="markers", name="매도",
            marker=dict(symbol="triangle-down", size=12, color="blue"),
        ))

    fig_price.update_layout(height=400, margin=dict(t=20, b=20), yaxis_tickformat=",")
    st.plotly_chart(fig_price, use_container_width=True)

    # --- 거래 내역 테이블 ---
    st.subheader("거래 내역")
    if trades_df.empty:
        st.info("해당 기간에 발생한 거래가 없습니다.")
    else:
        display_df = trades_df.copy()
        display_df["날짜"] = pd.to_datetime(display_df["날짜"]).dt.strftime("%Y-%m-%d")
        display_df["가격"] = display_df["가격"].apply(lambda x: f"{int(x):,}원")
        display_df["손익"] = display_df["손익"].apply(lambda x: f"{x:,}원")
        display_df["잔고"] = display_df["잔고"].apply(lambda x: f"{int(x):,}원")
        st.dataframe(display_df, use_container_width=True, hide_index=True)
else:
    st.info("왼쪽 사이드바에서 설정 후 **백테스팅 실행** 버튼을 눌러주세요.")
