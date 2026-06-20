"""
금융위원회 공공데이터 주식시세 API 클라이언트
실행: python fss_client.py
"""

import requests
import pandas as pd
import os
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv("../../.env")

API_KEY  = os.getenv("FSS_API_KEY", "")
BASE_URL = "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService"


def get_stock_price(
    ticker: str,
    start_date: str,
    end_date: str,
    num_rows: int = 100,
) -> pd.DataFrame:
    """
    주식 시세 조회
    
    Args:
        ticker:     종목코드 (예: "005930")
        start_date: 시작일 YYYYMMDD
        end_date:   종료일 YYYYMMDD
        num_rows:   한 번에 가져올 건수 (최대 100)
    
    Returns:
        pandas DataFrame
    """
    params = {
        "serviceKey": API_KEY,
        "numOfRows":  str(num_rows),
        "pageNo":     "1",
        "resultType": "json",
        "beginBasDt": start_date,
        "endBasDt":   end_date,
        "likeSrtnCd": ticker,         # 단축코드로 검색
    }

    resp = requests.get(
        f"{BASE_URL}/getStockPriceInfo",
        params=params,
        timeout=15,
    )
    resp.raise_for_status()

    data = resp.json()
    body = data.get("response", {}).get("body", {})

    total = int(body.get("totalCount", 0))
    items = body.get("items", {})

    if not items or total == 0:
        return pd.DataFrame()

    item_list = items.get("item", [])
    if isinstance(item_list, dict):       # 1건일 때 dict로 옴
        item_list = [item_list]

    df = pd.DataFrame(item_list)

    # 숫자 컬럼 변환
    num_cols = ["clpr","vs","mkp","hipr","lopr","trqu","trPrc",
                "lstgStCnt","mrktTotAmt"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 날짜 정렬
    if "basDt" in df.columns:
        df = df.sort_values("basDt").reset_index(drop=True)

    return df


def df_to_rag_text(row: pd.Series) -> str:
    """DataFrame 행을 RAG 학습용 자연어 문장으로 변환"""
    date    = row.get("basDt", "")
    code    = row.get("srtnCd", "")
    name    = row.get("itmsNm", "")
    market  = row.get("mrktCtg", "")
    close   = int(row.get("clpr", 0))
    vs      = int(row.get("vs", 0))
    flt_rt  = float(row.get("fltRt", 0))
    open_p  = int(row.get("mkp", 0))
    high    = int(row.get("hipr", 0))
    low     = int(row.get("lopr", 0))
    volume  = int(row.get("trqu", 0))
    mkt_cap = int(row.get("mrktTotAmt", 0))

    return (
        f"{date[:4]}년 {date[4:6]}월 {date[6:]}일 "
        f"{name}({code}, {market}) 주가 정보: "
        f"종가 {close:,}원, 전일대비 {vs:+,}원({flt_rt:+.2f}%), "
        f"시가 {open_p:,}원, 고가 {high:,}원, 저가 {low:,}원, "
        f"거래량 {volume:,}주, 시가총액 {mkt_cap//100000000:,}억원"
    )


# ── 테스트 실행 ───────────────────────────────────
if __name__ == "__main__":
    if not API_KEY:
        print("❌ .env 파일에 FSS_API_KEY를 입력하세요")
        print("   발급: https://www.data.go.kr → '주식시세' 검색")
        exit(1)

    end   = datetime.now().strftime("%Y%m%d")
    start = (datetime.now() - timedelta(days=30)).strftime("%Y%m%d")

    print(f"📥 삼성전자 최근 30일 데이터 수집 중... ({start} ~ {end})")
    df = get_stock_price("005930", start, end)

    if df.empty:
        print("❌ 데이터 없음 — API Key 또는 날짜 확인")
    else:
        print(f"✅ {len(df)}건 수집 완료\n")
        print(df[["basDt","itmsNm","clpr","vs","fltRt","trqu"]].to_string(index=False))

        # RAG용 텍스트 변환 예시
        print("\n📝 RAG 학습용 텍스트 변환 예시 (첫 3건):")
        for _, row in df.head(3).iterrows():
            print(f"  → {df_to_rag_text(row)}")
