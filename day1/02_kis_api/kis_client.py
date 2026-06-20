"""
KIS OpenAPI 클라이언트 — 모의투자 전용
실행: python kis_client.py
"""

import requests
import os
from dotenv import load_dotenv

load_dotenv("../../.env")

BASE_URL   = "https://openapivts.koreainvestment.com:29443"
APP_KEY    = os.getenv("KIS_APP_KEY", "")
APP_SECRET = os.getenv("KIS_APP_SECRET", "")
ACCOUNT_NO = os.getenv("KIS_ACCOUNT_NO", "")


# ── 1. Access Token 발급 ──────────────────────────
def get_token() -> str:
    """Access Token 발급 (24시간 유효)"""
    url  = f"{BASE_URL}/oauth2/tokenP"
    body = {
        "grant_type": "client_credentials",
        "appkey":     APP_KEY,
        "appsecret":  APP_SECRET,
    }
    resp = requests.post(url, json=body, timeout=10)
    resp.raise_for_status()
    token = resp.json()["access_token"]
    print(f"✅ Token 발급 성공: {token[:20]}...")
    return token


def make_headers(token: str, tr_id: str) -> dict:
    """공통 헤더 생성"""
    return {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {token}",
        "appkey":    APP_KEY,
        "appsecret": APP_SECRET,
        "tr_id":     tr_id,
        "custtype":  "P",
    }


# ── 2. 현재가 조회 ────────────────────────────────
def get_price(token: str, ticker: str) -> dict:
    """주식 현재가 조회 (TR: FHKST01010100)"""
    url    = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",   # J: 주식
        "FID_INPUT_ISCD": ticker,          # 종목코드
    }
    resp = requests.get(
        url,
        headers=make_headers(token, "FHKST01010100"),
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()
    if data["rt_cd"] != "0":
        raise ValueError(f"API 오류: {data['msg1']}")
    return data["output"]


# ── 3. 잔고 조회 ──────────────────────────────────
def get_balance(token: str) -> dict:
    """계좌 잔고 조회 (TR: VTTC8434R — 모의투자 전용)"""
    url    = f"{BASE_URL}/uapi/domestic-stock/v1/trading/inquire-balance"
    params = {
        "CANO":              ACCOUNT_NO,
        "ACNT_PRDT_CD":      "01",
        "AFHR_FLPR_YN":      "N",
        "OFL_YN":            "",
        "INQR_DVSN":         "02",
        "UNPR_DVSN":         "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN":         "01",
        "CTX_AREA_FK100":    "",
        "CTX_AREA_NK100":    "",
    }
    resp = requests.get(
        url,
        headers=make_headers(token, "VTTC8434R"),
        params=params,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


# ── 테스트 실행 ───────────────────────────────────
if __name__ == "__main__":
    if not APP_KEY:
        print("❌ .env 파일에 KIS_APP_KEY를 입력하세요")
        exit(1)

    # Token 발급
    token = get_token()

    # 삼성전자 현재가
    price_data = get_price(token, "005930")
    cur_price  = int(price_data["stck_prpr"])
    change     = int(price_data["prdy_vrss"])
    chg_pct    = float(price_data["prdy_ctrt"])
    print(f"\n📈 삼성전자 현재가: {cur_price:,}원")
    print(f"   전일대비: {change:+,}원 ({chg_pct:+.2f}%)")

    # 계좌 잔고
    bal = get_balance(token)
    if bal.get("rt_cd") == "0":
        summary = bal["output2"][0] if bal.get("output2") else {}
        print(f"\n💰 계좌 잔고")
        print(f"   예수금:    {int(summary.get('dnca_tot_amt', 0)):,}원")
        print(f"   평가금액:  {int(summary.get('tot_evlu_amt', 0)):,}원")
        print(f"   평가손익:  {int(summary.get('evlu_pfls_smtl_amt', 0)):+,}원")
    else:
        print(f"잔고 조회 실패: {bal.get('msg1','')}")
