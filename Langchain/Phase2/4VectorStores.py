"""
Phase 2 · Lesson 4 — Vector Stores
Storing and searching embeddings efficiently

WHAT WE ARE TRYING TO ACHIEVE:
We have 67 chunks converted to 384 numbers each.
Without vector store — we compare question against all chunks manually. Slow.
Vector Store = database built specifically for storing and searching vectors.

Two stores:
FAISS  → Facebook's vector search library, saves to disk, fast
Chroma → Easy to use, saves to disk, good for production
"""

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS, Chroma

load_dotenv()

PDF_PATH = "Phase2/NEW_SYNOPSIS (Autosaved).pdf"

# ── Step 1: Load, split, embed ────────────────────────────────
print("Loading and splitting document...")
loader = PyPDFLoader(PDF_PATH)
docs = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)
print(f"Total chunks: {len(chunks)}")

print("Loading embedding model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
print("Ready!")
print()


# ── 2. FAISS Vector Store ─────────────────────────────────────
# Facebook AI Similarity Search
# Fast, runs locally, saves to disk
# Use when: learning, small to medium projects

print("=== FAISS Vector Store ===")

# create FAISS store from chunks — embeds all chunks automatically
faiss_store = FAISS.from_documents(chunks, embeddings)
print(f"FAISS store created with {len(chunks)} chunks")

# save to disk — so you don't re-embed every time
faiss_store.save_local("Phase2/faiss_index")
print("FAISS store saved to disk!")
print()

# load from disk — next time just load, no re-embedding needed
faiss_store_loaded = FAISS.load_local(
    "Phase2/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)
print("FAISS store loaded from disk!")
print()

# search — find most relevant chunks for a question
question = "What is the research methodology used in this study?"
faiss_results = faiss_store_loaded.similarity_search(question, k=3)

print(f"Question: {question}")
print(f"Top 3 relevant chunks:")
for i, doc in enumerate(faiss_results, 1):
    print(f"\nResult {i}:")
    print(f"  Content : {doc.page_content[:150]}...")
    print(f"  Page    : {doc.metadata.get('page', 'N/A')}")
print()


# ── 3. similarity_search_with_score ──────────────────────────
# Same as similarity_search but also returns similarity score
# Use when: you want to see HOW relevant each result is

print("=== Search with Similarity Scores ===")
results_with_scores = faiss_store_loaded.similarity_search_with_score(question, k=3)

for i, (doc, score) in enumerate(results_with_scores, 1):
    print(f"Result {i} | Score: {score:.4f} | {doc.page_content[:100]}...")

print()
print("Note: In FAISS lower score = more similar (distance based)")
print()


# ── 4. Chroma Vector Store ────────────────────────────────────
# Easy to use, saves to disk automatically
# Use when: production apps, need metadata filtering

print("=== Chroma Vector Store ===")

chroma_store = Chroma.from_documents(
    chunks,
    embeddings,
    persist_directory="Phase2/chroma_db"  # saves to disk automatically
)
print(f"Chroma store created and saved to disk!")
print()

# search
chroma_results = chroma_store.similarity_search(question, k=3)

print(f"Question: {question}")
print(f"Top 3 relevant chunks:")
for i, doc in enumerate(chroma_results, 1):
    print(f"\nResult {i}:")
    print(f"  Content : {doc.page_content[:150]}...")
    print(f"  Page    : {doc.metadata.get('page', 'N/A')}")
print()


# ── 5. FAISS vs Chroma ────────────────────────────────────────
print("""
=== FAISS vs Chroma ===

FAISS:
  ✅ Very fast search
  ✅ Great for large datasets
  ❌ Manual save/load needed
  Use for: high performance, large scale

Chroma:
  ✅ Auto saves to disk
  ✅ Easy metadata filtering
  ✅ Beginner friendly
  Use for: production apps, easier workflow

Both:
  → Store your chunk embeddings permanently
  → Search by meaning not keywords
  → Return most relevant chunks for any question
  → Never need to re-embed unless document changes
""")