import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd
import chromadb
from openai import OpenAI

load_dotenv(Path(__file__).parent / "../../.env")

CSV_PATH = Path(__file__).parent / "../03_fss_api/data/stock_prices.csv"
CHROMA_PATH = Path(__file__).parent / "chroma_db_text"
COLLECTION_NAME = "stock_text_documents"
EMBED_MODEL = "text-embedding-3-small"

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def text_to_embedding(text: str) -> list[float]:
    response = client.embeddings.create(model=EMBED_MODEL, input=text)
    return response.data[0].embedding


def texts_to_embeddings(texts: list[str]) -> list[list[float]]:
    """OpenAI API 배치 호출 (최대 2048건 한 번에 처리)."""
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)
    return [item.embedding for item in sorted(response.data, key=lambda x: x.index)]


def row_to_document(row: pd.Series) -> str:
    raw_date = str(int(row["basDt"]))
    date_str = f"{raw_date[:4]}년 {int(raw_date[4:6])}월 {int(raw_date[6:])}일"

    vs = int(row["vs"])
    vs_str = f"+{vs:,}" if vs >= 0 else f"{vs:,}"

    flt = float(row["fltRt"])
    flt_str = f"+{flt:.2f}" if flt >= 0 else f"{flt:.2f}"

    market_cap_uk = int(row["mrktTotAmt"]) // 100_000_000

    return (
        f"{date_str} {row['itmsNm']}({row['srtnCd']}, {row['mrktCtg']}) 주가: "
        f"종가 {int(row['clpr']):,}원 (전일대비 {vs_str}원, {flt_str}%), "
        f"시가 {int(row['mkp']):,}원, 고가 {int(row['hipr']):,}원, 저가 {int(row['lopr']):,}원, "
        f"거래량 {int(row['trqu']):,}주, 시가총액 {market_cap_uk:,}억원"
    )


def _progress_bar(current: int, total: int, width: int = 20) -> str:
    pct = current / total
    filled = int(width * pct)
    bar = "=" * filled + " " * (width - filled)
    return f"[{bar}] {current:,}/{total:,} ({int(pct * 100)}%)"


def build(embed_batch_size: int = 2048, chroma_batch_size: int = 500) -> None:
    # 1단계: CSV 파일 존재 확인
    if not CSV_PATH.exists():
        print(f"❌ 데이터 파일 없음: {CSV_PATH}")
        print("먼저 day2/03_fss_api/collect_data.py 를 실행하세요")
        sys.exit(1)

    df = pd.read_csv(CSV_PATH)
    total = len(df)
    print(f"📂 CSV 로드 완료: {total:,}건")

    # 2단계: ChromaDB 초기화
    chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))

    existing = [c.name for c in chroma_client.list_collections()]
    if COLLECTION_NAME in existing:
        chroma_client.delete_collection(COLLECTION_NAME)
        print(f"🗑️  기존 컬렉션 삭제: {COLLECTION_NAME}")

    collection = chroma_client.create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )
    print(f"✨ 컬렉션 생성: {COLLECTION_NAME}")

    # 3단계: 배치 임베딩 + 저장
    # 먼저 전체 문서·메타를 준비한 뒤 embed_batch_size 단위로 API 호출
    all_docs  = [row_to_document(row) for _, row in df.iterrows()]
    all_ids   = [f"stock_{i}" for i in range(total)]
    all_metas = [
        {
            "date":   str(int(row["basDt"])),
            "ticker": str(row["srtnCd"]),
            "name":   str(row["itmsNm"]),
            "market": str(row["mrktCtg"]),
        }
        for _, row in df.iterrows()
    ]

    processed = 0
    for start in range(0, total, embed_batch_size):
        sl = slice(start, start + embed_batch_size)

        # OpenAI API 배치 호출 (최대 2048건)
        batch_embeds = texts_to_embeddings(all_docs[sl])

        # ChromaDB chroma_batch_size 단위 저장
        docs_sl  = all_docs[sl]
        ids_sl   = all_ids[sl]
        metas_sl = all_metas[sl]
        for c_start in range(0, len(docs_sl), chroma_batch_size):
            csl = slice(c_start, c_start + chroma_batch_size)
            collection.add(
                documents=docs_sl[csl],
                embeddings=batch_embeds[csl],
                ids=ids_sl[csl],
                metadatas=metas_sl[csl],
            )

        processed += len(batch_embeds)
        print(f"\r{_progress_bar(processed, total)}", end="", flush=True)

    print()

    # 4단계: 완료 메시지
    print(f"✅ ChromaDB 구축 완료: {total:,}건")
    print(f"💾 저장 위치: {CHROMA_PATH.resolve()}")


if __name__ == "__main__":
    build()
