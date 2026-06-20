# 📁 Day 2 · 04-1 · ChromaDB 벡터 데이터베이스 구축

## 이 실습에서 배우는 것
- 임베딩(Embedding) 개념: 텍스트 → 숫자 벡터 변환
- ChromaDB에 주식 데이터 저장
- 유사도 검색 원리와 실습
- 코사인 유사도로 관련 문서 찾기

---

## 📂 이 폴더의 파일 구성

```
day2/04_chromadb/
├── build_text_db.py    ← 실습에서 Claude Code로 직접 만들기
├── search_test.py      ← 실습에서 Claude Code로 직접 만들기
└── chroma_db_text/     ← 벡터 DB 저장 폴더 (자동 생성)
```

> `build_text_db.py`, `search_test.py` 는 **이 실습에서 직접 만듭니다.**
>
> ⚠️ 이 폴더에는 이후 실습(가격 패턴 검색용 `chroma_pattern_store.py`)에서
> 별도의 ChromaDB(`./data/chroma_pattern_db/`)도 만들게 됩니다.
> 이번 실습에서 만드는 `chroma_db_text/` 는 **자연어 문장 검색용 DB**이고,
> 그것과는 **완전히 별개의 DB**라는 점을 꼭 기억하세요.

---

## 🖥 실습 순서

---

### STEP 1 · 폴더 이동 + 파일 확인

```bash
cd day2/04_chromadb
```

```bash
ls
#  README.md  만 있으면 정상
```

**새 터미널 탭을 열고:**

```bash
claude
```

---

### STEP 2 · [Claude Code 실습] build_text_db.py 만들기

Claude Code가 실행되면 아래 프롬프트를 **그대로 복사해서 붙여넣기** 하세요:

```
day2/04_chromadb/build_text_db.py 파일을 만들어줘.

day2/03_fss_api/data/stock_prices.csv 에서 수집한 주식 데이터를
ChromaDB 벡터 데이터베이스로 구축하는 프로그램이야.
(이 DB는 이후 실습에서 만드는 가격 패턴 검색용 ChromaDB와는
 완전히 별개의 DB입니다. 이건 "자연어 문장"을 임베딩해서
 텍스트로 검색하는 용도입니다.)

기본 설정:
  .env 파일: ../../.env 경로에서 읽기
  CSV 파일 경로: ../03_fss_api/data/stock_prices.csv
  ChromaDB 저장 경로: ./chroma_db_text
  OpenAI 임베딩 모델: text-embedding-3-small

함수 1 · text_to_embedding(text)
  텍스트를 OpenAI 임베딩 API로 1536차원 벡터로 변환
  반환: 벡터 리스트

함수 2 · row_to_document(row)
  CSV 한 행(pandas Series)을 자연어 문장으로 변환
  포함할 정보: 날짜, 종목명, 종목코드, 시장구분,
              종가, 전일대비, 등락률, 시가, 고가, 저가,
              거래량, 시가총액
  예시 형식:
  "2024년 12월 31일 삼성전자(005930, KOSPI) 주가:
   종가 78,500원 (전일대비 +500원, +0.64%),
   시가 78,000원, 고가 79,000원, 저가 77,500원,
   거래량 12,345,678주, 시가총액 468,000억원"

함수 3 · build(batch_size=50)
  전체 구축 프로세스:

  1단계 · CSV 파일이 없으면 에러 메시지 출력 후 종료
    "❌ 데이터 파일 없음: (경로)"
    "먼저 day2/03_fss_api/collect_data.py 를 실행하세요"

  2단계 · ChromaDB 초기화
    PersistentClient 로 ./chroma_db_text 에 연결
    기존 "stock_text_documents" 컬렉션이 있으면 삭제 후 재생성
    코사인 유사도(cosine) 방식 사용

  3단계 · 배치 임베딩 + 저장
    각 행을 자연어 문장으로 변환 → 임베딩 생성
    문서, 임베딩, ID, 메타데이터를 리스트에 쌓기
    메타데이터는 date, ticker, name, market 포함
    batch_size(50건)씩 모아서 ChromaDB에 저장
    100건마다 진행률을 프로그레스 바로 출력
    예: [====================] 1,000/2,450 (41%)

  4단계 · 완료 메시지 출력
    "✅ ChromaDB 구축 완료: N건"
    "💾 저장 위치: (절대경로)"

파일명: build_text_db.py
```

---

### STEP 3 · build_text_db.py 코드 먼저 읽어보기

```bash
# VS Code에서 build_text_db.py 열어서 코드 구조 확인
# 강사 설명 듣는 시간
```

---

### STEP 4 · 벡터 DB 구축 실행

```bash
python build_text_db.py
# 📥 데이터 로딩: 2,450건
# 🔢 임베딩 생성 중 (배치 50건씩)...
# [====================] 2,450/2,450 (100%)
# ✅ ChromaDB 구축 완료: 2,450건
# 💾 저장 위치: ./chroma_db_text/
```

> 예상 소요 시간: 약 3~5분
> OpenAI 임베딩 API를 호출하므로 인터넷 연결 필요

---

### STEP 5 · Claude Code 실행

**새 터미널 탭 열기** (Ctrl + Shift + `)

```bash
# day2/04_chromadb 폴더 안에서 실행
claude
```

---

### STEP 6 · [Claude Code 실습] search_test.py 만들기

Claude Code가 실행되면 아래 프롬프트를 **그대로 붙여넣기** 하세요:

```
build_text_db.py 를 참고해서 search_test.py 파일을 만들어줘.

기능:
1. ./chroma_db_text/ 폴더에서 ChromaDB를 로딩해줘
   (컬렉션 이름: stock_text_documents)

2. 아래 5개 질문으로 자동 검색 테스트를 실행해줘
   - "삼성전자 12월 주가"
   - "코스피 상승한 날"
   - "거래량이 많았던 종목"
   - "반도체 주식 최근 흐름"
   - "주가가 많이 오른 날은?"

3. 각 질문마다 아래 형식으로 출력해줘
   ❓ 질문: 삼성전자 12월 주가
   📄 검색 결과 (상위 3건):
     1. [20241231] 삼성전자(005930) - 유사도: 0.92
        2024년 12월 31일 삼성전자...
     2. ...

4. --interactive 옵션을 붙여서 실행하면
   직접 질문을 입력할 수 있는 대화형 모드로 동작해줘
   종료: q 입력 또는 Ctrl+C

5. chroma_db_text 폴더가 없으면
   "먼저 build_text_db.py 를 실행하세요" 안내 후 종료해줘

6. .env 파일은 ../../.env 경로에서 읽어줘

파일명: search_test.py
```

---

### STEP 7 · search_test.py 자동 테스트 실행

```bash
python search_test.py
# ❓ 질문: 삼성전자 12월 주가
# 📄 검색 결과 (상위 3건):
#   1. [20241231] 삼성전자(005930) - 유사도: 0.92
#   ...
```

---

### STEP 8 · 대화형 검색 실습

```bash
python search_test.py --interactive
# 질문을 직접 입력해보세요:
# > 거래량이 가장 많았던 날은?
# > 삼성전자가 많이 오른 날은?
# > 종료: q
```

---

### STEP 9 · [추가 실습] 기능 더 넣어보기

**미션 1 — 특정 종목만 필터링**
```
search_test.py 에 종목코드로 필터링하는 기능을 추가해줘.
예: python search_test.py --ticker 005930
이렇게 실행하면 삼성전자 데이터에서만 검색해줘.
ChromaDB의 where 파라미터를 사용해줘.
```

**미션 2 — 검색 결과 개수 조절**
```
search_test.py 에서 검색 결과 개수를
--top-k 옵션으로 조절할 수 있게 해줘.
예: python search_test.py --top-k 10
기본값은 3으로 해줘.
```

**미션 3 — 유사도 기준 필터**
```
search_test.py 에서 유사도가 0.7 미만인 결과는
"관련 데이터 없음" 으로 표시해줘.
```

---

## 📐 임베딩 개념 설명

```
텍스트          →    임베딩 벡터 (1536차원)
"삼성전자 종가"  →   [0.123, -0.456, 0.789, ...]
"반도체 주가"   →   [0.118, -0.451, 0.801, ...]

두 텍스트의 의미가 비슷할수록
벡터 간의 코사인 유사도가 1에 가까워짐
```

### 유사도 기준
```
1.0  →  완전히 같음
0.9+ →  매우 유사
0.7+ →  관련 있음
0.5  →  관련 없음
```

> ⚠️ 금융 수치 데이터(이번 실습처럼 가격·등락률을 문장으로 바꾼 경우)는
> 일반 텍스트·뉴스보다 유사도 점수가 전반적으로 낮게 나오는 것이 정상입니다.
> 권장 기준: 일반 문서 0.7 이상 / 금융 수치 데이터 0.4 이상

---

## 🔗 이후 실습과의 관계 (중요)

```
이번 실습 (build_text_db.py)          다음 실습 (chroma_pattern_store.py)
────────────────────────────         ────────────────────────────────
저장 경로: ./chroma_db_text           저장 경로: ./data/chroma_pattern_db
컬렉션:   stock_text_documents        컬렉션:   price_patterns
저장 단위: 자연어 문장 1건             저장 단위: 20일 가격 패턴 벡터
용도:     "삼성전자 12월 주가" 검색     용도:     "이 가격모양과 비슷한 과거사례" 검색

→ 두 DB는 폴더와 컬렉션명이 완전히 분리되어 있어
   서로 덮어쓰거나 충돌하지 않습니다.
```

---

## ⚠️ 알려진 주의사항

### 다른 ChromaDB 폴더와 혼동하지 않기

이후 실습에서 `chroma_pattern_store.py` 를 만들 때
**저장 경로(`./data/chroma_pattern_db`)와 컬렉션명(`price_patterns`)이
이번 실습과 다른지 반드시 확인**하세요. 같은 이름을 쓰면
"기존 컬렉션 삭제 후 재생성" 로직이 서로의 데이터를 지울 수 있습니다.

---

## ❓ 자주 묻는 질문

**Q. 임베딩 생성에 비용이 드나요?**
```
OpenAI text-embedding-3-small 기준:
$0.02 / 1M 토큰
2,000건 문서 기준 약 $0.01 (약 13원) → 거의 무료
```

**Q. build_text_db.py 를 여러 번 실행하면?**
```
기존 컬렉션을 삭제하고 새로 만듭니다.
중복 저장 걱정 없이 다시 실행해도 됩니다.
```

**Q. ChromaDB 데이터 삭제하려면?**
```bash
# Windows
rmdir /s /q chroma_db_text

# Mac / Linux
rm -rf chroma_db_text/
# 삭제 후 build_text_db.py 다시 실행 필요
```

**Q. chroma_db_text 폴더가 없다고 오류가 나요**
```bash
# build_text_db.py 를 먼저 실행하지 않은 것
python build_text_db.py
# 완료 후 다시 시도
```

**Q. 유사도가 낮게 나와요 (0.7 미만)**
```
금융 수치 데이터는 단순 숫자 나열이라
일반 텍스트보다 유사도가 낮게 나오는 것이 정상입니다.

권장 유사도 기준:
  일반 문서·뉴스  → 0.7 이상
  금융 수치 데이터 → 0.4 이상

search_test.py 의 유사도 기준을 0.4 로 낮춰서 사용하세요.
```

---

> 💡 이 실습의 핵심 포인트
> `build_text_db.py` 는 수강생이 Claude Code로 직접 생성 → 바이브코딩 체험
> `search_test.py` 도 수강생이 Claude Code로 직접 생성 → 바이브코딩 체험
> "AI한테 말로 설명하면 코드가 만들어진다" 는 것을 직접 경험하는 것이 목표
