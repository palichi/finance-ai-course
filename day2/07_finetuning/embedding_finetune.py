import os
import time
import torch
import chromadb
from datasets import Dataset
from sentence_transformers import SentenceTransformer, util
from sentence_transformers.sentence_transformer.losses import MultipleNegativesRankingLoss
from sentence_transformers.sentence_transformer.trainer import SentenceTransformerTrainer
from sentence_transformers.sentence_transformer.training_args import SentenceTransformerTrainingArguments

CHROMA_PATH = "../04_chromadb/chroma_db"
BASE_MODEL = "BAAI/bge-m3"
OUTPUT_PATH = "./finetuned_embedding/"


# ── 기능 0: 디바이스 확인 ──────────────────────────────────────────────────────

def get_device() -> str:
    if torch.cuda.is_available():
        device = "cuda"
        print(f"GPU 사용: {torch.cuda.get_device_name(0)}")
    else:
        device = "cpu"
        print("⚠️  GPU를 찾을 수 없습니다. CPU로 학습합니다 — 소요 시간이 매우 길 수 있습니다 (30분+).")
    return device


# ── 기능 1: 베이스 모델 로딩 ──────────────────────────────────────────────────

def load_model(device: str, label: str = "모델") -> SentenceTransformer:
    print(f"\n[기능 1] {label} 로딩: {BASE_MODEL} (device={device})")
    model = SentenceTransformer(BASE_MODEL, device="cpu")  # CPU에 먼저 로드
    print("  로딩 완료")
    return model


# ── 기능 2: 학습 데이터 구성 ──────────────────────────────────────────────────

def build_training_dataset() -> tuple[Dataset, list[str]]:
    """
    (anchor=질문, positive=정답문서) 쌍을 구성하고
    HuggingFace Dataset으로 반환한다. corpus도 함께 반환.
    """
    print("\n[기능 2] 학습 데이터 구성")

    # chromadb에서 실제 문서 가져오기
    chroma_docs: list[str] = []
    try:
        db = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = db.get_collection("stock_data")
        result = collection.get(limit=200, include=["documents"])
        chroma_docs = result["documents"] or []
        print(f"  ChromaDB 문서 {len(chroma_docs)}개 로드")
    except Exception as e:
        print(f"  ⚠️  ChromaDB 로드 실패 ({e}) — 내장 예시 데이터만 사용")

    # 도메인 특화 (질문, 정답 문서) 쌍 20개
    hardcoded: list[tuple[str, str]] = [
        (
            "삼성전자 12월 주가는?",
            "2024년 12월 31일 삼성전자(005930, KOSPI) 주가: 종가 53,400원 (전일대비 -200원, -0.37%), "
            "시가 53,600원, 고가 54,000원, 저가 53,200원, 거래량 12,345,678주, 시가총액 3,187,440억원",
        ),
        (
            "SK하이닉스 최근 종가",
            "2024년 12월 31일 SK하이닉스(000660, KOSPI) 주가: 종가 171,000원 (전일대비 +1,500원, +0.88%), "
            "시가 169,500원, 고가 172,000원, 저가 169,000원, 거래량 3,210,456주, 시가총액 1,244,880억원",
        ),
        (
            "삼성전자 거래량 가장 많았던 날",
            "2024년 11월 15일 삼성전자(005930, KOSPI) 주가: 종가 56,800원 (전일대비 -3,200원, -5.34%), "
            "시가 60,000원, 고가 60,100원, 저가 56,500원, 거래량 58,932,100주, 시가총액 3,390,120억원",
        ),
        (
            "카카오 주가 하락한 날 언제?",
            "2024년 10월 08일 카카오(035720, KOSPI) 주가: 종가 32,150원 (전일대비 -4,350원, -11.93%), "
            "시가 36,500원, 고가 36,500원, 저가 31,900원, 거래량 24,567,890주, 시가총액 142,547억원",
        ),
        (
            "NAVER 시가총액 얼마야?",
            "2024년 12월 31일 NAVER(035420, KOSPI) 주가: 종가 176,500원 (전일대비 +500원, +0.28%), "
            "시가 176,000원, 고가 177,500원, 저가 175,500원, 거래량 890,234주, 시가총액 289,060억원",
        ),
        (
            "현대차 고가 기록",
            "2024년 06월 10일 현대차(005380, KOSPI) 주가: 종가 248,000원 (전일대비 +8,000원, +3.33%), "
            "시가 240,000원, 고가 252,500원, 저가 239,500원, 거래량 1,234,567주, 시가총액 529,336억원",
        ),
        (
            "LG에너지솔루션 저가는 얼마?",
            "2024년 01월 17일 LG에너지솔루션(373220, KOSPI) 주가: 종가 378,000원 (전일대비 -22,000원, -5.50%), "
            "시가 400,000원, 고가 400,500원, 저가 375,000원, 거래량 987,654주, 시가총액 886,680억원",
        ),
        (
            "코스피 시장 대형주 오늘 시가",
            "2024년 12월 30일 삼성전자(005930, KOSPI) 주가: 종가 53,600원 (전일대비 +400원, +0.75%), "
            "시가 53,200원, 고가 54,100원, 저가 53,000원, 거래량 9,876,543주, 시가총액 3,199,800억원",
        ),
        (
            "셀트리온 바이오주 주가",
            "2024년 12월 31일 셀트리온(068270, KOSPI) 주가: 종가 155,700원 (전일대비 +700원, +0.45%), "
            "시가 155,000원, 고가 156,500원, 저가 154,500원, 거래량 456,789주, 시가총액 220,016억원",
        ),
        (
            "삼성바이오로직스 전일대비 등락",
            "2024년 12월 31일 삼성바이오로직스(207940, KOSPI) 주가: 종가 985,000원 (전일대비 -15,000원, -1.50%), "
            "시가 1,000,000원, 고가 1,002,000원, 저가 982,000원, 거래량 234,567주, 시가총액 700,462억원",
        ),
        (
            "포스코홀딩스 철강주 가격",
            "2024년 12월 31일 POSCO홀딩스(005490, KOSPI) 주가: 종가 298,000원 (전일대비 +2,000원, +0.68%), "
            "시가 296,000원, 고가 300,500원, 저가 295,500원, 거래량 678,901주, 시가총액 260,254억원",
        ),
        (
            "기아 자동차 주식 거래량",
            "2024년 12월 31일 기아(000270, KOSPI) 주가: 종가 89,700원 (전일대비 +300원, +0.34%), "
            "시가 89,400원, 고가 90,100원, 저가 89,000원, 거래량 2,345,678주, 시가총액 363,556억원",
        ),
        (
            "삼성전자 연초 주가",
            "2024년 01월 02일 삼성전자(005930, KOSPI) 주가: 종가 74,300원 (전일대비 +500원, +0.68%), "
            "시가 74,000원, 고가 75,000원, 저가 73,800원, 거래량 10,234,567주, 시가총액 4,432,690억원",
        ),
        (
            "카카오뱅크 인터넷은행 주가",
            "2024년 12월 31일 카카오뱅크(323410, KOSPI) 주가: 종가 22,300원 (전일대비 -100원, -0.45%), "
            "시가 22,400원, 고가 22,700원, 저가 22,200원, 거래량 1,567,890주, 시가총액 105,821억원",
        ),
        (
            "코스닥 성장주 에코프로 주가",
            "2024년 12월 31일 에코프로(086520, KOSDAQ) 주가: 종가 89,200원 (전일대비 +1,200원, +1.36%), "
            "시가 88,000원, 고가 90,500원, 저가 87,500원, 거래량 3,456,789주, 시가총액 65,820억원",
        ),
        (
            "반도체 업종 주가 상승일",
            "2024년 08월 05일 SK하이닉스(000660, KOSPI) 주가: 종가 155,800원 (전일대비 +12,300원, +8.57%), "
            "시가 143,500원, 고가 157,000원, 저가 143,000원, 거래량 8,901,234주, 시가총액 1,132,752억원",
        ),
        (
            "삼성전자 2분기 주가 흐름",
            "2024년 06월 28일 삼성전자(005930, KOSPI) 주가: 종가 78,800원 (전일대비 +600원, +0.77%), "
            "시가 78,200원, 고가 79,200원, 저가 78,000원, 거래량 11,234,567주, 시가총액 4,703,360억원",
        ),
        (
            "LG화학 배터리 소재 주가",
            "2024년 12월 31일 LG화학(051910, KOSPI) 주가: 종가 285,500원 (전일대비 -2,500원, -0.87%), "
            "시가 288,000원, 고가 289,000원, 저가 284,500원, 거래량 345,678주, 시가총액 201,413억원",
        ),
        (
            "현대중공업 조선주 주가 동향",
            "2024년 12월 31일 HD현대중공업(329180, KOSPI) 주가: 종가 198,700원 (전일대비 +3,200원, +1.64%), "
            "시가 195,500원, 고가 200,000원, 저가 195,000원, 거래량 567,890주, 시가총액 163,940억원",
        ),
        (
            "코스피 12월 시가총액 1위",
            "2024년 12월 31일 삼성전자(005930, KOSPI) 주가: 종가 53,400원 (전일대비 -200원, -0.37%), "
            "시가 53,600원, 고가 54,000원, 저가 53,200원, 거래량 12,345,678주, 시가총액 3,187,440억원",
        ),
    ]

    # chromadb 실문서로 쌍 보강 (최대 10개)
    chroma_pairs: list[tuple[str, str]] = []
    for doc in chroma_docs[:10]:
        if "삼성전자" in doc:
            chroma_pairs.append(("삼성전자 주가 정보", doc))
        elif "SK하이닉스" in doc:
            chroma_pairs.append(("SK하이닉스 주가 현황", doc))
        elif "NAVER" in doc or "네이버" in doc:
            chroma_pairs.append(("네이버 주가 현황", doc))
        elif "거래량" in doc:
            chroma_pairs.append(("거래량 데이터 조회", doc))
        else:
            chroma_pairs.append(("주식 가격 정보", doc))

    all_pairs = hardcoded + chroma_pairs
    anchors = [q for q, _ in all_pairs]
    positives = [d for _, d in all_pairs]

    print(f"  학습 쌍 총 {len(all_pairs)}개 (내장 {len(hardcoded)}개 + ChromaDB {len(chroma_pairs)}개)")

    dataset = Dataset.from_dict({"anchor": anchors, "positive": positives})

    # corpus: 비교용 (chromadb 문서 + 정답 문서)
    corpus = list(dict.fromkeys(chroma_docs[:100] + positives))
    return dataset, corpus


# ── 기능 3: Contrastive Learning 학습 ────────────────────────────────────────

def finetune(
    model: SentenceTransformer,
    dataset: Dataset,
    output_path: str,
    epochs: int = 3,
    batch_size: int = 4,
) -> None:
    print(f"\n[기능 3] Fine-tuning 시작 (epochs={epochs}, batch_size={batch_size}, device=CPU)")
    print("  ⚠️  CPU 학습 중 — bge-m3 기준 약 10~30분 소요됩니다")
    t0 = time.time()

    loss_fn = MultipleNegativesRankingLoss(model)

    args = SentenceTransformerTrainingArguments(
        output_dir=output_path,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        warmup_steps=0.1,
        fp16=False,        # CPU는 fp16 미지원
        bf16=False,
        use_cpu=True,      # GPU 완전 비활성화
        logging_steps=2,
        save_strategy="no",
    )

    trainer = SentenceTransformerTrainer(
        model=model,
        args=args,
        train_dataset=dataset,
        loss=loss_fn,
    )
    trainer.train()

    elapsed = time.time() - t0
    print(f"  Fine-tuning 완료 ({elapsed:.1f}초 / {elapsed/60:.1f}분)")


# ── 기능 4: 학습 전후 비교 ────────────────────────────────────────────────────

def compare_models(
    base_model: SentenceTransformer,
    ft_model: SentenceTransformer,
    corpus: list[str],
) -> None:
    print("\n[기능 4] 학습 전후 검색 성능 비교")

    eval_queries = [
        "삼성전자 12월 주가는?",
        "거래량이 가장 많았던 날",
        "반도체 주식 상승일",
        "코스피 시가총액 1위 종목",
        "배터리 소재 관련 주가",
    ]

    if not corpus:
        print("  ⚠️  비교에 사용할 corpus가 없습니다")
        return

    print("  corpus 임베딩 생성 중...")
    emb_base = base_model.encode(corpus, convert_to_tensor=True, show_progress_bar=False)
    emb_ft = ft_model.encode(corpus, convert_to_tensor=True, show_progress_bar=False)

    for query in eval_queries:
        print(f"\n  질문: {query}")
        print("  " + "─" * 62)

        hits_base = util.semantic_search(
            base_model.encode(query, convert_to_tensor=True), emb_base, top_k=3
        )[0]
        hits_ft = util.semantic_search(
            ft_model.encode(query, convert_to_tensor=True), emb_ft, top_k=3
        )[0]

        print("  [베이스 모델 Top-3]")
        for rank, hit in enumerate(hits_base, 1):
            snippet = corpus[hit["corpus_id"]][:65].replace("\n", " ")
            print(f"    {rank}. score={hit['score']:.4f}  {snippet}...")

        print("  [Fine-tuned 모델 Top-3]")
        for rank, hit in enumerate(hits_ft, 1):
            snippet = corpus[hit["corpus_id"]][:65].replace("\n", " ")
            print(f"    {rank}. score={hit['score']:.4f}  {snippet}...")


# ── 기능 5: 모델 저장 ─────────────────────────────────────────────────────────

def save_model(model: SentenceTransformer, path: str) -> None:
    print(f"\n[기능 5] 모델 저장: {path}")
    os.makedirs(path, exist_ok=True)
    model.save(path)
    print(f"  저장 완료: {os.path.abspath(path)}")


# ── 메인 ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 65)
    print("  한국 주식 도메인 임베딩 Fine-tuning (BAAI/bge-m3)")
    print("=" * 65)

    get_device()  # 장치 정보 출력 (CPU 전용 모드로 실행)

    # 기능 1: 모두 CPU로 로드
    base_model = load_model("cpu", label="베이스 모델(비교용)")

    # 기능 2: 학습 데이터
    dataset, corpus = build_training_dataset()

    # 기능 3: fine-tuning (CPU)
    ft_model = load_model("cpu", label="Fine-tuning 모델")
    finetune(ft_model, dataset, OUTPUT_PATH)

    # 기능 4: 비교
    compare_models(base_model, ft_model, corpus)

    # 기능 5: 저장
    save_model(ft_model, OUTPUT_PATH)

    print("\n완료!")


if __name__ == "__main__":
    main()
