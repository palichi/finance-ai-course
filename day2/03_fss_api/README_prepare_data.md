prepare_ppo_data.py 파일을 만들어줘.

원본 CSV(data/stock_prices.csv)는 한국거래소(금융위원회) 표준 일별매매정보
API 필드를 그대로 사용하며, 컬럼은 정확히 아래 15개야 (이 순서 그대로):

  basDt        기준일자
  srtnCd       단축코드 (종목코드, 6자리, 앞자리 0 있음)
  isinCd       ISIN코드
  itmsNm       종목명
  mrktCtg      시장구분 (코스피/코스닥)
  clpr         종가
  vs           전일대비
  fltRt        등락률
  mkp          시가
  hipr         고가
  lopr         저가
  trqu         거래량
  trPrc        거래금액
  lstgStCnt    상장주식수
  mrktTotAmt   시장총액(시가총액)

이 중 PPO 학습 환경(StockTradingEnv)이 실제로 쓰는 컬럼은
clpr, mkp, hipr, lopr, trqu 5개뿐이고, 나머지 10개는 이번 전처리에서는
사용하지 않지만 원본 데이터를 읽을 때는 15개 컬럼 전부가 존재한다는 것을
전제로 코드를 작성해줘. (즉, read_csv 시 15개 컬럼이 모두 있다고 가정하고,
없는 컬럼을 임의로 만들어내거나 7개만 있다고 가정하지 말 것)

기능 1 · load_raw_data(csv_path) 함수를 만들어줘.
  data/stock_prices.csv 를 읽어줘. 위에 명시한 15개 컬럼이 모두 있는지
  확인하고, 빠진 컬럼이 있으면 "❌ 다음 컬럼이 없습니다: (목록)" 출력 후 종료해줘.
  srtnCd 컬럼은 dtype={'srtnCd': str} 로 읽고
  astype(str).str.zfill(6) 으로 앞자리 0을 보정해줘.
  인코딩은 utf-8-sig 로 읽어줘.
  파일이 없으면 "❌ data/stock_prices.csv 파일이 없습니다" 출력 후 종료해줘.

기능 2 · list_available_symbols(df) 함수를 만들어줘.
  데이터에 들어있는 종목코드(srtnCd)와 종목명(itmsNm) 목록을
  중복 제거해서 DataFrame으로 반환해줘. (종목코드, 종목명, 데이터 건수)

기능 3 · extract_symbol_data(df, symbol_code) 함수를 만들어줘.
  전체 15개 컬럼을 유지한 채로, 해당 종목코드(srtnCd)만 필터링해줘.
  basDt 기준으로 오름차순 정렬하고 reset_index(drop=True) 해줘.
  같은 종목·같은 날짜 중복이 있으면 마지막 값만 남기고 제거해줘.

기능 4 · select_and_rename_for_ppo(df) 함수를 만들어줘.
  기능 3에서 받은 15개 컬럼짜리 DataFrame에서
  PPO 학습에 필요한 5개 컬럼만 골라서(select) 이름을 바꿔줘(rename):
    mkp  → open
    hipr → high
    lopr → low
    clpr → close
    trqu → volume
  basDt 도 함께 남겨줘 (날짜 정보 보존용).
  결과 컬럼은 정확히 [basDt, open, high, low, close, volume] 6개여야 해.
  나머지 9개 컬럼(isinCd, itmsNm, mrktCtg, vs, fltRt, trPrc, lstgStCnt, mrktTotAmt)은
  이 함수에서 제거(drop)해줘.

기능 5 · validate_data(df, symbol_code, window_size=20) 함수를 만들어줘.
  기능 4를 거친 [basDt, open, high, low, close, volume] 데이터를 받아서 점검해줘.
  - 결측치(NaN) 개수 (컬럼별로)
  - 0 이하 또는 음수인 가격(open,high,low,close) 행 개수
  - 전체 데이터 일수가 window_size 보다 적으면
    "⚠️ {symbol_code}: 데이터가 {n}일 밖에 없습니다 (최소 {window_size}일 필요)" 출력
  - 결측치나 이상치가 있는 행은 제거하고, 제거된 행 수를 출력해줘.
  - 문제가 없으면 "✅ {symbol_code}: 데이터 검증 통과 ({n}일)" 출력해줘.
  검증을 통과하지 못해 사용할 수 없는 경우 None을 반환하고,
  통과하면 정제된 DataFrame을 반환해줘.

기능 6 · prepare_one_symbol(df, symbol_code, output_dir="data/ppo_ready") 함수를 만들어줘.
  기능 3 → 4 → 5 를 이 순서대로 호출해서 한 종목을 처리하고
  output_dir 폴더가 없으면 자동으로 만들어줘.
  결과를 {output_dir}/{symbol_code}.csv 로 저장해줘 (utf-8-sig 인코딩).
  저장되는 컬럼은 [basDt, open, high, low, close, volume] 6개여야 해.
  검증에 실패하면 저장하지 않고 None을 반환해줘.

기능 7 · prepare_all_symbols(csv_path="data/stock_prices.csv", output_dir="data/ppo_ready") 함수를 만들어줘.
  기능 1로 원본을 읽고, 기능 2로 종목 목록을 뽑은 뒤
  전체 종목에 대해 prepare_one_symbol() 을 반복 호출해줘.
  진행 상황을 아래처럼 출력해줘:
    [1/10] 005930 삼성전자 처리 중...
    ✅ 005930: 데이터 검증 통과 (245일) → data/ppo_ready/005930.csv 저장
    [2/10] 000660 SK하이닉스 처리 중...
    ...
  처리 실패한 종목은 중단하지 말고 다음 종목으로 계속 진행해줘.
  마지막에 성공/실패 종목 수를 요약 출력해줘:
    ✅ 전체 완료: 성공 8개 / 실패 2개
    ⚠️ 실패 종목: 000270(데이터 부족), 035720(결측치 과다)

기능 8 · 파일 맨 아래에 if __name__ == "__main__": 블록을 추가해줘.
  prepare_all_symbols() 를 실행해서 전체 종목을 한 번에 처리하게 해줘.

기능 9 · 파일 최상단 주석에 원본 15개 컬럼 전체 목록과
  그 중 실제로 사용하는 5개(mkp,hipr,lopr,clpr,trqu) 및
  사용하지 않는 9개를 명확히 구분해서 적어줘.
  또한 이 스크립트로 만들어진 data/ppo_ready/{종목코드}.csv 파일은
  이후 ppo_trading_model.py 에서 아래처럼 바로 읽어서 쓸 수 있어야 한다고 적어줘:
    df = pd.read_csv("data/ppo_ready/005930.csv")
    env = StockTradingEnv(df)

파일명: prepare_ppo_data.py
