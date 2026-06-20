import os
import sys
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / "../../.env")

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

CHROMA_PATH = Path(__file__).parent / "../04_chromadb/chroma_db"
COLLECTION_NAME = "stock_data"

QUESTIONS = [
    "삼성전자 최근 주가 흐름은?",
    "거래량이 가장 많았던 날은?",
    "SK하이닉스 주가가 오른 날은?",
    "가장 많이 상승한 종목은?",
    "12월에 삼성전자 주가는 어땠나요?",
]

SYSTEM_PROMPT = """당신은 한국 주식 데이터 분석 전문가입니다.
제공된 실제 주가 데이터를 기반으로 답변하세요.
데이터에 없는 내용은 없다고 솔직하게 말하세요."""

PROMPT = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "다음 주식 데이터를 참고하여 질문에 답변하세요.\n\n{context}\n\n질문: {question}"),
])


def load_vectorstore():
    if not CHROMA_PATH.exists():
        print("먼저 build_db.py 를 실행하세요")
        sys.exit(1)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    vectorstore = Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_PATH),
    )
    return vectorstore


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def format_source(doc, idx):
    metadata = doc.metadata
    date = metadata.get("date", "날짜 없음")
    name = metadata.get("name", "종목 없음")
    code = metadata.get("code", "코드 없음")
    content_preview = doc.page_content[:60].replace("\n", " ")
    return f"  {idx}. [{date}] {name}({code}): {content_preview}..."


K = 5


def load_rag_chain():
    vectorstore = load_vectorstore()

    doc_count = vectorstore._collection.count()
    print(f"✅ RAG 체인 로딩 완료 (벡터 DB: {doc_count:,}건, k={K})\n")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.1)
    retriever = vectorstore.as_retriever(search_kwargs={"k": K})

    chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | PROMPT
        | llm
        | StrOutputParser()
    )
    return chain, retriever


def run():
    print("ChromaDB 로딩 중...\n")
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
    run()
