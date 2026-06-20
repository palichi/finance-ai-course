# 📁 Day 2 · 05-2 · RAG 패턴 검색 + 강화학습(PPO) 결합

## 이 실습에서 배우는 것
- 강화학습(PPO)으로 "거래 행동 자체"를 최적화하는 방법
- 이전 실습(`05_pattern_db/chroma_pattern_store.py`)에서 만든
  ChromaDB 패턴 검색 결과를 PPO의 State에 결합하는 방법
- 학습 없이도 패턴만으로 바로 "물어보는" CLI 도구를 만드는 방법

---

## 📂 이 폴더의 파일 구성

```
day2/05_rag/
├── ppo_trading_model.py     ← 실습에서 Claude Code로 직접 만들기
├── ask_pattern_tool.py      ← 실습에서 Claude Code로 직접 만들기
├── rag_ppo_trading.py       ← 실습에서 Claude Code로 직접 만들기
└── models/                  ← 학습된 PPO 모델 저장 폴더 (자동 생성)
```

> 이 3개 파일을 전부 **이 실습에서 Claude Code로 직접 만듭니다.**

> ⚠️ 이 실습은 `day2/04_chroma/chroma_pattern_store.py` 가 만든
> ChromaDB(`day2/04_chroma/data/chroma_pattern_db`, 컬렉션 `price_patterns`)를
> **그대로 가져와서 사용**합니다. 05번 실습을 먼저 완료해야 합니다.

| 폴더 | 만드는 것 | 비고 |
|---|---|---|
| `04_chromadb/` | `chroma_db_text` (자연어 RAG) | 이번 실습과 무관 |
| `04_chromadb/` | `data/chroma_pattern_db` (패턴 RAG) | **이번 실습의 전제조건** ✅ |
| `05_rag/` (이번 실습) | PPO 모델 + RAG 결합 | 04번 결과를 가져와 사용 |

---

## 🖥 실습 순서

---

### STEP 1 · 폴더 이동 + 패키지 설치

```bash
cd day2/05_rag/
```

```bash
pip install gymnasium stable-baselines3 chromadb pandas numpy --break-system-packages
```

---

### STEP 2 · 04번 실습 결과물 확인

이번 실습은 `chroma_pattern_store.py` 를 다시 만들지 않고
**이전 실습에서 만든 파일과 DB를 그대로 가져와 씁니다.**

```bash
# 04_chroma_db 폴더의 chroma_pattern_store.py 를 복사해오기
cp ../04_chroma_db/chroma_pattern_store.py .
```

```bash
# ChromaDB에 패턴이 저장되어 있는지 확인
python -c "
from chroma_pattern_store import PricePatternStore
store = PricePatternStore(db_path='../04_chromadb/data/chroma_pattern_db')
print('📦 저장된 패턴 수:', store.count())
"
```

```
출력 예시:
📦 저장된 패턴 수: 475
```

> ⚠️ 0이 나오면 `04_chromadb` 실습을 먼저 끝내고 오세요.

---

### STEP 3 · Claude Code 실행

```bash
claude
```

---

### STEP 4 · [Claude Code 실습] ppo_trading_model.py 만들기

Claude Code가 실행되면 아래 프롬프트를 **그대로 복사해서 붙여넣기** 하세요:

```
ppo_trading_model.py 파일을 만들어줘.
순수 가격 예측이 아니라 "거래 행동 자체"를 최적화하는
강화학습(PPO) 거래 전략 학습 모델이야.

기능 1 · StockTradingEnv 클래스를 만들어줘 (gymnasium.Env 상속).
  생성자 인자: df, window_size=20, initial_balance=10_000_000, transaction_fee=0.00015
  df 는 open, high, low, close, volume 컬럼을 가진 일별 시세 데이터야.

기능 2 · action_space 는 gymnasium.spaces.Discrete(3) 으로 만들어줘.
  0 = 매도(전량), 1 = 보유, 2 = 매수(전량)

기능 3 · observation_space 는 gymnasium.spaces.Box 로 만들어줘.
  최근 window_size일의 [open, high, low, close, volume] 5개 컬럼을
  정규화한 값 + [포지션비율, 누적수익률] 2개를 이어붙인 벡터로 만들어줘.
  정규화 방법: 가격 4개 컬럼은 윈도우 첫날 종가 기준 상대비율로,
              거래량은 윈도우 내 평균 기준 상대비율로 정규화해줘.

기능 4 · reset() 메서드를 만들어줘.
  current_step 을 window_size 로 초기화하고
  balance(현금), shares_held(보유주식수), net_worth(총자산)를
  초기화해줘. 첫 관측값을 반환해줘.

기능 5 · step(action) 메서드를 만들어줘.
  action==2(매수)면 현재 현금으로 살 수 있는 최대 주식수를 계산해서
    수수료(transaction_fee) 포함 비용으로 전액 매수해줘.
  action==0(매도)면 보유 주식을 수수료 제외하고 전량 매도해줘.
  action==1(보유)이면 아무것도 하지 않아.
  매 스텝마다 current_step 을 1 증가시키고
  새로운 종가로 net_worth(현금 + 보유주식*현재가)를 다시 계산해줘.

기능 6 · reward 는 이번 스텝 net_worth 변화율로 계산해줘.
  reward = (현재 net_worth - 이전 net_worth) / 이전 net_worth
  계산이 끝나면 이전 net_worth 를 현재 값으로 갱신해줘.

기능 7 · net_worth 가 initial_balance 의 30% 이하로 떨어지면
  reward 에 -1.0 페널티를 추가하고 done=True 로 에피소드를 종료해줘.

기능 8 · 데이터 끝에 도달하면(current_step >= len(df)-1) done=True 로 해줘.
  step() 은 (관측값, reward, done, truncated, info) 5개를 반환해줘.
  info 에는 net_worth, balance, shares_held, price 를 담아줘.

기능 9 · render() 메서드를 만들어서
  현재 스텝, 가격, 현금, 보유주식, 총자산, 누적수익을 한 줄로 출력해줘.

기능 10 · generate_sample_price_data(n_days=1000, seed=42) 함수를 만들어줘.
  실습용 가상 일별 시세 데이터(랜덤워크 기반)를 생성해서
  open, high, low, close, volume 컬럼의 DataFrame으로 반환해줘.
  실전에서는 이 함수를 실제 시세 데이터로 교체할 거라는 주석을 달아줘.

기능 11 · train_ppo_trading_model(df, total_timesteps=50_000, model_save_path)
  함수를 만들어줘. stable_baselines3 의 PPO(MlpPolicy) 를 사용하고
  데이터를 80% 학습 / 20% 검증으로 나눠서
  DummyVecEnv + Monitor 로 감싼 학습 환경을 만들어줘.
  model.save() 호출 전에 os.makedirs(os.path.dirname(model_save_path), exist_ok=True)
  를 호출해서 저장 폴더가 없을 때 자동 생성되게 해줘.
  학습 후 모델을 저장하고 (model, train_df, test_df) 를 반환해줘.

기능 12 · backtest(model, test_df, window_size=20) 함수를 만들어줘.
  검증 데이터로 환경을 새로 만들고 모델로 끝까지 행동을 예측·실행해서
  최종 수익률을 계산해줘.
  같은 기간 동안 "처음에 사서 끝까지 보유만 했을 때(Buy & Hold)"의
  수익률도 같이 계산해서 두 수익률을 비교 출력해줘.

기능 13 · 파일 맨 아래에 if __name__ == "__main__": 블록을 추가해줘.
  1) generate_sample_price_data() 로 데이터 생성
  2) train_ppo_trading_model() 로 학습 (model_save_path="./models/ppo_trading_model")
  3) backtest() 로 결과 확인
  순서로 실행되게 해줘.

파일명: ppo_trading_model.py
```

---

### STEP 5 · ppo_trading_model.py 실행 확인

Claude Code가 파일을 만들면 **기존 터미널로 돌아가서** 실행:

```bash
python ppo_trading_model.py
```

출력 예시:
```
📈 가격 데이터 1000일 생성 완료
🚀 PPO 거래 전략 학습 시작
...
📊 백테스트 결과 (검증 데이터 기준)
PPO 전략 수익률  :   -0.91 %
단순 보유 수익률 :   -1.73 %  (Buy & Hold)
```

> 예상 소요 시간: 약 30초~2분 (`total_timesteps` 값에 따라 다름)
> VS Code에서 `StockTradingEnv` 클래스를 열어
> State / Action / Reward 구조를 확인하세요. 강사가 설명합니다.

---

### STEP 6 · [Claude Code 실습] ask_pattern_tool.py 만들기

Claude Code로 돌아가서 이어서 요청하세요:

```
ask_pattern_tool.py 파일을 만들어줘.
학습 없이 chroma_pattern_store.py 의 ChromaDB에 저장된 패턴만으로
"지금 이 패턴이 과거에 몇 번 있었고 결과가 어땠는지" 바로 물어보는 도구야.

chroma_pattern_store.py 의 PricePatternStore 를 사용하고,
db_path 는 "../05_pattern_db/data/chroma_pattern_db" 를 기본값으로 해줘.

기능 1 · ask_pattern(store, df, as_of_index, window_size, top_k) 함수를 만들어줘.
  df 의 as_of_index 시점을 기준으로 최근 window_size일 패턴을 가져와서
  store.search_similar_patterns() 로 검색하고 결과를 보기 좋게 출력해줘.

기능 2 · 출력 내용
  기준일, 기준가
  찾은 패턴 수, 평균 미래수익률, 수익률 편차, 상승확률
  상위 5개 유사 사례 (날짜, 유사도, 이후 수익률)

기능 3 · 상승확률이 0.65 이상이고 평균 미래수익률이 1.0% 이상이면
  "💡 참고 신호: 과거 유사패턴 다수가 상승 → 긍정적 신호 (참고용)" 출력
  상승확률이 0.35 이하이고 평균 미래수익률이 -1.0% 이하면
  "💡 참고 신호: 과거 유사패턴 다수가 하락 → 주의 신호 (참고용)" 출력
  그 외에는 "💡 참고 신호: 뚜렷한 방향성 없음 → 신중한 판단 필요" 출력

기능 4 · interactive_cli(store, df, window_size) 함수를 만들어줘.
  터미널에서 날짜(YYYYMMDD)를 입력받아 ask_pattern() 을 호출하는
  반복 입력 도구야. 'q' 입력 시 종료해줘.

기능 5 · 날짜를 입력하면 df 에서 해당 날짜의 행 인덱스를 찾아서
  ask_pattern() 에 넘겨줘. 없는 날짜를 입력하면
  "❌ 해당 날짜의 데이터가 없습니다" 출력 후 다시 입력받아줘.

기능 6 · 파일 맨 아래에 실행 예시를 추가해줘.
  가상 데이터로 ChromaDB를 만들고, 임의의 시점 하나를 골라
  ask_pattern() 을 바로 호출하는 비대화형 데모로 만들어줘.
  대화형으로 직접 써보고 싶으면 interactive_cli() 호출 줄의
  주석을 해제하면 된다는 안내 주석도 달아줘.

파일명: ask_pattern_tool.py
```

---

### STEP 7 · ask_pattern_tool.py 실행

Claude Code가 파일을 만들면:

```bash
python ask_pattern_tool.py
```

출력 예시:
```
============================================================
📅 기준일: 20240204   기준가: 49,195원
🔍 비슷한 과거 패턴 검색 (top 20)
============================================================
찾은 패턴 수      : 20건
평균 미래수익률   : -1.54%
수익률 편차(σ)    : 4.09%
상승 확률         : 40.0%

상위 5개 유사 사례:
  📉 20240204 | 유사도 1.000 | 이후 수익률 -0.56%
  📉 20231122 | 유사도 0.593 | 이후 수익률 -3.00%
  ...

💡 참고 신호: 뚜렷한 방향성 없음 → 신중한 판단 필요
============================================================
```

---

### STEP 8 · [Claude Code 실습] rag_ppo_trading.py 만들기

Claude Code로 돌아가서 이어서 요청하세요:

```
rag_ppo_trading.py 파일을 만들어줘.
ppo_trading_model.py 의 PPO 거래 환경에
chroma_pattern_store.py 의 유사 패턴 검색 결과를
State(관측값)에 추가로 결합하는 파일이야.

기능 1 · RAGEnhancedTradingEnv 클래스를 만들어줘 (gymnasium.Env 상속).
  생성자 인자: df, pattern_store, window_size=20, top_k=20,
             initial_balance=10_000_000, transaction_fee=0.00015, symbol

기능 2 · observation_space 는 다음을 이어붙인 벡터로 만들어줘:
  - 최근 window_size일의 [clpr, mkp, hipr, lopr, trqu, fltRt] 정규화 패턴
  - 포지션 비율, 누적 수익률 (2개)
  - ChromaDB 검색결과: 평균 미래수익률, 상승확률, 수익률표준편차 (3개, 모두 100으로 나눠서 정규화)

기능 3 · _get_rag_info() 메서드를 만들어서
  현재 step 의 패턴으로 pattern_store.search_similar_patterns() 를 호출하고
  결과를 위 3개 값으로 변환해줘.
  같은 step 에서 중복 검색하지 않도록 결과를 캐시(dict)해줘.

기능 4 · action_space 는 Discrete(3) 으로 만들어줘 (0=매도, 1=보유, 2=매수).
  매수 시 현금 전액으로 매수, 매도 시 보유 주식 전량 매도로 해줘.
  거래 시 transaction_fee 를 적용해줘.

기능 5 · reward 는 그 행동 이후 실제 총자산(net_worth) 변화율로 계산해줘.
  총자산이 초기자본의 30% 이하로 떨어지면 큰 페널티(-1.0)를 주고
  에피소드를 종료(done=True)해줘.

기능 6 · train_rag_ppo(df, pattern_store, symbol, total_timesteps, model_save_path)
  함수를 만들어줘. stable_baselines3 의 PPO 를 사용하고
  데이터를 80% 학습 / 20% 검증으로 나눠서 학습용 환경을 만들어줘.
  model.save() 호출 전에 저장 폴더가 없으면 자동 생성해줘.
  학습 후 모델을 저장해줘.

기능 7 · backtest_rag_ppo(model, test_df, pattern_store, symbol, window_size)
  함수를 만들어줘. 검증 데이터로 모델을 끝까지 실행하고
  PPO 전략 수익률과 단순 보유(Buy & Hold) 수익률을 비교해서 출력해줘.

기능 8 · 파일 맨 아래에 실행 예시를 추가해줘.
  pattern_store 는 db_path="../05_pattern_db/data/chroma_pattern_db" 로 불러와줘.
  1) 가상 데이터 생성 → 컬럼명 맞추기
  2) train_rag_ppo() 로 학습 (model_save_path="./models/rag_ppo_model")
  3) backtest_rag_ppo() 로 결과 확인

파일명: rag_ppo_trading.py
```

---

### STEP 9 · rag_ppo_trading.py 실행

Claude Code가 파일을 만들면:

```bash
python rag_ppo_trading.py
```

출력 예시:
```
🚀 RAG + PPO 결합 거래 전략 학습 시작
   학습 데이터: 480일 / 검증 데이터: 120일
   ChromaDB 저장 패턴 수: 455
...
📊 RAG+PPO 백테스트 결과
RAG+PPO 수익률   :   -23.19 %
단순 보유 수익률 :   -19.54 %  (Buy & Hold)
총 거래 횟수     :       17 회
```

> 예상 소요 시간: 약 1~5분 (total_timesteps 값에 따라 다름)
> 가상 데이터(랜덤워크)로는 의미 있는 수익이 나오지 않는 것이 정상입니다.
> 다음 단계에서 실제 시세 데이터로 교체합니다.

---

### STEP 10 · 추가 실습 — 기능 더 넣어보기

시간이 남으면 Claude Code에 자유롭게 요청해보세요:

**미션 1 · 실데이터로 교체**
```
ppo_trading_model.py 와 rag_ppo_trading.py 에서
generate_sample_price_data() 대신
data/ppo_ready/{종목코드}.csv 파일을 pandas로 읽어서 사용하도록 수정해줘.
```

**미션 2 · 여러 종목 각각 학습**
```
data/ppo_ready 폴더의 모든 종목 CSV에 대해
각각 PPO 모델을 학습하고 backtest 결과를 비교하는
train_all_symbols() 함수를 rag_ppo_trading.py 에 추가해줘.
종목마다 모델을 ./models/ppo_{종목코드} 로 따로 저장해줘.
```

**미션 3 · 거래 빈도 패널티 추가**
```
rag_ppo_trading.py 의 RAGEnhancedTradingEnv 에서
매수/매도 행동을 할 때마다 reward 에 작은 패널티(-0.001)를 추가해서
너무 자주 거래하지 않도록 수정해줘.
```

---

## 💡 이 실습의 핵심 포인트

```
ppo_trading_model.py     → 수강생이 Claude Code로 직접 생성
ask_pattern_tool.py      → 수강생이 Claude Code로 직접 생성
rag_ppo_trading.py       → 수강생이 Claude Code로 직접 생성
chroma_pattern_store.py  → 05번 실습 결과물을 그대로 재사용

"이미 만든 컴포넌트(ChromaDB 패턴 검색)를
 새로운 시스템(강화학습)에 재사용하며 통합(Integration)하는 것"
이 이 실습의 핵심 포인트입니다.
```

이 실습에서 만든 PPO는 **강화학습**이며, 페리도트님이 이후 다룰
**Fine-tuning(LLM 추가학습)** 과는 완전히 다른 개념입니다.

| 구분 | PPO (이번 실습) | Fine-tuning (LLM 학습) |
|---|---|---|
| 학습 대상 | 거래 행동 정책 | 언어모델 가중치 |
| 입력 | 가격 패턴(숫자) | 텍스트 |
| 출력 | 매수/매도/보유(행동) | 텍스트 |
| 관계 | DB·RAG와 데이터로 직접 연결 | 별도 트랙 (나중에 결과 해석용으로 연결 가능) |

---

## ⚠️ 알려진 주의사항

### ChromaDB 패턴 수가 0건으로 나오는 문제

`04_chromadb` 실습을 먼저 끝내지 않았거나,
`db_path` 경로(`../04_chromadb/data/chroma_pattern_db`)가
실제 위치와 다르면 발생합니다. 경로를 다시 확인하세요.

### 모델 저장 시 오류가 나는 경우

```
원인: 저장 경로 폴더(./models)가 없는 경우
→ STEP 4, STEP 8 프롬프트에 이미
   "os.makedirs(..., exist_ok=True)" 를 포함했으니,
   직접 추가 요청할 필요는 없습니다.
```

---

## ❓ 자주 묻는 질문

**Q. ChromaDB 검색 결과의 상승확률이 항상 50% 근처로만 나와요**
```
원인 1: 데이터가 가상(랜덤워크) 데이터라 실제 패턴이 거의 없음
→ 실데이터로 교체 후 다시 확인

원인 2: 종목 하나만 저장해서 유사 사례 풀이 너무 작음
→ 05_pattern_db 실습의 미션 2(여러 종목 동시 저장)를 먼저 적용
```

**Q. stable_baselines3 설치 시 오류가 나요**
```bash
pip install gymnasium stable-baselines3 --break-system-packages
```

**Q. 학습이 너무 오래 걸려요**
```
total_timesteps 값을 줄여서 먼저 구조가 작동하는지만 확인하세요.
실습용: 2,000 ~ 5,000
실전용: 100,000 이상 권장
```

**Q. PPO 수익률이 Buy & Hold 보다 항상 낮게 나와요**
```
정상적인 현상입니다. 학습 스텝이 적거나 데이터가 짧으면
에이전트가 의미 있는 전략을 학습하기 전입니다.
total_timesteps 를 늘리고, 실데이터로 교체한 뒤 다시 확인하세요.
```

**Q. ask_pattern_tool.py 의 interactive_cli() 가 실행이 안 돼요**
```
파일 맨 아래 if __name__ == "__main__": 블록에서
interactive_cli(store, df) 줄의 주석(#)을 해제했는지 확인하세요.
```

**Q. PPO·RAG가 DB생성·Fine-tuning과 무슨 관계가 있나요?**
```
DB 생성은 PPO의 전제조건(데이터 없이는 학습 불가)이고,
RAG는 PPO의 State를 보강하는 입력입니다.
Fine-tuning(LLM 학습)과는 학습 대상·입출력이 완전히 다른
별도 트랙이며, 추후 "PPO 결과를 LLM이 해석해 설명을 생성"하는
방식으로만 서로 연결할 수 있습니다.
```