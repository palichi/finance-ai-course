# 🔍 ChromaDB 구축 확인 가이드

> `build_db.py` 실행 후 데이터가 올바르게 저장됐는지 확인하는 3가지 방법

---

## 확인 방법 요약

| 방법 | 난이도 | 소요시간 | 특징 |
|------|--------|---------|------|
| 방법 1 · 터미널 확인 | ⭐ 쉬움 | 30초 | 가장 빠름 |
| 방법 2 · 검색 테스트 | ⭐⭐ 보통 | 1분 | 학생 반응 가장 좋음 |
| 방법 3 · Streamlit 앱 | ⭐⭐⭐ 실습 | 10분 | 가장 시각적 · Claude Code 실습 |

---

## 방법 1 · 터미널에서 바로 확인 (가장 빠름)

`build_db.py` 실행 직후 터미널에서 아래 명령어를 입력합니다.

```bash
python -c "
import chromadb
db  = chromadb.PersistentClient(path='./chroma_db')
col = db.get_collection('stock_data')

print('=== ChromaDB 구축 확인 ===')
print(f'저장된 문서 수: {col.count():,}건')

# 샘플 1건 꺼내보기
result = col.peek(limit=1)
print()
print('=== 저장된 문서 샘플 (1건) ===')
print('[문서 내용]')
print(result[\"documents\"][0])
print()
print('[메타데이터]')
print(result[\"metadatas\"][0])
print()
print('[벡터 앞 5개]')
print(result[\"embeddings\"][0][:5])
"
```

### 출력 예시

```
=== ChromaDB 구축 확인 ===
저장된 문서 수: 2,450건

=== 저장된 문서 샘플 (1건) ===
[문서 내용]
2024년 01월 02일 삼성전자(005930, KOSPI) 주가:
종가 78,500원 (전일대비 +500원, +0.64%) ...

[메타데이터]
{'date': '20240102', 'ticker': '005930', 'name': '삼성전자', 'market': 'KOSPI'}

[벡터 앞 5개]
[0.0234, -0.0412, 0.0819, 0.0156, -0.0334]
```

### 확인 포인트

```
✅ 저장된 문서 수 → 2,000건 이상이면 정상
✅ 문서 내용     → 자연어 문장이 보이면 정상
✅ 메타데이터    → date, ticker, name, market 이 있으면 정상
✅ 벡터          → 소수점 숫자들이 보이면 정상
```

---

## 방법 2 · 자연어 검색 테스트 (학생들이 가장 신기해 하는 것)

숫자 데이터에 자연어 질문을 던져서 관련 데이터를 찾아주는 것을 확인합니다.

```bash
python -c "
import chromadb
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv('../../.env')
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
db     = chromadb.PersistentClient(path='./chroma_db')
col    = db.get_collection('stock_data')

# 질문을 벡터로 변환 후 검색
question = '삼성전자 주가가 가장 높았던 날'
emb = client.embeddings.create(
    model='text-embedding-3-small',
    input=question
).data[0].embedding

result = col.query(query_embeddings=[emb], n_results=3)

print(f'질문: {question}')
print()
for i, (doc, meta, dist) in enumerate(zip(
    result['documents'][0],
    result['metadatas'][0],
    result['distances'][0]
), 1):
    print(f'{i}위 (유사도: {1-dist:.3f})')
    print(f'   {doc[:70]}...')
    print()
"
```

### 출력 예시

```
질문: 삼성전자 주가가 가장 높았던 날

1위 (유사도: 0.923)
   2024년 07월 10일 삼성전자(005930, KOSPI) 주가: 종가 87,800원...

2위 (유사도: 0.891)
   2024년 07월 11일 삼성전자(005930, KOSPI) 주가: 종가 86,500원...

3위 (유사도: 0.876)
   2024년 03월 29일 삼성전자(005930, KOSPI) 주가: 종가 85,200원...
```

### 다양한 질문으로 테스트해보세요

```
"삼성전자 주가가 가장 높았던 날"
"거래량이 가장 많았던 날"
"SK하이닉스가 많이 오른 날"
"코스피 종목이 하락한 날"
"12월 주가 데이터"
```

> 💡 이 순간 학생들이 "숫자만 저장했는데 자연어 질문으로 찾아준다!" 는 것을 체감합니다.

---

## 방법 3 · Streamlit 확인 앱 (가장 시각적)

→ **별도 실습 가이드 참고:** [`CONFIRM_DB_LAB.md`](CONFIRM_DB_LAB.md)

Claude Code로 `confirm_db.py` 를 직접 만들고  
브라우저에서 시각적으로 확인하는 실습입니다.

---

## 강의 추천 순서

```
① build_db.py 실행 (3~5분 대기)
        ↓
② 방법 1 · 터미널에서 "2,450건 저장됨" 빠르게 확인
        ↓
③ 방법 2 · 자연어 검색 시연 → 학생들 반응 유도
        ↓
④ 방법 3 · Streamlit 앱 실습 (CONFIRM_DB_LAB.md 참고)
```

---

## ❓ 자주 묻는 질문

**Q. `chroma_db` 폴더가 없다고 오류가 나요**
```bash
# build_db.py 를 먼저 실행
python build_db.py
```

**Q. 저장된 문서 수가 0건이에요**
```bash
# stock_prices.csv 가 있는지 확인
ls ../03_fss_api/data/
# 없으면 collect_data.py 먼저 실행
cd ../03_fss_api && python collect_data.py
```

**Q. 유사도가 0.5 이하로 낮게 나와요**
```
정상입니다.
질문과 데이터의 표현 방식이 다를수록 유사도가 낮아집니다.
더 구체적인 질문으로 바꿔보세요.
예: "주가" → "삼성전자 종가"
```
