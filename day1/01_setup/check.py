"""
환경 점검 스크립트
강의 시작 전 모든 세팅이 올바른지 확인합니다.
실행: streamlit run check.py
"""

import streamlit as st
import sys
import os

st.set_page_config(page_title="환경 점검", page_icon="✅", layout="centered")
st.title("✅ 환경 점검 — 강의 준비 확인")
st.caption("모든 항목이 초록색이면 강의 시작 준비 완료!")

results = []

# 1. Python 버전
v = sys.version_info
ok = v.major == 3 and v.minor >= 11
results.append(("Python 버전", f"{v.major}.{v.minor}.{v.micro}", ok,
                "3.11 이상 필요"))

# 2. 패키지 확인
packages = [
    ("streamlit",  "Streamlit 웹앱"),
    ("requests",   "HTTP 요청"),
    ("pandas",     "데이터 처리"),
    ("numpy",      "수치 계산"),
    ("plotly",     "차트 시각화"),
    ("openai",     "OpenAI API"),
    ("langchain",  "LangChain"),
    ("chromadb",   "ChromaDB 벡터DB"),
    ("dotenv",     "환경변수 (.env)"),
]
for pkg, desc in packages:
    try:
        mod = __import__(pkg)
        ver = getattr(mod, "__version__", "설치됨")
        results.append((f"패키지: {desc}", ver, True, ""))
    except ImportError:
        results.append((f"패키지: {desc}", "미설치", False,
                        f"pip install {pkg}"))

# 3. .env 파일 확인
env_path = os.path.join(os.path.dirname(__file__), "../../.env")
env_exists = os.path.exists(env_path)
results.append((".env 파일", "존재함" if env_exists else "없음", env_exists,
                "cp .env.example .env 실행 후 Key 입력"))

# 4. API Key 확인
from dotenv import load_dotenv
load_dotenv(env_path)

for key_name, desc in [
    ("KIS_APP_KEY",    "KIS App Key"),
    ("KIS_APP_SECRET", "KIS App Secret"),
    ("KIS_ACCOUNT_NO", "KIS 계좌번호"),
    ("OPENAI_API_KEY", "OpenAI API Key"),
    ("FSS_API_KEY",    "금융위 API Key"),
]:
    val = os.getenv(key_name, "")
    filled = bool(val) and "여기에" not in val and len(val) > 5
    masked = val[:4] + "****" if filled else "미입력"
    results.append((f"API Key: {desc}", masked, filled,
                    f".env 파일에 {key_name} 입력 필요"))

# 결과 출력
st.markdown("---")
pass_count = sum(1 for _, _, ok, _ in results if ok)
total = len(results)

col1, col2 = st.columns(2)
col1.metric("통과", f"{pass_count} / {total}")
col2.metric("상태", "✅ 준비 완료!" if pass_count == total else "⚠️ 확인 필요")

st.markdown("---")
for name, value, ok, tip in results:
    icon = "✅" if ok else "❌"
    col_a, col_b, col_c = st.columns([3, 2, 3])
    col_a.write(f"{icon} {name}")
    col_b.code(value)
    if not ok and tip:
        col_c.caption(f"💡 {tip}")

if pass_count == total:
    st.success("🎉 모든 항목 통과! 강의를 시작할 수 있습니다.")
    st.balloons()
else:
    st.warning(f"⚠️ {total - pass_count}개 항목을 확인해주세요. 강사에게 도움을 요청하세요.")
