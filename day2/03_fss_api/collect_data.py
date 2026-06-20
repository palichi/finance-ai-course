"""
KOSPI200 종목 주가 데이터 수집 스크립트
data/kospi200_list.csv → data/stock_prices.csv
"""

import os
import sys
import time
import requests
import pandas as pd
from datetime import datetime, timedelta
from dotenv import load_dotenv

# 기능 10: ../../.env 에서 API Key 로드
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

API_KEY   = os.getenv("FSS_API_KEY", "")
BASE_URL  = "https://apis.data.go.kr/1160100/service/GetStockSecuritiesInfoService"
DATA_DIR  = os.path.join(os.path.dirname(__file__), "data")
LIST_CSV  = os.path.join(DATA_DIR, "kospi200_list.csv")

OUTPUT_CSV = os.path.join(DATA_DIR, "stock_prices.csv")
START_DATE = "20240101"   # 기능 2: 최초 수집 시작일 고정


def get_stock_price(ticker: str, start_date: str, end_date: str) -> pd.DataFrame:
    """종목의 주가 데이터를 페이지 단위로 전체 수집"""
    all_items = []
    page = 1

    while True:
        params = {
            "serviceKey": API_KEY,
            "numOfRows":  "100",
            "pageNo":     str(page),
            "resultType": "json",
            "beginBasDt": start_date,
            "endBasDt":   end_date,
            "likeSrtnCd": ticker,
        }
        resp = requests.get(
            f"{BASE_URL}/getStockPriceInfo",
            params=params,
            timeout=15,
        )
        resp.raise_for_status()

        body  = resp.json().get("response", {}).get("body", {})
        total = int(body.get("totalCount", 0))
        items = body.get("items", {})

        if not items or total == 0:
            break

        item_list = items.get("item", [])
        if isinstance(item_list, dict):   # 1건일 때 dict로 옴
            item_list = [item_list]

        all_items.extend(item_list)

        if len(all_items) >= total:
            break

        page += 1
        time.sleep(0.2)   # 페이지 간 부하 방지

    if not all_items:
        return pd.DataFrame()

    df = pd.DataFrame(all_items)

    # 기능 3: srtnCd 앞자리 0 보존
    df["srtnCd"] = df["srtnCd"].astype(str).str.zfill(6)

    num_cols = ["clpr", "vs", "mkp", "hipr", "lopr", "trqu", "trPrc", "lstgStCnt", "mrktTotAmt"]
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "basDt" in df.columns:
        df = df.sort_values("basDt").reset_index(drop=True)

    return df


def main():
    # 기능 9: API Key 확인
    if not API_KEY:
        print(".env 파일에 FSS_API_KEY 를 입력하세요")
        sys.exit(1)

    # 기능 1: 종목 리스트 파일 확인
    if not os.path.exists(LIST_CSV):
        print("data/kospi200_list.csv 파일이 없습니다. 종목 리스트를 먼저 준비하세요")
        sys.exit(1)

    # 기능 4: data 폴더 없으면 자동 생성
    os.makedirs(DATA_DIR, exist_ok=True)

    # 기능 1: 종목 리스트 읽기 (srtnCd, itmsNm)
    stocks = pd.read_csv(LIST_CSV, encoding="utf-8-sig", dtype=str)
    stocks["srtnCd"] = stocks["srtnCd"].astype(str).str.zfill(6)
    total_stocks = len(stocks)

    # 기존 데이터 로드 (기능 2: 증분 수집용)
    if os.path.exists(OUTPUT_CSV):
        existing = pd.read_csv(OUTPUT_CSV, encoding="utf-8-sig", dtype={"srtnCd": str})
        existing["srtnCd"] = existing["srtnCd"].astype(str).str.zfill(6)
    else:
        existing = pd.DataFrame()

    today      = datetime.now().strftime("%Y%m%d")
    all_frames = [existing] if not existing.empty else []
    failed     = []

    for i, row in enumerate(stocks.itertuples(index=False), start=1):
        code = row.srtnCd
        name = row.itmsNm

        # 기능 7: 진행 상황 출력
        print(f"[{i}/{total_stocks}] {name}({code}) 수집 중...")

        # 기능 2: 시작일 결정 (신규 vs 증분)
        if not existing.empty and code in existing["srtnCd"].values:
            last_dt = existing[existing["srtnCd"] == code]["basDt"].max()
            start   = (datetime.strptime(str(last_dt), "%Y%m%d") + timedelta(days=1)).strftime("%Y%m%d")
        else:
            start = START_DATE

        if start > today:
            print(f"✅ {name}: 이미 최신 데이터")
            continue

        try:
            df = get_stock_price(code, start, today)
            if df.empty:
                print(f"⚠️ {name}: 수집 실패 (데이터 없음) - 다음 종목으로 진행")
                failed.append(code)
            else:
                all_frames.append(df)
                print(f"✅ {name}: {len(df)}건 수집")
        except Exception as e:
            print(f"⚠️ {name}: 수집 실패 ({e}) - 다음 종목으로 진행")
            failed.append(code)

        # 기능 8: 서버 과부하 방지
        time.sleep(0.5)

    if not all_frames:
        print("수집된 데이터가 없습니다.")
        return

    # 기능 6: 전체 합치기 + 종목코드·날짜 기준 중복 제거
    result = pd.concat(all_frames, ignore_index=True)
    result["srtnCd"] = result["srtnCd"].astype(str).str.zfill(6)
    result = result.drop_duplicates(subset=["srtnCd", "basDt"])
    if "basDt" in result.columns:
        result = result.sort_values(["srtnCd", "basDt"]).reset_index(drop=True)

    # 기능 4: utf-8-sig 인코딩으로 저장
    result.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")

    # 기능 7: 완료 메시지
    print(f"\n✅ 전체 완료: 총 {len(result):,}건 → {OUTPUT_CSV} 저장")

    # 기능 5: 실패 종목 요약
    if failed:
        print(f"⚠️ 수집 실패 종목 ({len(failed)}개): {', '.join(failed)}")


if __name__ == "__main__":
    main()
