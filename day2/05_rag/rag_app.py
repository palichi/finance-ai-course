from rag_chain import load_rag_chain, format_source

QUESTIONS = [
    "삼성전자 최근 주가 흐름은?",
    "거래량이 가장 많았던 날은?",
    "SK하이닉스 주가가 오른 날은?",
    "가장 많이 상승한 종목은?",
    "12월에 삼성전자 주가는 어땠나요?",
]


def main():
    print("RAG 체인 로딩 중...\n")
    chain, retriever = load_rag_chain()

    for question in QUESTIONS:
        source_docs = retriever.invoke(question)
        answer = chain.invoke(question)

        print(f"❓ 질문: {question}")
        print(f"💬 답변: {answer}")
        print(f"📄 참고 데이터 ({min(3, len(source_docs))}건):")
        for i, doc in enumerate(source_docs[:3], start=1):
            print(format_source(doc, i))
        print()


if __name__ == "__main__":
    main()
