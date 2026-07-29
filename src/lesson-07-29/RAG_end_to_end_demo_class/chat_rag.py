# chat_rag.py
"""
Interactive chat with the Photography RAG index (no agent dependencies).

Usage:
  export OPENAI_API_KEY=...
  python chat_rag.py
"""
import os, sys, pathlib
from typing import List

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate

INDEX_DIR = "./rag_index_photography"
COLLECTION = "photography"

SYSTEM_RULES = (
    "You are a concise photography assistant.\n"
    "- Always base answers ONLY on the provided CONTEXT.\n"
    "- If context is insufficient, say so.\n"
    "- Keep answers to ≤6 bullets/sentences.\n"
    "- Add bracketed citations [1], [2], ... that map to the numbered sources."
)

ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", SYSTEM_RULES),
        ("human",
         "QUESTION: {question}\n\n"
         "CONTEXT (numbered sources):\n{context}\n\n"
         "Answer concisely and include bracketed citations that map to the numbers above.")
    ]
)

def ensure_index():
    persist_path = pathlib.Path(INDEX_DIR).resolve()
    if not persist_path.exists() or not any(persist_path.iterdir()):
        print("❌ No index found. Run: `python build_rag.py` first.")
        sys.exit(1)

def format_context(docs: List[Document]) -> str:
    parts = []
    for i, d in enumerate(docs, 1):
        title = d.metadata.get("title", "Unknown")
        source = d.metadata.get("source", "")
        snippet = d.page_content[:1200]
        parts.append(f"[{i}] {title} — {source}\n{snippet}")
    return "\n\n".join(parts) if parts else "(no context)"

def make_components():
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    persist_path = pathlib.Path(INDEX_DIR).resolve()
    vectordb = Chroma(
        embedding_function=embeddings,
        persist_directory=str(persist_path),
        collection_name=COLLECTION,
    )
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.0)
    return retriever, llm

def answer_question(retriever, llm, question: str) -> str:
    docs: List[Document] = retriever.invoke(question)  # modern API
    context = format_context(docs)
    msg = ANSWER_PROMPT.invoke({"question": question, "context": context})
    resp = llm.invoke(msg)
    return resp.content.strip()

def main():
    ensure_index()
    retriever, llm = make_components()
    print("\n📷 Photography RAG Chat — type 'exit' to quit.")
    while True:
        try:
            q = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nBye!")
            break
        if q.lower() in {"exit", "quit"}:
            print("Bye!")
            break
        try:
            ans = answer_question(retriever, llm, q)
            print(f"\nAssistant:\n{ans}")
        except Exception as e:
            print(f"[error] {e}")

if __name__ == "__main__":
    main()
''' Example questions:
“What three camera settings form the exposure triangle?”
“How does aperture size affect depth of field?”
“What happens if I use a slow shutter speed without a tripod?”
“Why do photographers care about ISO?”
'''
