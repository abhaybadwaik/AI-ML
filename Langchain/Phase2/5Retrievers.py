"""
Phase 2 · Lesson 5 — Retrievers
Wrapping vector stores for use in LangChain chains

WHAT WE ARE TRYING TO ACHIEVE:
Vector store needs .similarity_search() called manually.
Retriever wraps it so it works inside LCEL chains automatically.
This is the final piece before building full RAG pipeline.
"""

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

load_dotenv()

PDF_PATH = "Phase2/NEW_SYNOPSIS (Autosaved).pdf"

# ── Setup: Load, Split, Embed, Store ─────────────────────────
print("Setting up vector store...")
loader = PyPDFLoader(PDF_PATH)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# load from disk if exists, else create
import os
if os.path.exists("Phase2/faiss_index"):
    faiss_store = FAISS.load_local("Phase2/faiss_index", embeddings, allow_dangerous_deserialization=True)
    print("Loaded FAISS from disk!")
else:
    faiss_store = FAISS.from_documents(chunks, embeddings)
    faiss_store.save_local("Phase2/faiss_index")
    print("Created and saved FAISS!")
print()


# ── 1. Basic Retriever ────────────────────────────────────────
# .as_retriever() wraps vector store into a retriever
# search_kwargs={"k": 3} → return top 3 chunks

print("=== Basic Retriever ===")

retriever = faiss_store.as_retriever(
    search_type="similarity",   # find most similar chunks
    search_kwargs={"k": 3}      # return top 3
)

question = "What is the research methodology?"
results = retriever.invoke(question)

print(f"Question: {question}")
print(f"Chunks retrieved: {len(results)}")
for i, doc in enumerate(results, 1):
    print(f"\nChunk {i} (Page {doc.metadata.get('page', 'N/A')}):")
    print(f"  {doc.page_content[:150]}...")
print()


# ── 2. MMR Retriever ──────────────────────────────────────────
# MMR = Maximum Marginal Relevance
# Finds relevant chunks but avoids returning duplicates
# Use when: results are too similar to each other

print("=== MMR Retriever ===")

mmr_retriever = faiss_store.as_retriever(
    search_type="mmr",           # diverse results
    search_kwargs={
        "k": 3,                  # return 3 chunks
        "fetch_k": 10,           # consider top 10 first, then pick 3 diverse ones
    }
)

mmr_results = mmr_retriever.invoke(question)
print(f"MMR chunks retrieved: {len(mmr_results)}")
for i, doc in enumerate(mmr_results, 1):
    print(f"Chunk {i} (Page {doc.metadata.get('page', 'N/A')}): {doc.page_content[:100]}...")
print()


# ── 3. Score Threshold Retriever ─────────────────────────────
# Only returns chunks above a similarity threshold
# Use when: you want quality control — no irrelevant chunks

print("=== Score Threshold Retriever ===")

threshold_retriever = faiss_store.as_retriever(
    search_type="similarity_score_threshold",
    search_kwargs={
        "score_threshold": 0.5,  # only return chunks with score above 0.5
        "k": 3
    }
)

threshold_results = threshold_retriever.invoke(question)
print(f"Chunks above threshold: {len(threshold_results)}")
for i, doc in enumerate(threshold_results, 1):
    print(f"Chunk {i}: {doc.page_content[:100]}...")
print()


# ── 4. Retriever inside LCEL chain ───────────────────────────
# THIS is the real power — retriever plugs into chain automatically
# No manual searching, no manual passing — all automatic

print("=== Retriever in LCEL Chain ===")

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=300)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are a helpful assistant. Answer the question based on the context provided.
If the answer is not in the context, say 'I don't know'.

Context:
{context}"""),
    ("human", "{question}"),
])

def format_docs(docs):
    """Join retrieved chunks into one string for the prompt"""
    return "\n\n".join(doc.page_content for doc in docs)

# full RAG chain — retriever finds chunks, LLM answers from them
rag_chain = (
    {
        "context": retriever | format_docs,  # retrieve chunks → format as string
        "question": RunnablePassthrough(),   # pass question through unchanged
    }
    | prompt
    | llm
    | StrOutputParser()
)

questions = [
    "What is the research methodology used in this study?",
    "What are the objectives of the study?",
    "What are the limitations of this study?",
]

for q in questions:
    print(f"Q: {q}")
    answer = rag_chain.invoke(q)
    print(f"A: {answer}")
    print()

print("""
=== Summary ===
Retriever = vector store wrapped for use in LCEL chains

Three types:
  similarity              → most similar chunks (default)
  mmr                     → diverse chunks, no repetition
  similarity_score_threshold → only high quality chunks

Key line:
  retriever = faiss_store.as_retriever(search_type=..., search_kwargs=...)

In RAG chain:
  context: retriever | format_docs  → auto retrieves and formats chunks
  question: RunnablePassthrough()   → passes question unchanged
""")