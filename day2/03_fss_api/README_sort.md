sort_stock_data.py 파일을 만들어줘.
data/stock_prices.csv 파일의 날짜·종목 순서를 정렬해서 다시 저장하는 스크립트야.

기능 1 · data/stock_prices.csv 파일이 있는지 먼저 확인해줘.
  파일이 없으면 "❌ data/stock_prices.csv 파일이 없습니다" 출력 후 종료해줘.

기능 2 · 기존 data/stock_price.csv 파일을
  data/stock_prices_bak.csv 로 이름을 바꿔서(백업) 저장해줘.
  (shutil.copy 또는 os.rename 사용, 원본을 안전하게 보존)
  만약 data/stock_prices_bak.csv 가 이미 존재하면
  덮어쓰기 전에 "⚠️ 기존 백업 파일이 있습니다. 덮어씁니다" 출력해줘.

기능 3 · data/stock_prices_bak.csv 파일을 읽어줘.
  종목코드 컬럼(srtnCd)은 앞자리 0이 사라지지 않도록
  dtype={'srtnCd': str} 로 읽고, 혹시 0이 빠진 값이 있으면
  astype(str).str.zfill(6) 으로 보정해줘.
  인코딩은 utf-8-sig 로 읽어줘.

기능 4 · 읽은 데이터를 종목코드(srtnCd) 기준으로 먼저 정렬하고,
  같은 종목 안에서는 날짜(basDt) 기준으로 오름차순 정렬해줘.
  정렬 후 인덱스를 reset_index(drop=True) 로 재정렬해줘.

기능 5 · 정렬 과정에서 다음을 검증하고 결과를 출력해줘.
  - 종목별로 날짜 중복이 있는지 확인 (srtnCd + basDt 기준 duplicated)
  - 중복이 있으면 "⚠️ 중복 데이터 N건 발견 - 마지막 값만 유지" 출력하고
    drop_duplicates(subset=["srtnCd","basDt"], keep="last") 로 제거해줘.
  - 종목별로 날짜가 실제로 오름차순인지 최종 검증해서
    "✅ 정렬 검증 완료" 또는 문제가 있으면 어떤 종목인지 출력해줘.

기능 6 · 정렬이 끝난 데이터를 data/stock_prices.csv 로 새로 저장해줘.
  인코딩은 utf-8-sig 로 저장해줘 (한글 깨짐 방지).

기능 7 · 마지막에 작업 요약을 출력해줘.
  - 백업 파일 경로
  - 원본 데이터 건수 vs 정렬 후 데이터 건수 (중복 제거로 줄었다면 그 차이도)
  - 정렬 후 종목 수
  - 정렬 후 전체 날짜 범위 (가장 오래된 날짜 ~ 가장 최근 날짜)

기능 8 · 전체 과정에서 오류가 나면 try/except 로 감싸서
  "❌ 오류 발생: (오류내용)" 을 출력하고
  원본 백업 파일은 그대로 보존되도록 해줘 (절대 삭제하지 않음).

파일명: sort_stock_data.py