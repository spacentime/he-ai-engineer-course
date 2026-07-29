# eval_rag_tiny.py
"""
Super-short RAG eval demo:
- Custom: keyword_recall, cited_in_retrieved
- RAGAS: answer_relevancy, faithfulness, context_precision, context_recall

Run:
  pip install langchain langchain-openai langchain-chroma datasets ragas chromadb
  export OPENAI_API_KEY=...
  python eval_rag_tiny.py
"""

import os, re, time, pathlib
from typing import List
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from datasets import Dataset
from ragas import evaluate
from ragas.metrics import answer_relevancy, faithfulness, context_precision, context_recall

INDEX_DIR = "./rag_index_photography"
COLLECTION = "photography"
K = int(os.getenv("EVAL_TOP_K", "5"))

GOLD = [
    {
        "q": "What camera settings control exposure? Explain briefly.",
        "keywords": ["aperture", "shutter", "iso", "exposure"],
        "expected_titles": ["Aperture", "Shutter speed", "ISO", "Exposure (photography)"],
    },
    {
        "q": "How can a photographer increase depth of field?",
        "keywords": ["aperture", "f-number", "distance", "focal length", "depth of field"],
        "expected_titles": ["Depth of field", "Aperture"],
    },
    {
        "q": "What is the rule of thirds and how is it used?",
        "keywords": ["composition", "grid", "intersections", "balance", "rule of thirds"],
        "expected_titles": ["Rule of thirds", "Photography"],
    },
    {
        "q": "What does white balance do in a digital camera?",
        "keywords": ["color", "temperature", "tint", "neutral", "white balance"],
        "expected_titles": ["White balance"],
    },
]

def run_answer(llm: ChatOpenAI, retriever, q: str):
    docs = retriever.invoke(q)
    titles = [d.metadata.get("title", "") for d in docs]
    ctx = [d.page_content for d in docs]
    numbered = "\n\n".join(f"[{i+1}] {titles[i]}\n{ctx[i][:800]}" for i in range(len(docs)))
    prompt = f"""Answer ONLY from CONTEXT in 3–6 bullets.
                End with: CITATIONS: [i]; [j]

                Q: {q}

                CONTEXT:
                {numbered}
            """
    ans = llm.invoke(prompt).content.strip()
    cited_idx = re.findall(r"\[(\d+)\]", re.search(r"CITATIONS:\s*(.+)$", ans, flags=re.I|re.M).group(1)) if "CITATIONS:" in ans else []
    cited_titles = [titles[int(i)-1] for i in cited_idx if i.isdigit() and 1 <= int(i) <= len(titles)]
    return ans, cited_titles, titles, ctx

def keyword_recall(answer: str, kws: List[str]) -> float:
    al = answer.lower()
    return sum(kw.lower() in al for kw in kws) / max(1, len(kws))

def cited_in_retrieved(cited: List[str], retrieved: List[str]) -> float:
    if not cited: return 1.0
    r = {t.strip().lower() for t in retrieved}
    return sum(t.strip().lower() in r for t in cited) / len(cited)

def build_reference(vdb: Chroma, expected_titles: List[str], k_per=6, max_chars=6000) -> str:
    blocks, seen = [], set()
    for t in expected_titles:
        for d in vdb.similarity_search("", k=k_per, filter={"title": t}):
            if d.page_content not in seen:
                seen.add(d.page_content); blocks.append(d.page_content)
    return ("\n\n".join(blocks))[:max_chars] or "(no reference)"

def main():
    emb = OpenAIEmbeddings(model="text-embedding-3-small")
    persist_path = pathlib.Path(INDEX_DIR).resolve()
    vdb = Chroma(embedding_function=emb, persist_directory=str(persist_path), collection_name=COLLECTION)
    retriever = vdb.as_retriever(search_kwargs={"k": K})
    llm = ChatOpenAI(model=os.getenv("EVAL_LLM", "gpt-4o-mini"), temperature=0)

    rq, ra, rc, rr = [], [], [], []
    kw_sum = cir_sum = 0.0; lat = []

    print("Evaluating...\n")
    for i, item in enumerate(GOLD, 1):
        t0 = time.time()
        ans, cited, retrieved, ctx = run_answer(llm, retriever, item["q"])
        lat.append((time.time() - t0) * 1000)
        kw = keyword_recall(ans, item["keywords"]); cir = cited_in_retrieved(cited, retrieved)
        kw_sum += kw; cir_sum += cir
        print(f"Q{i}: {item['q']}\n  keyword_recall={kw:.2f}  cited∈retrieved={cir:.2f}  latency={lat[-1]:.0f}ms")
        if cited: print("  cited:", "; ".join(cited))
        rq.append(item["q"]); ra.append(ans); rc.append(ctx); rr.append(build_reference(vdb, item["expected_titles"]))

    n = len(GOLD)
    print(f"\nAverages → keyword_recall={kw_sum/n:.2f}  cited∈retrieved={cir_sum/n:.2f}  latency={sum(lat)/n:.0f}ms")

    ds = Dataset.from_dict({"question": rq, "answer": ra, "contexts": rc, "reference": rr, "ground_truth": rr})
    res = evaluate(ds, metrics=[answer_relevancy, faithfulness, context_precision, context_recall], llm=llm, embeddings=emb)

    print("\nRAGAS:")
    scores = getattr(res, "scores", None)
    if isinstance(scores, dict):
        for k in ["answer_relevancy","faithfulness","context_precision","context_recall"]:
            if k in scores: 
                v = getattr(scores[k], "score", scores[k])
                try: print(f"  {k}: {float(v):.3f}")
                except: pass
    else:
        print(res)

if __name__ == "__main__":
    main()
