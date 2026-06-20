# build_db.py 완전 해설

> ChromaDB 벡터 데이터베이스 구축 프로그램  
> 바이브코딩으로 만드는 금융 AI 시스템 · Day 2-04

---

## 한마디 요약

> **주식 데이터를 AI가 검색할 수 있는 형태로 변환하여 저장하는 프로그램**

---

## 1. 데이터는 어디서 오나요?

`build_db.py` 는 **직접 데이터를 수집하지 않습니다.**  
앞 실습인 `collect_data.py` 가 먼저 수집해서 저장한 파일을 읽어옵니다.

```
[Day 2 · 03_fss_api]                    [Day 2 · 04_chromadb]
collect_data.py                    →     build_db.py
금융위 API 호출                          stock_prices.csv 읽기
→ stock_prices.csv 저장                  → ChromaDB 구축
```

---

## 2. 데이터 흐름 전체 순서

```
① 금융위원회 공공 API        ← 인터넷에서 자동 수집 (무료)
        ↓
② collect_data.py 실행       ← 수강생이 직접 실행
        ↓
③ data/stock_prices.csv 저장 ← 컴퓨터에 자동 저장
        ↓
④ build_db.py 실행           ← 수강생이 직접 실행
        ↓
⑤ chroma_db/ 폴더 생성       ← 완성된 벡터 DB
```

---

## 3. 수강생이 직접 해야 하는 것

**딱 2가지 명령어만 실행하면 됩니다.**

```bash
# Step 1: 주식 데이터 수집 (03_fss_api 폴더에서)
cd day2/03_fss_api
python collect_data.py
# → 금융위 API에서 자동으로 가져와서 CSV로 저장

# Step 2: 벡터 DB 구축 (04_chromadb 폴더에서)
cd ../04_chromadb
python build_db.py
# → 위 CSV를 읽어서 ChromaDB로 변환
```

> 데이터를 직접 만들거나 준비할 필요가 없습니다.  
> 단, `.env` 파일에 `FSS_API_KEY` 가 입력되어 있어야 합니다.  
> 발급 방법 → [`docs/API_KEYS.md`](../../docs/API_KEYS.md)

---

## 4. 수집되는 데이터 기준

`collect_data.py` 에서 아래 기준으로 수집합니다:

| 항목 | 내용 |
|------|------|
| 종목 수 | 10개 |
| 수집 기간 | 최근 1년치 |
| 출처 | 금융위원회 공공데이터포털 (data.go.kr) |
| 형식 | 일별 OHLCV (시가·고가·저가·종가·거래량) |
| 예상 건수 | 약 2,450건 (10종목 × 약 245 거래일) |
| 비용 | 무료 |

### 수집 대상 종목

| 종목코드 | 종목명 |
|---------|--------|
| 005930 | 삼성전자 |
| 000660 | SK하이닉스 |
| 005380 | 현대차 |
| 000270 | 기아 |
| 035420 | NAVER |
| 035720 | 카카오 |
| 051910 | LG화학 |
| 006400 | 삼성SDI |
| 068270 | 셀트리온 |
| 207940 | 삼성바이오로직스 |

---

## 5. 전체 흐름 한눈에 보기

```
stock_prices.csv  →  텍스트 변환  →  벡터 변환  →  ChromaDB 저장
(숫자 주가 데이터)    (자연어 문장)    (숫자 1536개)   (검색 가능한 DB)
```

이 프로그램은 CSV 파일의 숫자 데이터를 AI가 이해하고 검색할 수 있는 형태로 변환하여 ChromaDB에 저장합니다.

---

## 6. 함수별 역할 상세 설명

---

### 6-1. `text_to_embedding()` — 텍스트를 숫자 배열로 변환

OpenAI 서버에 텍스트를 보내면 **1536개의 숫자 배열(벡터)** 로 돌려줍니다.  
이것을 **임베딩(Embedding)** 이라고 부릅니다.

```python
def text_to_embedding(text: str) -> list[float]:
    resp = client.embeddings.create(
        model="text-embedding-3-small",  # OpenAI 임베딩 모델
        input=text,
    )
    return resp.data[0].embedding  # 숫자 1536개짜리 리스트 반환
```

#### 입력과 출력

```
입력: "삼성전자 종가 78,500원"
출력: [0.123, -0.456, 0.789, 0.012, -0.334, ... ]  ← 숫자 1536개
```

#### 왜 숫자로 바꾸나요?

의미가 비슷한 문장은 비슷한 숫자 배열이 만들어집니다.

```
"삼성전자 주가"   → [0.123, -0.456, 0.789, ...]  ─┐
"삼성전자 종가"   → [0.121, -0.451, 0.791, ...]  ─┘ 거의 같음 (유사도 0.99)
"오늘 날씨"       → [0.891,  0.234,-0.567, ...]     완전히 다름 (유사도 0.1)
```

나중에 "삼성전자 주가 알려줘" 라고 물으면  
이 숫자 배열로 가장 가까운 데이터를 자동으로 찾아줍니다.

---

### 6-2. `row_to_document()` — CSV 한 행을 자연어 문장으로 변환

CSV의 숫자 데이터를 AI가 이해하기 쉬운 자연어 문장으로 바꿉니다.

#### 변환 전 (CSV 원본 데이터)

```
basDt     srtnCd   itmsNm    clpr   vs    fltRt  mkp    hipr   lopr   trqu
20241231  005930   삼성전자  78500  +500  +0.64  78000  79000  77500  12345678
```

#### 변환 후 (자연어 문장)

```
"2024년 12월 31일 삼성전자(005930, KOSPI) 주가:
 종가 78,500원 (전일대비 +500원, +0.64%),
 시가 78,000원, 고가 79,000원, 저가 77,500원,
 거래량 12,345,678주, 시가총액 468,000억원"
```

> 💡 AI(LLM)는 숫자 표보다 자연어 문장을 훨씬 잘 이해합니다.  
> 나중에 GPT에 데이터를 넘겨줄 때 더 정확한 답변이 나옵니다.

---

### 6-3. `build()` — 전체 구축 프로세스 (3단계)

#### 단계 1 · 데이터 로딩

```python
df = pd.read_csv(DATA_FILE)
print(f"📥 데이터 로딩: {len(df):,}건")
```

앞 실습(03_fss_api)에서 수집한 `stock_prices.csv` 를 읽어옵니다.  
10개 종목 × 1년치 약 2,450건의 데이터입니다.

---

#### 단계 2 · ChromaDB 초기화

```python
db  = chromadb.PersistentClient(path=CHROMA_DIR)
db.delete_collection("stock_data")  # 기존 데이터 삭제 (중복 방지)
col = db.create_collection(
    name="stock_data",
    metadata={"hnsw:space": "cosine"},  # 코사인 유사도 사용
)
```

- `./chroma_db/` 폴더에 데이터베이스를 만듭니다.
- 기존 데이터가 있으면 삭제 후 새로 만들어 중복을 방지합니다.
- 코사인 유사도: 두 벡터가 얼마나 같은 방향인지 측정 (1.0 = 완전히 같음, 0.5 = 관련 없음)

---

#### 단계 3 · 배치 임베딩 + 저장

```python
for i, (_, row) in enumerate(df.iterrows()):
    text = row_to_document(row)    # ① 자연어 변환
    emb  = text_to_embedding(text) # ② 벡터 변환 (OpenAI API 호출)

    docs.append(text)
    embeds.append(emb)
    ids.append(f"stock_{i}")
    metas.append({
        "date":   row["basDt"],    # 날짜     ← 나중에 필터 검색용
        "ticker": row["srtnCd"],   # 종목코드 ← "005930만 검색" 가능
        "name":   row["itmsNm"],   # 종목명
        "market": row["mrktCtg"],  # 시장구분
    })

    if len(docs) >= batch_size:  # 50건씩 모아서
        col.add(...)             # 한꺼번에 저장 (속도 향상)
```

#### 배치 저장의 이유

| 비교 | 한 건씩 저장 | 50건씩 배치 저장 |
|------|-------------|----------------|
| 디스크 쓰기 횟수 | 2,450번 | 49번 |
| 속도 | 느림 | 약 50배 빠름 |
| 메모리 사용 | 낮음 | 약간 높음 (무관한 수준) |

---

## 7. 메타데이터(metas)를 저장하는 이유

나중에 검색할 때 조건을 걸어서 필터링할 수 있습니다.

```python
# 메타데이터 필터 검색 예시
col.query(
    query_embeddings=[질문벡터],
    where={"ticker": "005930"},  # 삼성전자 데이터에서만 검색
    n_results=5
)

# 날짜 범위 필터
col.query(
    query_embeddings=[질문벡터],
    where={"date": {"$gte": "20241201"}},  # 12월 이후만
    n_results=5
)
```

---

## 8. 실행 결과 해석

```bash
python build_db.py

📥 데이터 로딩: 2,450건          ← CSV에서 읽은 행 수
🔢 임베딩 생성 중 (배치 50건씩)...
  [====================] 2,450/2,450 (100%)   ← 진행 상황
✅ ChromaDB 구축 완료: 2,450건   ← DB에 저장된 문서 수
💾 저장 위치: D:\AI_project\...\chroma_db
```

---

## 9. 실행 후 만들어지는 파일

```
day2/04_chromadb/
└── chroma_db/                 ← 이 폴더가 새로 생깁니다
    ├── chroma.sqlite3          ← 메타데이터 저장 (날짜·종목코드 등)
    └── [UUID폴더]/
        ├── data_level0.bin    ← 벡터 데이터 저장
        └── header.bin
```

> 이 폴더가 있으면 다음 실습(`search_test.py`, `rag_chain.py`)에서  
> 바로 불러와서 검색에 사용할 수 있습니다.

---

## 10. 비용 안내

| 항목 | 계산 | 금액 |
|------|------|------|
| 모델 | text-embedding-3-small | |
| 단가 | $0.02 / 1M 토큰 | |
| 데이터량 | 2,450건 × 평균 100토큰 | = 245,000 토큰 |
| 총 비용 | 245,000 ÷ 1,000,000 × $0.02 | ≈ $0.005 **(약 7원)** |

> ✅ 임베딩 생성 비용은 거의 무료 수준입니다. 실습에서 부담 없이 사용하세요.

---

## 11. 전체 요약

| 질문 | 답변 |
|------|------|
| 데이터를 내가 준비해야 하나? | ❌ 아니오 — 자동 수집 |
| 어디서 가져오나? | 금융위원회 공공 API (무료) |
| 무슨 데이터인가? | 주요 10개 종목의 최근 1년 주가 |
| 수동으로 할 게 있나? | `collect_data.py` 실행 1번뿐 |
| API Key가 필요한가? | ✅ FSS_API_KEY (.env 파일에 입력) |

---

## 12. 자주 묻는 질문

**Q. `stock_prices.csv` 파일이 없다고 오류가 나요**
```bash
# 03_fss_api 폴더에서 먼저 실행
cd day2/03_fss_api
python collect_data.py
# 완료 후 다시 build_db.py 실행
```

**Q. `build_db.py` 를 여러 번 실행하면?**
```
기존 컬렉션을 삭제하고 새로 만듭니다.
중복 저장 걱정 없이 다시 실행해도 됩니다.
```

**Q. ChromaDB 데이터를 삭제하려면?**
```bash
# Windows
rmdir /s /q chroma_db

# Mac / Linux
rm -rf chroma_db/
# 삭제 후 build_db.py 다시 실행 필요
```

**Q. 다른 종목 데이터도 넣을 수 있나요?**
```
collect_data.py 의 종목 리스트를 수정하면
원하는 종목을 추가할 수 있습니다.
collect_data.py → build_db.py 순서로 다시 실행하세요.
```

---

*바이브코딩으로 만드는 금융 AI 시스템 · Day 2-04 · ChromaDB 구축 · 강사: 이상목*
