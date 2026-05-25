"""
Phase 3 · Lesson 4 — Hybrid Search
Combining semantic search and keyword search for better retrieval

WHAT WE ARE TRYING TO ACHIEVE:
Semantic search finds by meaning but misses exact keywords.
Keyword search finds exact words but misses meaning.
Hybrid combines both — best of both worlds.
"""

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os

load_dotenv()


# ── Setup ─────────────────────────────────────────────────────
print("Setting up...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=300)

# load chunks for BM25 (needs raw documents)
loader = PyPDFLoader("Phase2/NEW_SYNOPSIS (Autosaved).pdf")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

# load FAISS store
faiss_store = FAISS.load_local(
    "Phase2/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)
print("✅ Ready!")
print()


# ── 1. Semantic Retriever (FAISS) ─────────────────────────────
semantic_retriever = faiss_store.as_retriever(search_kwargs={"k": 3})


# ── 2. BM25 Keyword Retriever ─────────────────────────────────
# BM25 = Best Match 25 — classic keyword search algorithm
# Finds chunks containing exact words from the question
bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 3


# ── 3. Hybrid — EnsembleRetriever ────────────────────────────
# Combines both retrievers with weights
# weights=[0.5, 0.5] → equal importance to both
# weights=[0.7, 0.3] → more weight to semantic
hybrid_retriever = EnsembleRetriever(
    retrievers=[semantic_retriever, bm25_retriever],
    weights=[0.5, 0.5]
)


# ── 4. RAG chain ──────────────────────────────────────────────
prompt = ChatPromptTemplate.from_messages([
    ("system", """Answer from context only. If not in context say 'I dont have enough information.'
Context: {context}"""),
    ("human", "{question}"),
])

def format_docs(docs):
    # deduplicate chunks
    seen = set()
    unique = []
    for doc in docs:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            unique.append(doc)
    return "\n\n".join(
        f"[Page {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}"
        for doc in unique
    )

def make_chain(retriever):
    return (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

semantic_chain = make_chain(semantic_retriever)
keyword_chain  = make_chain(bm25_retriever)
hybrid_chain   = make_chain(hybrid_retriever)


# ── 5. Compare all three ──────────────────────────────────────
print("="*60)
print("=== Hybrid Search Comparison ===")
print("="*60)

questions = [
    "What is Cochran's formula?",        # exact keyword — BM25 should win
    "What is UTAUT2?",                   # acronym — BM25 should win
    "Why do people hesitate to use UPI?", # meaning based — semantic should win
    "What is the sample size?",          # both should work
]

for q in questions:
    print(f"\nQ: {q}")
    print(f"Semantic : {semantic_chain.invoke(q)[:120]}...")
    print(f"Keyword  : {keyword_chain.invoke(q)[:120]}...")
    print(f"Hybrid   : {hybrid_chain.invoke(q)[:120]}...")
    print()

print("""
=== Summary ===
Semantic Search → finds by meaning, misses exact keywords
Keyword Search  → finds exact words, misses meaning
Hybrid Search   → combines both, best results overall

BM25Retriever      → keyword search
EnsembleRetriever  → combines multiple retrievers with weights

Production rule:
  Always use Hybrid Search in production RAG
  weights=[0.5, 0.5] is a good starting point
  Tune weights based on your document type
""")