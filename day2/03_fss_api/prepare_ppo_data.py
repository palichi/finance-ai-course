# prepare_ppo_data.py
# 원본 CSV(data/stock_prices.csv) 컬럼 (한국거래소 일별매매정보 API 표준, 총 15개)
#
# [사용하는 컬럼 - PPO 학습 환경 입력]
#   mkp   시가      → open
#   hipr  고가      → high
#   lopr  저가      → low
#   clpr  종가      → close
#   trqu  거래량    → volume
#
# [사용하지 않는 컬럼 - 원본에는 존재하지만 이번 전처리에서 제외]
#   basDt      기준일자  (날짜 보존용으로 출력 파일에는 포함)
#   srtnCd     단축코드 (종목코드, 6자리)
#   isinCd     ISIN코드
#   itmsNm     종목명
#   mrktCtg    시장구분 (코스피/코스닥)
#   vs         전일대비
#   fltRt      등락률
#   trPrc      거래금액
#   lstgStCnt  상장주식수
#   mrktTotAmt 시장총액(시가총액)
#
# 출력 파일: data/ppo_ready/{종목코드}.csv
# 출력 컬럼: [basDt, open, high, low, close, volume]
#
# ppo_trading_model.py 에서 아래처럼 바로 읽어서 사용 가능:
#   df = pd.read_csv("data/ppo_ready/005930.csv")
#   env = StockTradingEnv(df)

import os
import sys
import pandas as pd

REQUIRED_COLUMNS = [
    "basDt", "srtnCd", "isinCd", "itmsNm", "mrktCtg",
    "clpr", "vs", "fltRt", "mkp", "hipr", "lopr",
    "trqu", "trPrc", "lstgStCnt", "mrktTotAmt",
]
PPO_COLUMNS = ["basDt", "open", "high", "low", "close", "volume"]


# 기능 1
def load_raw_data(csv_path="data/stock_prices.csv") -> pd.DataFrame:
    if not os.path.exists(csv_path):
        print(f"❌ {csv_path} 파일이 없습니다")
        sys.exit(1)

    df = pd.read_csv(csv_path, dtype={"srtnCd": str}, encoding="utf-8-sig")

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        print(f"❌ 다음 컬럼이 없습니다: {missing}")
        sys.exit(1)

    df["srtnCd"] = df["srtnCd"].astype(str).str.zfill(6)
    return df


# 기능 2
def list_available_symbols(df: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df.groupby(["srtnCd", "itmsNm"], sort=True)
        .size()
        .reset_index(name="데이터건수")
        .rename(columns={"srtnCd": "종목코드", "itmsNm": "종목명"})
    )
    return summary


# 기능 3
def extract_symbol_data(df: pd.DataFrame, symbol_code: str) -> pd.DataFrame:
    filtered = df[df["srtnCd"] == symbol_code].copy()
    filtered = filtered.drop_duplicates(subset=["srtnCd", "basDt"], keep="last")
    filtered = filtered.sort_values("basDt", ascending=True)
    filtered = filtered.reset_index(drop=True)
    return filtered


# 기능 4
def select_and_rename_for_ppo(df: pd.DataFrame) -> pd.DataFrame:
    renamed = df[["basDt", "mkp", "hipr", "lopr", "clpr", "trqu"]].copy()
    renamed = renamed.rename(columns={
        "mkp": "open",
        "hipr": "high",
        "lopr": "low",
        "clpr": "close",
        "trqu": "volume",
    })
    return renamed[PPO_COLUMNS]


# 기능 5
def validate_data(df: pd.DataFrame, symbol_code: str, window_size: int = 20):
    price_cols = ["open", "high", "low", "close"]
    bad_rows = set()

    # 결측치 확인
    nan_counts = df[PPO_COLUMNS].isnull().sum()
    if nan_counts.any():
        print(f"  ⚠️ {symbol_code}: 결측치 발견 → {nan_counts[nan_counts > 0].to_dict()}")
        bad_rows |= set(df[df[PPO_COLUMNS].isnull().any(axis=1)].index)

    # 0 이하 가격 확인
    invalid_price = df[(df[price_cols] <= 0).any(axis=1)]
    if len(invalid_price) > 0:
        print(f"  ⚠️ {symbol_code}: 0 이하 가격 {len(invalid_price)}행 발견")
        bad_rows |= set(invalid_price.index)

    # 이상 행 제거
    if bad_rows:
        removed = len(bad_rows)
        df = df.drop(index=list(bad_rows)).reset_index(drop=True)
        print(f"  ⚠️ {symbol_code}: {removed}행 제거됨")

    # 최소 일수 확인
    n = len(df)
    if n < window_size:
        print(f"  ⚠️ {symbol_code}: 데이터가 {n}일 밖에 없습니다 (최소 {window_size}일 필요)")
        return None

    print(f"  ✅ {symbol_code}: 데이터 검증 통과 ({n}일)")
    return df


# 기능 6
def prepare_one_symbol(
    df: pd.DataFrame,
    symbol_code: str,
    output_dir: str = "data/ppo_ready",
):
    symbol_df = extract_symbol_data(df, symbol_code)
    ppo_df = select_and_rename_for_ppo(symbol_df)
    validated = validate_data(ppo_df, symbol_code)

    if validated is None:
        return None

    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, f"{symbol_code}.csv")
    validated.to_csv(out_path, index=False, encoding="utf-8-sig")
    return out_path


# 기능 7
def prepare_all_symbols(
    csv_path: str = "data/stock_prices.csv",
    output_dir: str = "data/ppo_ready",
):
    df = load_raw_data(csv_path)
    symbols_df = list_available_symbols(df)
    total = len(symbols_df)

    success = []
    fail = []

    for i, row in enumerate(symbols_df.itertuples(), start=1):
        code = row.종목코드
        name = row.종목명
        print(f"[{i}/{total}] {code} {name} 처리 중...")

        try:
            out_path = prepare_one_symbol(df, code, output_dir)
            if out_path:
                print(f"  → {out_path} 저장")
                success.append(code)
            else:
                fail.append((code, "검증 실패"))
        except Exception as e:
            print(f"  ❌ {code}: 오류 발생 → {e}")
            fail.append((code, str(e)))

    print(f"\n✅ 전체 완료: 성공 {len(success)}개 / 실패 {len(fail)}개")
    if fail:
        fail_str = ", ".join(f"{c}({r})" for c, r in fail)
        print(f"⚠️ 실패 종목: {fail_str}")


# 기능 8
if __name__ == "__main__":
    prepare_all_symbols()
