import os
import shutil
import pandas as pd

DATA_FILE = "data/stock_prices.csv"
BACKUP_FILE = "data/stock_prices_bak.csv"

# 기능 1: 파일 존재 확인
if not os.path.exists(DATA_FILE):
    print("❌ data/stock_prices.csv 파일이 없습니다")
    exit(1)

try:
    # 기능 2: 백업
    if os.path.exists(BACKUP_FILE):
        print("⚠️ 기존 백업 파일이 있습니다. 덮어씁니다")
    shutil.copy(DATA_FILE, BACKUP_FILE)
    print(f"✅ 백업 완료: {BACKUP_FILE}")

    # 기능 3: 읽기
    df = pd.read_csv(
        BACKUP_FILE,
        dtype={"srtnCd": str},
        encoding="utf-8-sig",
    )
    original_count = len(df)

    # 앞자리 0 보정
    df["srtnCd"] = df["srtnCd"].astype(str).str.zfill(6)

    # 기능 5: 중복 검증
    dup_mask = df.duplicated(subset=["srtnCd", "basDt"], keep="last")
    dup_count = dup_mask.sum()
    if dup_count > 0:
        print(f"⚠️ 중복 데이터 {dup_count}건 발견 - 마지막 값만 유지")
        df = df.drop_duplicates(subset=["srtnCd", "basDt"], keep="last")

    # 기능 4: 정렬
    df = df.sort_values(["srtnCd", "basDt"], ascending=[True, True])
    df = df.reset_index(drop=True)

    # 기능 5: 오름차순 정렬 최종 검증
    problem_stocks = []
    for code, group in df.groupby("srtnCd"):
        dates = group["basDt"].tolist()
        if dates != sorted(dates):
            problem_stocks.append(code)

    if problem_stocks:
        print(f"❌ 정렬 이상 종목: {problem_stocks}")
    else:
        print("✅ 정렬 검증 완료")

    # 기능 6: 저장
    df.to_csv(DATA_FILE, index=False, encoding="utf-8-sig")
    print(f"✅ 저장 완료: {DATA_FILE}")

    # 기능 7: 요약
    sorted_count = len(df)
    stock_count = df["srtnCd"].nunique()
    date_min = df["basDt"].min()
    date_max = df["basDt"].max()

    print("\n=== 작업 요약 ===")
    print(f"  백업 파일     : {BACKUP_FILE}")
    print(f"  원본 데이터   : {original_count:,}건")
    if dup_count > 0:
        print(f"  중복 제거     : {dup_count:,}건 제거 → {sorted_count:,}건")
    else:
        print(f"  정렬 후 데이터: {sorted_count:,}건")
    print(f"  종목 수       : {stock_count:,}개")
    print(f"  날짜 범위     : {date_min} ~ {date_max}")

except Exception as e:
    print(f"❌ 오류 발생: {e}")
    print(f"  백업 파일은 보존됩니다: {BACKUP_FILE}")
