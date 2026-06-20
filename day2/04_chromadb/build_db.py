import os
import sys
import pandas as pd
import chromadb
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("../../.env")

CSV_PATH = "../03_fss_api/data/stock_prices.csv"
CHROMA_PATH = "./chroma_db"
EMBED_MODEL = "text-embedding-3-small"

client = OpenAI()


def text_to_embedding(text: str) -> list[float]:
    response = client.embeddings.create(model=EMBED_MODEL, input=text)
    return response.data[0].embedding


def texts_to_embeddings(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]


def row_to_document(row: pd.Series) -> str:
    date = str(row["basDt"])
    year, month, day = date[:4], date[4:6], date[6:]

    close = int(row["clpr"])
    vs = int(row["vs"])
    flt_rt = float(row["fltRt"])
    mkp = int(row["mkp"])
    hipr = int(row["hipr"])
    lopr = int(row["lopr"])
    trqu = int(row["trqu"])
    mrkt_tot_amt = int(row["mrktTotAmt"]) // 100_000_000  # 원 → 억원

    vs_sign = "+" if vs >= 0 else ""
    flt_sign = "+" if flt_rt >= 0 else ""

    return (
        f"{year}년 {month}월 {day}일 {row['itmsNm']}({row['srtnCd']}, {row['mrktCtg']}) 주가: "
        f"종가 {close:,}원 (전일대비 {vs_sign}{vs:,}원, {flt_sign}{flt_rt:.2f}%), "
        f"시가 {mkp:,}원, 고가 {hipr:,}원, 저가 {lopr:,}원, "
        f"거래량 {trqu:,}주, 시가총액 {mrkt_tot_amt:,}억원"
    )


def _print_progress(current: int, total: int, width: int = 20) -> None:
    pct = current / total
    filled = int(width * pct)
    bar = "=" * filled + " " * (width - filled)
    print(f"\r[{bar}] {current:,}/{total:,} ({int(pct * 100)}%)", end="", flush=True)


def build(batch_size: int = 50, embed_batch: int = 100) -> None:
    # 1단계: CSV 파일 확인
    if not os.path.exists(CSV_PATH):
        print(f"❌ 데이터 파일 없음: {CSV_PATH}")
        print("먼저 day2/03_fss_api/collect_data.py 를 실행하세요")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH, dtype=str)
    total = len(df)
    print(f"📂 데이터 로드 완료: {total:,}건")

    # 2단계: ChromaDB 초기화
    db = chromadb.PersistentClient(path=CHROMA_PATH)
    try:
        db.delete_collection("stock_data")
    except Exception:
        pass
    collection = db.create_collection(
        name="stock_data",
        metadata={"hnsw:space": "cosine"},
    )

    # 3단계: 배치 임베딩 + 저장
    pending_docs, pending_ids, pending_meta = [], [], []
    saved = 0

    def flush(docs, ids, meta):
        # 100건씩 한 번의 API 호출로 임베딩 생성
        embeddings = texts_to_embeddings(docs)
        # ChromaDB에는 batch_size씩 나눠서 저장
        for start in range(0, len(docs), batch_size):
            collection.add(
                documents=docs[start:start + batch_size],
                embeddings=embeddings[start:start + batch_size],
                ids=ids[start:start + batch_size],
                metadatas=meta[start:start + batch_size],
            )

    for i, (_, row) in enumerate(df.iterrows()):
        pending_docs.append(row_to_document(row))
        pending_ids.append(f"{row['basDt']}_{row['srtnCd']}")
        pending_meta.append({
            "date": str(row["basDt"]),
            "ticker": str(row["srtnCd"]),
            "name": str(row["itmsNm"]),
            "market": str(row["mrktCtg"]),
        })

        if len(pending_docs) == embed_batch:
            flush(pending_docs, pending_ids, pending_meta)
            saved += len(pending_docs)
            pending_docs, pending_ids, pending_meta = [], [], []
            _print_progress(saved, total)

    # 남은 배치 처리
    if pending_docs:
        flush(pending_docs, pending_ids, pending_meta)
        saved += len(pending_docs)

    _print_progress(total, total)
    print()

    # 4단계: 완료 메시지
    print(f"✅ ChromaDB 구축 완료: {total:,}건")
    print(f"💾 저장 위치: {os.path.abspath(CHROMA_PATH)}")


if __name__ == "__main__":
    build()
