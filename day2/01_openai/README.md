# 📁 Day 2 · 01 · OpenAI API 기초

## 이 실습에서 배우는 것
- OpenAI API 호출 구조 이해
- Role 시스템 (system / user / assistant)
- 토큰과 비용 개념
- temperature, max_tokens 파라미터 조절

---

## 🖥 실습 명령어

### ① 폴더 이동
```bash
cd day2/01_openai
```

### ② 기본 API 호출 테스트
```bash
python hello_openai.py
# 출력 예:
# 답변: 안녕하세요! 저는 투자 전문 AI 어시스턴트입니다...
# 사용 토큰: 입력 35 / 출력 87 / 합계 122
# 예상 비용: $0.000018
```

### ③ 파라미터 실험
```bash
python param_test.py
# temperature를 0.0 / 0.5 / 1.0 으로 바꿔가며
# 답변이 어떻게 달라지는지 확인
```

### ④ (실습) Claude Code로 실험

```bash
claude
```

**실습 미션 — temperature 실험**
```
> hello_openai.py 를 수정해서
  같은 질문에 temperature=0.0, 0.5, 1.0 으로
  각각 답변을 받아서 비교해주는 코드로 만들어줘
```

---

## 📐 핵심 개념 정리

### 메시지 구조
```python
messages = [
    {
        "role": "system",       # AI의 역할/성격 설정
        "content": "당신은 한국 주식 투자 전문가입니다."
    },
    {
        "role": "user",         # 사용자 질문
        "content": "삼성전자 전망은?"
    },
    {
        "role": "assistant",    # AI 이전 답변 (멀티턴 시 포함)
        "content": "..."
    },
]
```

### 주요 파라미터
```
model        : 사용할 모델
               gpt-4o-mini  (저렴, 실습 권장)
               gpt-4o       (고성능, 비쌈)

temperature  : 창의성 조절 (0.0 ~ 2.0)
               0.0 → 항상 같은 답변 (정확성 중요할 때)
               0.3 → 금융 분석 권장값
               1.0 → 다양한 답변 (창작 등)

max_tokens   : 최대 응답 길이
               500  → 짧은 답변
               2000 → 긴 분석 보고서

stream       : 실시간 스트리밍 (True/False)
               True → 글자가 하나씩 실시간 출력
```

### 비용 계산
```
gpt-4o-mini 기준:
입력: $0.150 / 1M 토큰
출력: $0.600 / 1M 토큰

1000번 질문 예시:
평균 200토큰 입력 + 500토큰 출력
= (200 × 0.00000015) + (500 × 0.0000006) × 1000번
= 약 $0.33 (약 450원)  → 매우 저렴!
```

---

## ❓ 자주 묻는 질문

**Q. `AuthenticationError` 오류가 나요**
```
.env 파일의 OPENAI_API_KEY 확인
sk- 로 시작하는 전체 키가 맞는지 확인
```

**Q. `RateLimitError` 오류가 나요**
```
API 사용 한도 초과 → 잠시 기다렸다가 재시도
또는 OpenAI 대시보드에서 크레딧 확인
```
