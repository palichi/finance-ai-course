# 📁 Day 2 · 03 · 금융위원회 주식시세 API

## 이 실습에서 배우는 것
- 공공데이터포털 API 사용 방법
- 주식 시세 데이터 자동 수집
- pandas로 데이터 정제 및 저장
- 수집 데이터를 RAG 학습용으로 변환

---

## 📂 이 폴더의 파일 구성

```
day2/03_fss_api/
├── fss_client.py       ← 미리 제공 (API 연결 기본 코드)
├── collect_data.py     ← 실습에서 Claude Code로 직접 만들기
├── explore.py          ← 실습에서 Claude Code로 직접 만들기
└── data/               ← 수집된 CSV 저장 폴더 (자동 생성)
    └── stock_prices.csv
```

> `collect_data.py` 와 `explore.py` 는 **이 실습에서 직접 만듭니다.**
> 아래 순서대로 따라오세요.

---

## 🖥 실습 순서

---

### STEP 1 · 폴더 이동 + 파일 확인

```bash
cd day2/03_fss_api
```

```bash
# 현재 파일 목록 확인
ls
# fss_client.py  README.md  만 있으면 정상
```

---

### STEP 2 · 기본 API 연결 테스트 (제공된 파일)

```bash
python fss_client.py
```

출력 예시:
```
✅ API 연결 성공
📥 삼성전자 최근 30일 데이터 수집 중...
✅ 30건 수집 완료
📝 RAG 학습용 텍스트 변환 예시 (첫 3건):
  → 2024년 12월 31일 삼성전자(005930) 종가 78,500원 ...
```

> VS Code에서 `fss_client.py` 를 열어 코드 구조를 확인하세요.
> 강사가 이 파일을 보며 API 연결 방법을 설명합니다.

---

### STEP 3 · Claude Code 실행

**새 터미널 탭 열기** (Ctrl + Shift + `)

```bash
# day2/03_fss_api 폴더 안에서 실행
claude
```

---

### STEP 4 · [Claude Code 실습] collect_data.py 만들기

Claude Code가 실행되면 아래 프롬프트를 **그대로 복사해서 붙여넣기** 하세요:

```
make_kospi200.py 파일을 만들어줘.

기능 1 · data 폴더의 data.csv 데이터 파일을 읽어서 종목번호와 종목명 만의 kospi200.csv 파일을 만들어줘.
아래의 예 처럼 만들어
  005930  삼성전자
  000660  SK하이닉스
  005380  현대차
  000270  기아
  035420  NAVER
  035720  카카오
  051910  LG화학
  006400  삼성SDI
  068270  셀트리온
  207940  삼성바이오로직스

기능 2 · 종목코드(srtnCd) 는 반드시 문자열로 저장하고
  앞자리 0이 빠지지 않도록 zfill(6) 처리해줘
  예: 5930 → 005930
  df = get_stock_price(...) 호출 직후 아래 줄에 넣어줘:
  df["srtnCd"] = df["srtnCd"].astype(str).str.zfill(6)

기능 3 · data 폴더가 없으면 폴더를 자동으로 만들고
  data/kospi200.csv 로 저장해줘
  인코딩은 utf-8-sig 로 해줘 (한글 깨짐 방지)
```


```
fss_client.py 를 참고해서 collect_data.py 파일을 만들어줘.

기능 1 · data/kospi200.csv 파일에 있는 종목의 최근 3년치 주가 데이터를 수집해줘
  data/kospi200_list.csv 를 읽어서 종목코드, 종목명 리스트로 사용
  컬럼: srtnCd(종목코드), itmsNm(종목명)
  srtnCd 는 읽을 때 바로 astype(str).str.zfill(6) 처리
  파일이 없으면 "data/kospi200_list.csv 파일이 없습니다. 종목 리스트를 먼저 준비하세요" 출력 후 종료
기능 2 · 종목별로 수집 후 하나의 DataFrame으로 합쳐줘
  최초 수집 시작일을 2024-01-01 로 고정
  기존 데이터가 없는 종목(신규)은 2024-01-01 부터 오늘까지 수집
  기존 데이터가 있는 종목은 "마지막 날짜 + 1일" ~ 오늘까지만 수집 (기존 로직 유지)
기능 3 · 종목코드(srtnCd) 는 반드시 문자열로 저장하고
  앞자리 0이 빠지지 않도록 zfill(6) 처리해줘
  예: 5930 → 005930
  df = get_stock_price(...) 호출 직후 아래 줄에 넣어줘:
  df["srtnCd"] = df["srtnCd"].astype(str).str.zfill(6)

기능 4 · data 폴더가 없으면 폴더를 자동으로 만들고
  data/stock_prices.csv 로 저장해줘
  인코딩은 utf-8-sig 로 해줘 (한글 깨짐 방지)

기능 5 · 종목별 수집 실패 시 (API 오류, 데이터 없음 등)
  중단하지 말고 "⚠️ 현대차: 수집 실패 (사유) - 다음 종목으로 진행" 출력 후 계속 진행
  실패한 종목 목록을 마지막에 별도로 요약 출력:
  "⚠️ 수집 실패 종목 (3개): 000270, 035720, 207940"

기능 6 · 나머지 기존 기능 모두 유지
  종목코드+날짜 기준 drop_duplicates

기능 7 · 수집 진행 상황을 아래처럼 출력해줘
  [1/10] 삼성전자(005930) 수집 중...
  ✅ 삼성전자: 245건 수집
  [2/10] SK하이닉스(000660) 수집 중...
  ...
  ✅ 전체 완료: 총 2,450건 → data/stock_prices.csv 저장

기능 8 · API 호출 사이에 time.sleep(0.5) 을 넣어서
  서버 과부하를 방지해줘

기능 9 · FSS_API_KEY 가 없으면
  ".env 파일에 FSS_API_KEY 를 입력하세요" 출력 후 종료해줘

기능 10 · .env 파일은 ../../.env 경로에서 읽어줘

파일명: collect_data.py
```

---

### STEP 5 · collect_data.py 실행 확인

Claude Code가 파일을 만들면 **기존 터미널로 돌아가서** 실행:

```bash
python collect_data.py
```

출력 예시:
```
[1/10] 삼성전자(005930) 수집 중...
  ✅ 삼성전자: 245건 수집
[2/10] SK하이닉스(000660) 수집 중...
  ✅ SK하이닉스: 243건 수집
...
✅ 전체 완료: 총 2,450건 → data/stock_prices.csv 저장
```

> 예상 소요 시간: 약 2~3분

---

### STEP 6 · 수집된 데이터 확인

```bash
python -c "
import pandas as pd
df = pd.read_csv('data/stock_prices.csv', dtype={'srtnCd': str})
print('📊 데이터 크기:', df.shape)
print()
print('📋 처음 5행:')
print(df[['basDt','srtnCd','itmsNm','clpr','vs','fltRt','trqu']].head())
print()
print('📋 종목코드 확인 (앞 0이 있어야 정상):')
print(df['srtnCd'].unique())
"
```

출력 예시:
```
📊 데이터 크기: (2450, 14)

📋 처음 5행:
      basDt  srtnCd  itmsNm   clpr   vs  fltRt      trqu
0  20240102  005930  삼성전자  78500  500   0.64  12345678

📋 종목코드 확인 (앞 0이 있어야 정상):
['005930' '000660' '005380' '000270' '035420' ...]
```

> ⚠️ 종목코드가 `5930` 처럼 앞 0이 빠져 있으면
> 아래 주의사항 섹션을 참고하세요.

---

### STEP 7 · [Claude Code 실습] explore.py 만들기

Claude Code로 돌아가서 이어서 요청하세요:

```
이번엔 explore.py 파일을 만들어줘.

data/stock_prices.csv 파일을 읽어서
Streamlit으로 데이터를 시각화하는 웹앱이야.

데이터 로딩 시 srtnCd 컬럼은 반드시
dtype={'srtnCd': str} 으로 읽어서 종목코드 앞 0이 유지되게 해줘.

기능 1 · 사이드바에서 종목 선택
  전체 종목 목록을 CSV에서 자동으로 읽어서 표시해줘

기능 2 · 선택한 종목의 종가 추이 라인차트
  x축: 날짜, y축: 종가, Plotly 사용

기능 3 · 선택한 종목의 거래량 막대차트
  전일 대비 상승일은 빨간색, 하락일은 파란색으로 표시해줘

기능 4 · 상단에 통계 카드 4개
  - 수집 종목 수
  - 전체 데이터 건수
  - 수집 기간 (시작일 ~ 종료일)
  - 최고 거래량 종목

기능 5 · 하단에 원본 데이터 테이블
  st.expander로 접을 수 있게 해줘

기능 6 · data 폴더가 없거나 CSV 파일이 없으면
  st.error로 "먼저 collect_data.py 를 실행하세요" 안내 후
  st.stop() 으로 종료해줘

파일명: explore.py
```

---

### STEP 8 · explore.py 실행

Claude Code가 파일을 만들면:

```bash
streamlit run explore.py
# 브라우저가 열리면 성공
# 사이드바에서 종목 선택 → 차트 확인
```

---

### STEP 9 · 추가 실습 — 기능 더 넣어보기

시간이 남으면 Claude Code에 자유롭게 요청해보세요:

**미션 1 · 종목 비교 기능**
```
explore.py 에 여러 종목을 동시에 선택해서
종가 추이를 한 차트에서 비교하는 기능을 추가해줘.
기준일(첫날) 대비 수익률(%)로 정규화해서 비교해줘.
```

**미션 2 · 수익률 히트맵**
```
explore.py 에 월별 수익률 히트맵을 추가해줘.
x축: 월, y축: 종목명
색상: 수익률 높을수록 빨간색, 낮을수록 파란색
```

**미션 3 · CSV 다운로드 버튼**
```
explore.py 에 현재 조회 중인 종목 데이터를
CSV로 다운로드하는 버튼을 추가해줘.
```

---

## 💡 이 실습의 핵심 포인트

```
fss_client.py   → 강사가 미리 제공 (API 연결 방법 학습용)
collect_data.py → 수강생이 Claude Code로 직접 생성
explore.py      → 수강생이 Claude Code로 직접 생성

"코드를 직접 짜지 않아도 AI가 만들어준다" 는 것을
체감하는 것이 이 실습의 목표입니다.
```

---

## ⚠️ 알려진 주의사항

### 종목코드 앞 0 빠짐 문제

수집된 CSV에서 종목코드가 `5930` 처럼 앞 0이 없으면
Claude Code에 아래와 같이 요청해서 수정하세요:

```
collect_data.py 에서
df = get_stock_price(...) 호출 바로 아래 줄에
df["srtnCd"] = df["srtnCd"].astype(str).str.zfill(6)
한 줄을 추가해줘.
```

수정 후 재실행:
```bash
python collect_data.py   # 데이터 재수집

cd ../04_chromadb
python build_db.py       # DB 재구축
```

---

## ❓ 자주 묻는 질문

**Q. collect_data.py 실행 중 오류가 나요**
```
원인 1: FSS_API_KEY 미입력
→ .env 파일 확인

원인 2: API 승인 대기 중
→ data.go.kr 마이페이지 → 개발계정 → 승인 여부 확인
→ 승인까지 최대 1~2시간 소요 (강의 전날 미리 발급 권장)

원인 3: 일일 호출 한도 초과
→ 내일 다시 시도 (일 10,000건 제한)
```

**Q. data 폴더가 안 만들어져요**
```bash
mkdir data
```

**Q. CSV를 열었더니 한글이 깨져요**
```
저장 시 encoding="utf-8-sig" 로 지정했는지 확인
Excel에서 열 때: 데이터 → 텍스트 가져오기 → UTF-8 선택
```

**Q. collect_data.py 를 실행했는데 데이터가 100건밖에 없어요**
```
공공데이터 API는 한 번에 최대 100건만 반환합니다.
1년치(약 245건)를 가져오려면 pageNo 를 늘려가며
여러 번 호출해야 합니다.
Claude Code에 아래와 같이 요청하세요:

"collect_data.py 에서 한 종목당 최대 500건까지
 pageNo 를 반복 호출해서 전체 데이터를 가져오게 수정해줘."
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
