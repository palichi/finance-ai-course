from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import chromadb

DEFAULT_CHROMA_PATH = "./data/chroma_pattern_db"
DEFAULT_COLLECTION = "price_patterns"
WINDOW_SIZE = 20
FUTURE_DAYS = 5
N_FEATURES = 6  # clpr, mkp, hipr, lopr, trqu, fltRt
VECTOR_DIM = WINDOW_SIZE * N_FEATURES  # 120


@dataclass
class SearchResult:
    count: int
    mean_return_pct: float
    std_return_pct: float
    up_probability: float
    top_cases: list[dict[str, Any]] = field(default_factory=list)


class PricePatternStore:
    """가격 패턴을 ChromaDB에 저장하고 유사 패턴을 검색하는 클래스."""

    def __init__(
        self,
        chroma_path: str = DEFAULT_CHROMA_PATH,
        collection_name: str = DEFAULT_COLLECTION,
    ) -> None:
        self.chroma_path = str(Path(chroma_path).resolve())
        self.collection_name = collection_name
        self._client = chromadb.PersistentClient(path=self.chroma_path)
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    # ------------------------------------------------------------------ #
    # 내부 헬퍼                                                            #
    # ------------------------------------------------------------------ #

    @staticmethod
    def _normalize_window(window: pd.DataFrame) -> list[float]:
        """20일 윈도우 → 120차원 정규화 벡터.

        가격 4종: 첫날 종가 기준 상대 변화율 (value / base_close - 1)
        거래량   : 윈도우 평균 기준 상대 변화율 (value / avg_vol - 1)
        등락률   : 원본 값 그대로 사용
        """
        base_close = float(window["clpr"].iloc[0])
        avg_vol = float(window["trqu"].mean())

        vector: list[float] = []
        for _, row in window.iterrows():
            norm_close = float(row["clpr"]) / base_close - 1.0
            norm_open  = float(row["mkp"])  / base_close - 1.0
            norm_high  = float(row["hipr"]) / base_close - 1.0
            norm_low   = float(row["lopr"]) / base_close - 1.0
            norm_vol   = (float(row["trqu"]) / avg_vol - 1.0) if avg_vol else 0.0
            flt_rt     = float(row["fltRt"])
            vector.extend([norm_close, norm_open, norm_high, norm_low, norm_vol, flt_rt])
        return vector

    @staticmethod
    def _calc_future_return(grp: pd.DataFrame, window_end: int, future_days: int) -> float | None:
        """window_end 시점 종가 기준으로 future_days 뒤 수익률(%) 반환.

        window_end 는 슬라이싱 exclusive 인덱스 (iloc 기준).
        future_days 뒤 데이터가 없으면 None 반환.
        """
        future_idx = window_end + future_days - 1
        if future_idx >= len(grp):
            return None
        base_price  = float(grp["clpr"].iloc[window_end - 1])
        future_price = float(grp["clpr"].iloc[future_idx])
        return (future_price / base_price - 1.0) * 100.0

    # ------------------------------------------------------------------ #
    # 공개 API                                                             #
    # ------------------------------------------------------------------ #

    def build_from_dataframe(
        self,
        df: pd.DataFrame,
        window_size: int = WINDOW_SIZE,
        future_days: int = FUTURE_DAYS,
        batch_size: int = 500,
    ) -> list[str]:
        """DataFrame에서 패턴을 추출해 ChromaDB에 저장한다.

        Args:
            df         : basDt, srtnCd, itmsNm, clpr, mkp, hipr, lopr, trqu, fltRt 컬럼 필요
            window_size: 슬라이딩 윈도우 크기 (일)
            future_days: 미래 수익률 계산 기간 (일)
            batch_size : ChromaDB upsert 배치 크기

        Returns:
            저장된 패턴 ID 목록
        """
        min_days = window_size + future_days
        all_ids: list[str] = []
        all_docs: list[str] = []
        all_vectors: list[list[float]] = []
        all_metas: list[dict] = []

        for symbol, grp in df.groupby("srtnCd"):
            grp = grp.sort_values("basDt").reset_index(drop=True)
            n = len(grp)

            # 방어 코드: 데이터 부족
            if n < min_days:
                print(f"⚠️  데이터가 부족합니다 (최소 {min_days}일 필요, 현재 {n}일) [{symbol}]")
                continue

            name = str(grp["itmsNm"].iloc[0]) if "itmsNm" in grp.columns else str(symbol)

            # 마지막 future_days 행은 미래 결과 미확인 → 슬라이딩 대상 제외
            max_start = n - window_size - future_days
            for start in range(max_start + 1):
                end = start + window_size  # exclusive
                window = grp.iloc[start:end]

                future_return = self._calc_future_return(grp, end, future_days)
                if future_return is None:
                    continue

                vector = self._normalize_window(window)
                base_date  = str(int(window["basDt"].iloc[0]))
                base_price = float(window["clpr"].iloc[0])
                pat_id     = f"{symbol}_{base_date}_{start}"

                all_ids.append(pat_id)
                all_docs.append(f"{name}({symbol}) {base_date} 시작 {window_size}일 패턴")
                all_vectors.append(vector)
                all_metas.append({
                    "symbol": str(symbol),
                    "base_date": base_date,
                    "base_price": base_price,
                    "future_return_pct": round(future_return, 4),
                    "direction": "up" if future_return >= 0 else "down",
                })

        if not all_ids:
            return []

        # 500개 배치 upsert
        total = len(all_ids)
        for i in range(0, total, batch_size):
            sl = slice(i, i + batch_size)
            self._collection.upsert(
                ids=all_ids[sl],
                documents=all_docs[sl],
                embeddings=all_vectors[sl],
                metadatas=all_metas[sl],
            )
            done = min(i + batch_size, total)
            print(f"\r저장 중... {done:,}/{total:,}", end="", flush=True)

        print(f"\n✅ 총 {total:,}개 패턴 저장 완료 → {self.chroma_path}")
        return all_ids

    def search_similar_patterns(
        self,
        query_pattern: list[float],
        top_k: int = 5,
    ) -> SearchResult:
        """쿼리 패턴과 유사한 과거 패턴 top_k개를 찾아 통계 요약을 반환한다.

        Args:
            query_pattern: 정규화된 120차원 벡터
            top_k        : 반환할 유사 패턴 수

        Returns:
            SearchResult(count, mean_return_pct, std_return_pct, up_probability, top_cases)
        """
        results = self._collection.query(
            query_embeddings=[query_pattern],
            n_results=top_k,
            include=["metadatas", "documents", "distances"],
        )

        metas = results["metadatas"][0]
        docs  = results["documents"][0]
        dists = results["distances"][0]

        if not metas:
            return SearchResult(
                count=0,
                mean_return_pct=0.0,
                std_return_pct=0.0,
                up_probability=0.0,
            )

        returns  = [float(m["future_return_pct"]) for m in metas]
        mean_r   = float(np.mean(returns))
        std_r    = float(np.std(returns))
        up_prob  = sum(1 for r in returns if r >= 0) / len(returns)

        top_cases = [
            {
                "rank": rank + 1,
                "document": doc,
                "similarity": round(1 - dist, 6),
                **meta,
            }
            for rank, (meta, doc, dist) in enumerate(zip(metas, docs, dists))
        ]

        return SearchResult(
            count=len(metas),
            mean_return_pct=round(mean_r, 4),
            std_return_pct=round(std_r, 4),
            up_probability=round(up_prob, 4),
            top_cases=top_cases,
        )

    def count(self) -> int:
        """저장된 패턴 수를 반환한다."""
        return self._collection.count()


# ====================================================================== #
# 실행 예시                                                               #
# ====================================================================== #

def _make_dummy_df(symbol: str, name: str, n_days: int = 60) -> pd.DataFrame:
    """테스트용 가상 일별 시세 데이터 생성."""
    rng = np.random.default_rng(seed=42)
    base = 50_000
    prices = base * np.cumprod(1 + rng.normal(0.001, 0.015, n_days))
    highs  = prices * (1 + rng.uniform(0.005, 0.02, n_days))
    lows   = prices * (1 - rng.uniform(0.005, 0.02, n_days))
    opens  = prices * (1 + rng.normal(0.0, 0.008, n_days))
    vols   = rng.integers(500_000, 5_000_000, n_days)

    flt_rt = np.zeros(n_days)
    flt_rt[1:] = (prices[1:] / prices[:-1] - 1.0) * 100.0

    dates = pd.date_range("20240101", periods=n_days, freq="B").strftime("%Y%m%d").astype(int)

    return pd.DataFrame({
        "basDt":   dates,
        "srtnCd":  symbol,
        "itmsNm":  name,
        "clpr":    prices.astype(int),
        "mkp":     opens.astype(int),
        "hipr":    highs.astype(int),
        "lopr":    lows.astype(int),
        "trqu":    vols,
        "fltRt":   flt_rt.round(2),
    })


if __name__ == "__main__":
    import shutil

    DEMO_PATH = "./data/chroma_pattern_demo"

    # 기존 데모 DB 초기화
    shutil.rmtree(DEMO_PATH, ignore_errors=True)

    # 가상 데이터 생성 (2개 종목, 각 60일)
    df = pd.concat([
        _make_dummy_df("005930", "삼성전자", n_days=60),
        _make_dummy_df("000660", "SK하이닉스", n_days=60),
    ], ignore_index=True)

    print(f"📊 샘플 데이터: {len(df)}행 ({df['srtnCd'].nunique()}개 종목)")

    # 저장
    store = PricePatternStore(chroma_path=DEMO_PATH, collection_name="price_patterns")
    ids = store.build_from_dataframe(df, window_size=20, future_days=5, batch_size=500)

    print(f"🗂️  저장된 패턴 수: {store.count():,}개")

    # 유사 패턴 검색 (첫 번째 패턴을 쿼리로 사용)
    if ids:
        first_grp = df[df["srtnCd"] == "005930"].sort_values("basDt").reset_index(drop=True)
        query_vec = PricePatternStore._normalize_window(first_grp.iloc[:20])

        result = store.search_similar_patterns(query_vec, top_k=5)

        print("\n🔍 유사 패턴 검색 결과")
        print(f"  찾은 패턴 수     : {result.count}")
        print(f"  평균 미래 수익률 : {result.mean_return_pct:+.4f}%")
        print(f"  수익률 표준편차  : {result.std_return_pct:.4f}%")
        print(f"  상승 확률        : {result.up_probability * 100:.1f}%")
        print("\n  상위 유사 사례:")
        for case in result.top_cases:
            direction = "↑" if case["direction"] == "up" else "↓"
            print(
                f"  [{case['rank']}] {case['document']} | "
                f"유사도 {case['similarity']:.4f} | "
                f"5일 후 수익률 {case['future_return_pct']:+.2f}% {direction}"
            )
