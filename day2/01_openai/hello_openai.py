"""
OpenAI API 기초 실습
실행: python hello_openai.py
"""

import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv("../../.env")

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ── 시스템 프롬프트 (AI 역할 설정) ───────────────
SYSTEM_PROMPT = """
당신은 한국 주식 투자 전문 AI 어시스턴트입니다.
- 20년 이상의 한국 주식시장 분석 경험을 가지고 있습니다
- 구체적인 수치와 근거를 제시하며 답변합니다
- 항상 마지막에 "⚠️ 본 답변은 참고용이며 투자 결정은 본인 판단으로 하세요" 를 추가합니다
"""

# ── API 호출 ──────────────────────────────────────
def ask(question: str, temperature: float = 0.3) -> str:
    """OpenAI API에 질문을 보내고 답변을 받습니다"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",        # 저렴하고 빠른 모델
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": question},
        ],
        temperature=temperature,    # 창의성 (0=일정, 1=창의적)
        max_tokens=500,             # 최대 응답 길이
    )

    answer     = response.choices[0].message.content
    input_tok  = response.usage.prompt_tokens
    output_tok = response.usage.completion_tokens
    total_tok  = response.usage.total_tokens
    cost       = (input_tok * 0.00000015) + (output_tok * 0.0000006)

    print(f"\n{'='*50}")
    print(f"질문: {question}")
    print(f"{'='*50}")
    print(f"답변: {answer}")
    print(f"{'─'*50}")
    print(f"📊 사용 토큰: 입력 {input_tok} / 출력 {output_tok} / 합계 {total_tok}")
    print(f"💰 예상 비용: ${cost:.6f} (약 {cost*1350:.2f}원)")

    return answer


# ── API 호출 (비교용, 결과만 반환) ───────────────
def ask_silent(question: str, temperature: float) -> tuple[str, int, int, float]:
    """API 호출 후 (답변, 입력토큰, 출력토큰, 비용) 반환 (출력 없음)"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": question},
        ],
        temperature=temperature,
        max_tokens=500,
    )
    answer     = response.choices[0].message.content
    input_tok  = response.usage.prompt_tokens
    output_tok = response.usage.completion_tokens
    cost       = (input_tok * 0.00000015) + (output_tok * 0.0000006)
    return answer, input_tok, output_tok, cost


# ── 실행 ─────────────────────────────────────────
if __name__ == "__main__":
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ .env 파일에 OPENAI_API_KEY를 입력하세요")
        exit(1)

    QUESTION = "오늘 삼성전자 주식을 사야 할까요? 한 문장으로 답해주세요."
    TEMPERATURES = [0.0, 0.5, 1.0]

    print("\n" + "="*60)
    print(f"🧪 Temperature 비교 실험")
    print(f"질문: {QUESTION}")
    print("="*60)

    results = []
    for temp in TEMPERATURES:
        print(f"\n⏳ temperature={temp} 호출 중...", end="", flush=True)
        answer, in_tok, out_tok, cost = ask_silent(QUESTION, temp)
        results.append((temp, answer, in_tok, out_tok, cost))
        print(" 완료")

    # 결과 나란히 출력
    print("\n" + "="*60)
    print("📊 비교 결과")
    print("="*60)
    total_cost = 0.0
    for temp, answer, in_tok, out_tok, cost in results:
        total_cost += cost
        print(f"\n[ temperature = {temp} ]")
        print(f"  답변: {answer}")
        print(f"  토큰: 입력 {in_tok} / 출력 {out_tok}  |  비용: ${cost:.6f} (약 {cost*1350:.2f}원)")

    print("\n" + "-"*60)
    print(f"💰 총 비용: ${total_cost:.6f} (약 {total_cost*1350:.2f}원)")
    print("-"*60)
    print("\n💡 관찰 포인트:")
    print("  - temperature=0.0 : 매번 동일한 답변 (결정론적)")
    print("  - temperature=0.5 : 적당한 다양성")
    print("  - temperature=1.0 : 가장 창의적/다양한 답변")
