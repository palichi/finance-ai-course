# 📁 Day 2 · 05 · ChromaDB 가격 패턴 검색 DB 구축

## 이 실습에서 배우는 것
- "텍스트 임베딩"이 아닌 "수치 패턴 임베딩"의 개념
- 일별 시세를 슬라이딩 윈도우로 쪼개서 벡터로 만드는 방법
- 패턴 다음에 실제로 일어난 결과를 metadata로 함께 저장하는 방법
- "지금 패턴과 비슷한 과거 사례 + 그 결과"를 검색하는 방법

---

## 📂 이 폴더의 파일 구성

```
day2/05_pattern_db/
├── chroma_pattern_store.py   ← 실습에서 Claude Code로 직접 만들기
└── data/
    └── chroma_pattern_db/    ← 벡터 DB 저장 폴더 (자동 생성)
```

> `chroma_pattern_store.py` 는 **이 실습에서 직접 만듭니다.**

> ⚠️ 이전 실습(`04_chromadb/build_text_db.py`)에서 만든 ChromaDB와
> **완전히 별개의 DB**입니다. 절대 혼동하지 마세요.

| 구분 | 이전 실습 (build_text_db.py) | 이번 실습 (chroma_pattern_store.py) |
|---|---|---|
| 저장 경로 | `./chroma_db_text` | `./data/chroma_pattern_db` |
| 컬렉션명 | `stock_text_documents` | `price_patterns` |
| 저장 단위 | 자연어 문장 1건 (하루치 시세 설명) | 20일치 가격 패턴 벡터 1건 |
| 임베딩 방식 | OpenAI 텍스트 임베딩 모델 | 직접 계산한 수치 정규화 벡터 |
| 검색 목적 | "삼성전자 12월 주가" 같은 문장 검색 | "이 가격 모양과 비슷한 과거 사례" 검색 |

---

## 🖥 실습 순서

---

### STEP 1 · 폴더 이동 + 패키지 설치

```bash
cd day2/05_pattern_db
```

```bash
pip install chromadb pandas numpy --break-system-packages
```

---

### STEP 2 · Claude Code 실행

```bash
claude
```

---

### STEP 3 · [Claude Code 실습] chroma_pattern_store.py 만들기

Claude Code가 실행되면 아래 프롬프트를 **그대로 복사해서 붙여넣기** 하세요:

```
chroma_pattern_store.py 파일을 만들어줘.
(이 DB는 day2/04_chromadb/build_text_db.py 가 만드는
 자연어 문장 검색용 ChromaDB와는 완전히 별개의 DB입니다.
 이건 "가격 패턴"을 직접 벡터로 만들어서 검색하는 용도입니다.)

기능 1 · 일별 시세 데이터(컬럼: basDt, srtnCd, itmsNm, clpr, mkp, hipr, lopr, trqu, fltRt)를
  20일 단위 슬라이딩 윈도우로 쪼개서 "패턴"으로 만들어줘.
  각 패턴은 종가(clpr), 시가(mkp), 고가(hipr), 저가(lopr), 거래량(trqu), 등락률(fltRt) 6개를
  벡터로 변환해줘.

기능 2 · 가격은 절댓값이 아니라 "모양"으로 비교해야 하니까
  윈도우의 첫날 종가를 기준으로 상대 변화율로 정규화해줘.
  예: norm_close = clpr / 첫날종가 - 1.0
  거래량은 그 윈도우 내 평균을 기준으로 정규화해줘.

기능 3 · 각 패턴을 ChromaDB의 PersistentClient 로 저장해줘.
  저장 경로는 함수 인자로 받게 해줘 (기본값: ./data/chroma_pattern_db)
  collection 이름도 인자로 받게 해줘 (기본값: price_patterns)

기능 4 · 각 패턴을 저장할 때 "그 패턴 다음 5일 후 실제로 일어난 수익률"을
  metadata 에 함께 저장해줘.
  metadata 항목: symbol, base_date, base_price, future_return_pct, direction(up/down)
  마지막 5일은 미래 결과를 모르니까 패턴 생성 대상에서 제외해줘.

기능 5 · "지금 패턴"을 받아서 ChromaDB에서 가장 비슷한 과거 패턴 top_k개를 찾고
  그 패턴들 다음에 실제로 일어난 결과를 통계로 요약해서 반환하는 함수를 만들어줘.
  반환값: 찾은 패턴 수, 평균 미래수익률, 수익률 표준편차, 상승확률, 상위 유사사례 리스트

기능 6 · 클래스명은 PricePatternStore 로 만들고
  build_from_dataframe(), search_similar_patterns(), count() 메서드를 포함해줘.

기능 7 · ChromaDB upsert 시 한 번에 너무 많이 넣으면 느려지니까
  500개씩 배치로 나눠서 저장해줘.

기능 8 · build_from_dataframe() 호출 시 데이터 건수가
  window_size + future_days 보다 적으면
  "⚠️ 데이터가 부족합니다 (최소 N일 필요, 현재 M일)" 출력하고
  빈 리스트를 반환하는 방어 코드를 추가해줘.

기능 9 · 파일 맨 아래에 실행 예시(if __name__ == "__main__":)를 추가해줘.
  가상의 일별 시세 데이터를 만들고
  컬럼명을 basDt, srtnCd, clpr, mkp, hipr, lopr, trqu, fltRt 형태로 맞춘 뒤
  ChromaDB에 저장하고, 저장된 개수와 유사 패턴 검색 결과를 출력해줘.

파일명: chroma_pattern_store.py
```

---

### STEP 4 · chroma_pattern_store.py 실행 확인

Claude Code가 파일을 만들면 **기존 터미널로 돌아가서** 실행:

```bash
python chroma_pattern_store.py
```

출력 예시:
```
✅ DEMO005930: 패턴 475개 ChromaDB에 저장 완료

📦 저장된 패턴 총 개수: 475

🔍 유사 패턴 검색 결과
   찾은 패턴 수    : 10
   평균 미래수익률 : -1.61%
   상승확률        : 30.0%
```

> 예상 소요 시간: 약 10~30초 (데이터 건수에 따라 다름)
> VS Code에서 `pattern_to_vector()` 함수를 열어
> 가격을 "절댓값"이 아니라 "모양(상대 변화율)"으로 정규화하는 이유를 확인하세요.
> 강사가 설명하는 시간입니다.

---

### STEP 5 · 저장된 패턴 확인

```bash
python -c "
from chroma_pattern_store import PricePatternStore
store = PricePatternStore(db_path='./data/chroma_pattern_db')
print('📦 저장된 패턴 수:', store.count())
"
```

출력 예시:
```
📦 저장된 패턴 수: 475
```

> ⚠️ 패턴 수가 0 이면 STEP 3의 `build_from_dataframe()` 호출이
> 실제로 실행되지 않은 것입니다. `if __name__ == "__main__":` 블록을 확인하세요.

---

### STEP 6 · 직접 패턴 검색해보기

```bash
python -c "
from chroma_pattern_store import PricePatternStore
import pandas as pd

store = PricePatternStore(db_path='./data/chroma_pattern_db')

# 저장할 때 쓴 것과 같은 형식의 데이터에서 최근 20일을 가져와 검색
# (실전에서는 오늘 기준 최근 20일 시세로 교체)
"
```

> 이 STEP은 다음 실습(`ask_pattern_tool.py`)에서
> 날짜를 입력해서 바로 조회할 수 있는 CLI 도구로 더 편하게 확장합니다.

---

### STEP 7 · [추가 실습] 기능 더 넣어보기

시간이 남으면 Claude Code에 자유롭게 요청해보세요:

**미션 1 · 실데이터로 교체**
```
chroma_pattern_store.py 의 실행 예시 부분에서
가상 데이터 대신 data/stock_price.csv (또는 종목별로 분리된
data/ppo_ready/{종목코드}.csv) 파일을 pandas로 읽어서
build_from_dataframe() 에 넘기도록 수정해줘.
```

**미션 2 · 여러 종목 동시 저장**
```
build_from_dataframe() 을 여러 종목에 대해 반복 호출해서
ChromaDB에 종목별로 함께 저장하는
build_from_multiple_symbols(df_dict) 함수를 추가해줘.
종목 풀이 작으면 유사 패턴 검색의 신뢰도가 떨어지니
같은 업종 여러 종목을 함께 저장하는 것이 좋다는 주석을 달아줘.
```

**미션 3 · 미래 기간(future_days) 조절**
```
chroma_pattern_store.py 의 future_days 기본값(5일) 대신
1일, 10일, 20일 등 여러 기간으로 각각 패턴 DB를 만들어서
기간별로 상승확률이 어떻게 달라지는지 비교하는
compare_future_days(df, days_list) 함수를 추가해줘.
```

---

## 📐 패턴 임베딩 개념 설명

```
일반 텍스트 임베딩 (build_text_db.py 에서 한 것)
"삼성전자 종가" → [0.123, -0.456, 0.789, ...]  (의미 공간)

패턴 임베딩 (이번 실습)
[20일치 종가·시가·고가·저가·거래량·등락률] → [0.02, -0.01, 0.03, ...]  (모양 공간)

두 임베딩은 차원의 "의미"가 완전히 다르므로
하나의 ChromaDB collection에 절대 섞지 않습니다.
```

```
패턴이 비슷하다 = 벡터 거리가 가깝다
        ↓
그 패턴들 "다음에" 실제로 일어난 수익률을 모아서 통계 냄
        ↓
"이런 모양의 패턴은 보통 이렇게 됐다" 라는 참고 신호 생성
```

> ⚠️ 이건 **확정된 예측이 아니라 참고용 통계**입니다.
> 상승확률이 50% 근처로 나오면 뚜렷한 신호가 없다는 뜻이며,
> 그 자체가 정상적인 결과입니다.

---

## ⚠️ 알려진 주의사항

### 다른 ChromaDB 폴더와 절대 혼동하지 않기

```
day2/04_chromadb/chroma_db_text/      ← 자연어 문장 검색 DB
day2/05_pattern_db/data/chroma_pattern_db/   ← 가격 패턴 검색 DB

저장 경로(db_path)와 컬렉션명(collection_name)이
서로 다른지 항상 확인하세요. 같은 이름을 쓰면
"기존 컬렉션 삭제 후 재생성" 로직이 다른 실습의 DB를 지울 수 있습니다.
```

### 종목 1개만으로는 신호가 약할 수 있음

```
유사 패턴 검색 결과의 상승확률이 항상 50% 근처로만 나온다면
종목 1개의 데이터 풀이 너무 작은 것이 원인일 수 있습니다.
미션 2(여러 종목 동시 저장)를 먼저 시도해보세요.
```

### "미래 결과"가 확정되는 시점 주의

```
오늘 패턴을 저장하려면 최소 future_days(기본 5일) 만큼
지난 시점이어야 "그 다음 실제 수익률"을 알 수 있습니다.
가장 최근 5일치는 결과를 아직 모르므로
build_from_dataframe() 이 자동으로 패턴 생성 대상에서 제외합니다.
```

---

## ❓ 자주 묻는 질문

**Q. 패턴 수가 0건으로 나와요**
```
원인: 데이터 건수가 window_size(20일) + future_days(5일) = 25일보다 적음
→ 최소 25일 이상의 연속된 시세 데이터가 필요합니다.
```

**Q. ChromaDB 패키지 설치 시 오류가 나요**
```bash
pip install chromadb --break-system-packages
```

**Q. chroma_pattern_store.py 를 여러 번 실행하면 패턴이 중복 저장되나요?**
```
아닙니다. upsert() 를 사용하므로 같은 ID(symbol_날짜)는
덮어쓰기 됩니다. 중복 저장 걱정 없이 다시 실행해도 됩니다.
```

**Q. 유사도(similarity)가 낮게 나와요**
```
가격 패턴은 코사인 유사도 기준으로
일반 텍스트보다 분포가 다르게 나타날 수 있습니다.
유사도 자체보다 "찾은 패턴들의 평균 미래수익률·상승확률"이
더 중요한 지표입니다.
```

**Q. ChromaDB 데이터 삭제하려면?**
```bash
# Windows
rmdir /s /q data\chroma_pattern_db

# Mac / Linux
rm -rf data/chroma_pattern_db/
# 삭제 후 chroma_pattern_store.py 다시 실행 필요
```

---

> 💡 이 실습의 핵심 포인트
> `chroma_pattern_store.py` 는 수강생이 Claude Code로 직접 생성 → 바이브코딩 체험
> "텍스트가 아닌 숫자 패턴도 ChromaDB로 검색할 수 있다" 는 것을
> 직접 경험하는 것이 이 실습의 목표입니다.
