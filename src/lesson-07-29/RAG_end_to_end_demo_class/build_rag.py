# build_rag.py
"""
Builds a photography knowledge base from public Wikipedia pages,
creates a Chroma index with OpenAI embeddings, and runs a quick smoke test.

Usage:
  export OPENAI_API_KEY=...
  python build_rag.py
"""
import os, time, pathlib, requests, shutil
from typing import List
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
# from dotenv import load_dotenv
# load_dotenv()  # l
DATA_DIR = pathlib.Path("./data_photography")
INDEX_DIR = "./rag_index_photography"
COLLECTION = "photography"
DATA_DIR.mkdir(parents=True, exist_ok=True)

TITLES = [
    "Photography",
    "Aperture",
    "Shutter speed",
    "ISO",
    "Depth of field",
    "Rule of thirds",
    "White balance",
    "Exposure (photography)",
]

WIKI_SUMMARY_URL = "https://en.wikipedia.org/api/rest_v1/page/summary/{title}"
WIKI_CANONICAL = "https://en.wikipedia.org/wiki/{title}"


def fetch_plain_wikipedia(title: str) -> str:
    url = WIKI_SUMMARY_URL.format(title=title.replace(" ", "_"))
    headers = {"User-Agent": "RAG-demo/1.0 (HUJI AI Engineering)"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()
    data = r.json()
    # `extract` contains a clean summary text
    return data.get("extract", "")

def download_corpus(titles: List[str]) -> List[Document]:
    docs = []
    for t in titles:
        print(f"↳ downloading: {t}")
        text = fetch_plain_wikipedia(t)
        (DATA_DIR / f"{t.replace(' ', '_')}.txt").write_text(text, encoding="utf-8")
        docs.append(
            Document(
                page_content=text,
                metadata={"title": t, "source": WIKI_CANONICAL.format(title=t.replace(" ", "_"))},
            )
        )
        time.sleep(0.3)  # be gentle
    return docs

def build_index(docs: List[Document], persist_dir: str = INDEX_DIR):
    # Convert to absolute path to avoid Windows path issues
    persist_path = pathlib.Path(persist_dir).resolve()
    
    # Remove existing corrupted index if it exists
    if persist_path.exists():
        print(f"🗑️  Removing existing index at {persist_path}...")
        try:
            shutil.rmtree(persist_path)
        except Exception as e:
            print(f"⚠️  Warning: Could not fully remove existing index: {e}")
            # Try to remove individual files
            for item in persist_path.iterdir():
                try:
                    if item.is_dir():
                        shutil.rmtree(item)
                    else:
                        item.unlink()
                except Exception:
                    pass
    
    print("🔧 splitting & embedding...")
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
    chunks = splitter.split_documents(docs)

    embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
    # Use absolute path string for ChromaDB
    vectordb = Chroma.from_documents(
        chunks,
        embedding=embeddings,
        persist_directory=str(persist_path),
        collection_name=COLLECTION,
    )
    vectordb.persist()
    print(f"✅ index built → {persist_path} (chunks={len(chunks)})")

def smoke_test():
    print("\n🧪 smoke test (top-3 passages)...")
    # Use absolute path for consistency
    persist_path = pathlib.Path(INDEX_DIR).resolve()
    vectordb = Chroma(
        embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
        persist_directory=str(persist_path),
        collection_name=COLLECTION,
    )
    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.0)

    q = "What affects depth of field in photography? Provide bullet points and cite sources."
    docs = retriever.invoke(q)  # ✅ instead of get_relevant_documents
    context = "\n\n---\n\n".join(
        f"[{i+1}] {d.metadata.get('title')} — {d.metadata.get('source')}\n{d.page_content[:1200]}"
        for i, d in enumerate(docs)
    )
    prompt = f"""Answer ONLY from the CONTEXT. Use 3–6 concise bullets.
Add inline citations like [1], [2] that map to the numbered sources.

QUESTION: {q}

CONTEXT:
{context}
"""
    resp = llm.invoke(prompt)
    print("\nAnswer:\n", resp.content)


if __name__ == "__main__":
    print("⬇️  Downloading public data…")
    docs = download_corpus(TITLES)
    print("📦 Building vector index…")
    build_index(docs, INDEX_DIR)
    smoke_test()
    print("\nAll set. Next: `python chat_rag.py` or `python eval_rag.py`")
