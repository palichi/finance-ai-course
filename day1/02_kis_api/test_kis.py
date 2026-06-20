"""
한국투자증권 OpenAPI 핵심 모듈
KIS (Korea Investment Securities) OpenAPI Wrapper

모의투자 전용 - Base URL: https://openapivts.koreainvestment.com:29443
실전투자 전용 - Base URL: https://openapi.koreainvestment.com:9443
"""

import requests
import json
import time
import datetime
import streamlit as st
from typing import Optional, Dict, Any

# ── 상수 ──────────────────────────────────────────────
MOCK_BASE_URL  = "https://openapivts.koreainvestment.com:29443"   # 모의투자
REAL_BASE_URL  = "https://openapi.koreainvestment.com:9443"       # 실전투자 (미사용)

# ── 토큰 캐시 키 ───────────────────────────────────────
_TOKEN_CACHE = {}


class KISApi:
    """한국투자증권 OpenAPI 래퍼 (모의투자)"""

    def __init__(self, app_key: str, app_secret: str, account_no: str, account_type: str = "01"):
        self.app_key     = app_key
        self.app_secret  = app_secret
        self.account_no  = account_no        # 계좌번호 8자리
        self.account_type = account_type     # 01: 종합계좌
        self.base_url    = MOCK_BASE_URL
        self._token: Optional[str] = None
        self._token_expired: Optional[datetime.datetime] = None

    # ── 인증 ──────────────────────────────────────────
    def get_token(self) -> str:
        """Access Token 발급 / 재사용"""
        now = datetime.datetime.now()
        if self._token and self._token_expired and now < self._token_expired:
            return self._token

        url = f"{self.base_url}/oauth2/tokenP"
        body = {
            "grant_type": "client_credentials",
            "appkey": self.app_key,
            "appsecret": self.app_secret,
        }
        resp = requests.post(url, json=body, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        self._token = data["access_token"]
        # 만료 1분 전에 갱신 (기본 24시간)
        self._token_expired = now + datetime.timedelta(seconds=int(data.get("expires_in", 86400)) - 60)
        return self._token

    def _headers(self, tr_id: str, extra: Dict = None) -> Dict:
        """공통 헤더 생성"""
        h = {
            "content-type":    "application/json; charset=utf-8",
            "authorization":   f"Bearer {self.get_token()}",
            "appkey":          self.app_key,
            "appsecret":       self.app_secret,
            "tr_id":           tr_id,
            "custtype":        "P",  # 개인
        }
        if extra:
            h.update(extra)
        return h

    def _get(self, path: str, tr_id: str, params: Dict) -> Dict:
        """GET 요청"""
        url = self.base_url + path
        resp = requests.get(url, headers=self._headers(tr_id), params=params, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, tr_id: str, body: Dict) -> Dict:
        """POST 요청"""
        url = self.base_url + path
        resp = requests.post(url, headers=self._headers(tr_id), json=body, timeout=10)
        resp.raise_for_status()
        return resp.json()

    # ── 시세 조회 ─────────────────────────────────────
    def get_price(self, ticker: str) -> Dict:
        """
        주식 현재가 조회
        TR: FHKST01010100 (모의: VTTC8434R)
        Returns: {stck_prpr, prdy_vrss, prdy_ctrt, stck_hgpr, stck_lwpr, acml_vol, ...}
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": ticker,
        }
        return self._get(
            "/uapi/domestic-stock/v1/quotations/inquire-price",
            "FHKST01010100",
            params,
        )

    def get_orderbook(self, ticker: str) -> Dict:
        """호가 조회 TR: FHKST01010200"""
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD": ticker,
        }
        return self._get(
            "/uapi/domestic-stock/v1/quotations/inquire-asking-price-exp-ccn",
            "FHKST01010200",
            params,
        )

    def get_daily_chart(self, ticker: str, start: str, end: str, period: str = "D") -> Dict:
        """
        일봉/주봉/월봉 조회
        TR: FHKST03010100
        period: D(일) W(주) M(월)
        start/end: YYYYMMDD
        """
        params = {
            "FID_COND_MRKT_DIV_CODE": "J",
            "FID_INPUT_ISCD":          ticker,
            "FID_INPUT_DATE_1":        start,
            "FID_INPUT_DATE_2":        end,
            "FID_PERIOD_DIV_CODE":     period,
            "FID_ORG_ADJ_PRC":         "0",  # 수정주가
        }
        return self._get(
            "/uapi/domestic-stock/v1/quotations/inquire-daily-itemchartprice",
            "FHKST03010100",
            params,
        )

    def get_minute_chart(self, ticker: str, time_unit: str = "1") -> Dict:
        """분봉 조회 TR: FHKST03010200"""
        params = {
            "FID_ETC_CLS_CODE":        "",
            "FID_COND_MRKT_DIV_CODE":  "J",
            "FID_INPUT_ISCD":          ticker,
            "FID_INPUT_HOUR_1":        time_unit,
            "FID_PW_DATA_INCU_YN":     "N",
        }
        return self._get(
            "/uapi/domestic-stock/v1/quotations/inquire-time-itemchartprice",
            "FHKST03010200",
            params,
        )

    def search_stock(self, query: str) -> Dict:
        """종목 검색 TR: CTPF1002R"""
        params = {
            "PRDT_TYPE_CD": "300",
            "PDNO": query,
        }
        return self._get(
            "/uapi/domestic-stock/v1/quotations/search-stock-info",
            "CTPF1002R",
            params,
        )

    # ── 주문 ──────────────────────────────────────────
    def buy_order(self, ticker: str, qty: int, price: int = 0, order_type: str = "01") -> Dict:
        """
        매수 주문
        TR: VTTC0802U (모의투자 매수)
        order_type: 00=지정가, 01=시장가
        price=0 이면 시장가 자동 처리
        """
        body = {
            "CANO":          self.account_no,
            "ACNT_PRDT_CD":  self.account_type,
            "PDNO":          ticker,
            "ORD_DVSN":      order_type,
            "ORD_QTY":       str(qty),
            "ORD_UNPR":      "0" if order_type == "01" else str(price),
        }
        return self._post(
            "/uapi/domestic-stock/v1/trading/order-cash",
            "VTTC0802U",   # 모의투자 매수
            body,
        )

    def sell_order(self, ticker: str, qty: int, price: int = 0, order_type: str = "01") -> Dict:
        """
        매도 주문
        TR: VTTC0801U (모의투자 매도)
        """
        body = {
            "CANO":          self.account_no,
            "ACNT_PRDT_CD":  self.account_type,
            "PDNO":          ticker,
            "ORD_DVSN":      order_type,
            "ORD_QTY":       str(qty),
            "ORD_UNPR":      "0" if order_type == "01" else str(price),
        }
        return self._post(
            "/uapi/domestic-stock/v1/trading/order-cash",
            "VTTC0801U",   # 모의투자 매도
            body,
        )

    def cancel_order(self, org_odno: str, ticker: str, qty: int, price: int) -> Dict:
        """주문 취소 TR: VTTC0803U"""
        body = {
            "CANO":          self.account_no,
            "ACNT_PRDT_CD":  self.account_type,
            "KRX_FWDG_ORD_ORGNO": "",
            "ORGN_ODNO":     org_odno,
            "ORD_DVSN":      "00",
            "RVSE_CNCL_DVSN_CD": "02",  # 취소
            "ORD_QTY":       str(qty),
            "ORD_UNPR":      str(price),
            "QTY_ALL_ORD_YN": "Y",
        }
        return self._post(
            "/uapi/domestic-stock/v1/trading/order-rvsecncl",
            "VTTC0803U",
            body,
        )

    # ── 조회 ──────────────────────────────────────────
    def get_balance(self) -> Dict:
        """
        잔고 조회 (보유 종목 + 예수금)
        TR: VTTC8434R (모의투자)
        """
        params = {
            "CANO":              self.account_no,
            "ACNT_PRDT_CD":      self.account_type,
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
        return self._get(
            "/uapi/domestic-stock/v1/trading/inquire-balance",
            "VTTC8434R",
            params,
        )

    def get_orders(self, start: str = "", end: str = "") -> Dict:
        """
        당일 주문 내역 조회 TR: VTTC8001R
        start/end: HHMMSS
        """
        if not start:
            start = "090000"
        if not end:
            end = datetime.datetime.now().strftime("%H%M%S")
        params = {
            "CANO":          self.account_no,
            "ACNT_PRDT_CD":  self.account_type,
            "INQR_STRT_DTM": datetime.datetime.now().strftime("%Y%m%d") + start,
            "INQR_END_DTM":  datetime.datetime.now().strftime("%Y%m%d") + end,
            "SLL_BUY_DVSN_CD": "00",  # 00:전체, 01:매도, 02:매수
            "INQR_DVSN":     "00",
            "PDNO":          "",
            "ORD_GNO_BRNO":  "",
            "ODNO":          "",
            "INQR_DVSN_3":   "00",
            "INQR_DVSN_1":   "",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }
        return self._get(
            "/uapi/domestic-stock/v1/trading/inquire-daily-ccld",
            "VTTC8001R",
            params,
        )

    def get_account_profit(self) -> Dict:
        """계좌 수익률 조회 TR: VTTC8708R"""
        params = {
            "CANO":         self.account_no,
            "ACNT_PRDT_CD": self.account_type,
            "AFHR_FLPR_YN": "N",
            "OFL_YN":       "N",
            "INQR_DVSN":    "00",
            "UNPR_DVSN":    "01",
            "FUND_STTL_ICLD_YN": "N",
            "FNCG_AMT_AUTO_RDPT_YN": "N",
            "PRCS_DVSN":    "00",
            "CTX_AREA_FK100": "",
            "CTX_AREA_NK100": "",
        }
        return self._get(
            "/uapi/domestic-stock/v1/trading/inquire-balance",
            "VTTC8434R",
            params,
        )


# ── 세션 싱글톤 ──────────────────────────────────────
def get_api() -> Optional[KISApi]:
    """세션에서 API 인스턴스 반환"""
    if not st.session_state.get("api_connected"):
        return None
    if "kis_api" not in st.session_state:
        return None
    return st.session_state["kis_api"]


def init_api(app_key: str, app_secret: str, account_no: str) -> KISApi:
    """API 초기화 및 세션 저장"""
    api = KISApi(app_key, app_secret, account_no)
    st.session_state["kis_api"]      = api
    st.session_state["api_connected"] = True
    st.session_state["account_no"]    = account_no
    return api
