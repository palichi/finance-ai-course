"""
data/data.csv → data/kospi200.csv, data/kospi200_list.csv 변환 스크립트
kospi200.csv     : 종목코드, 종목명 (한글 컬럼)
kospi200_list.csv: srtnCd,  itmsNm  (FSS API 컬럼 — collect_data.py 용)
"""

import os
import pandas as pd

DATA_DIR   = os.path.join(os.path.dirname(__file__), "data")
INPUT_CSV  = os.path.join(DATA_DIR, "data.csv")
OUTPUT_CSV = os.path.join(DATA_DIR, "kospi200.csv")
LIST_CSV   = os.path.join(DATA_DIR, "kospi200_list.csv")


def main():
    # 기능 3: data 폴더 없으면 자동 생성
    os.makedirs(DATA_DIR, exist_ok=True)

    # 기능 1: data.csv 읽기 (BOM 포함 utf-8-sig)
    df = pd.read_csv(INPUT_CSV, encoding="utf-8-sig", dtype=str)

    # 기능 2: 종목코드 앞자리 0 보존
    df["종목코드"] = df["종목코드"].astype(str).str.zfill(6)

    # 종목코드, 종목명만 추출
    result = df[["종목코드", "종목명"]].copy()

    # 기능 3: kospi200.csv 저장 (한글 컬럼)
    result.to_csv(OUTPUT_CSV, index=False, encoding="utf-8-sig")
    print(f"✅ {len(result)}개 종목 저장 완료 → {OUTPUT_CSV}")

    # kospi200_list.csv 저장 (FSS API 컬럼명: srtnCd, itmsNm)
    list_df = result.rename(columns={"종목코드": "srtnCd", "종목명": "itmsNm"})
    list_df.to_csv(LIST_CSV, index=False, encoding="utf-8-sig")
    print(f"✅ {len(list_df)}개 종목 저장 완료 → {LIST_CSV}")

    print(list_df.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
