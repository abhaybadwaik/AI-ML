"""
Phase 2 · Lesson 2 — Text Splitters
Splitting large documents into small chunks for LLM processing

WHAT WE ARE TRYING TO ACHIEVE:
LLMs have token limits — we can't send 35 pages at once.
Text Splitters break documents into small chunks.
Only relevant chunks are sent to LLM when user asks a question.

Two key parameters:
  chunk_size    → max size of each chunk
  chunk_overlap → how much chunks overlap to keep context
"""

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter, TokenTextSplitter
load_dotenv()

# load the research paper first
loader = PyPDFLoader(r"C:\Users\abhay\OneDrive\Desktop\AI-ML\Langchain\Phase2\NEW_SYNOPSIS (Autosaved).pdf")
docs = loader.load()

print(f"Original document : {len(docs)} pages")
print(f"Total characters  : {sum(len(d.page_content) for d in docs)}")
print()


# ── 1. RecursiveCharacterTextSplitter ────────────────────────
# Most used splitter in real projects
# Splits by: paragraphs → sentences → words → characters
# Tries to keep text meaningful at each split
# Use when: splitting any document for RAG

print("=== RecursiveCharacterTextSplitter ===")
print()

recursive_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,       # max 500 characters per chunk
    chunk_overlap=50,     # 50 chars overlap between chunks
    length_function=len,  # measure by character count
)

recursive_chunks = recursive_splitter.split_documents(docs)

print(f"Total chunks created : {len(recursive_chunks)}")
print(f"Avg chunk size       : {sum(len(c.page_content) for c in recursive_chunks) // len(recursive_chunks)} chars")
print()

# look at first chunk
print("--- Chunk 1 ---")
print("Content:", recursive_chunks[0].page_content)
print("Metadata:", recursive_chunks[0].metadata)
print()

# look at chunk 2 — notice overlap with chunk 1
print("--- Chunk 2 ---")
print("Content:", recursive_chunks[1].page_content)
print()


# ── 2. chunk_overlap — why it matters ────────────────────────
# Without overlap — context breaks at boundaries
# With overlap — chunks share some text so meaning isn't lost

print("=== Why chunk_overlap matters ===")
print()

# no overlap
no_overlap_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=0,    # no overlap
)

# with overlap
with_overlap_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,  # 100 chars overlap
)

no_overlap_chunks = no_overlap_splitter.split_documents(docs)
with_overlap_chunks = with_overlap_splitter.split_documents(docs)

print(f"No overlap   → {len(no_overlap_chunks)} chunks")
print(f"With overlap → {len(with_overlap_chunks)} chunks")
print()
print("With overlap has more chunks because shared text adds volume.")
print("But context is preserved across chunk boundaries.")
print()


# ── 3. TokenTextSplitter ─────────────────────────────────────
# Splits by token count instead of character count
# More accurate for LLM token limits
# Use when: you need precise token control

print("=== TokenTextSplitter ===")
print()

token_splitter = TokenTextSplitter(
    chunk_size=200,      # max 200 tokens per chunk
    chunk_overlap=20,    # 20 token overlap
)

token_chunks = token_splitter.split_documents(docs)

print(f"Total chunks created : {len(token_chunks)}")
print()
print("--- First token chunk ---")
print(token_chunks[0].page_content[:300])
print()


# ── 4. Chunk size guide ───────────────────────────────────────
print("""
=== Chunk size guide for real projects ===

chunk_size=500   → short focused chunks, better for precise Q&A
chunk_size=1000  → medium chunks, good balance
chunk_size=2000  → large chunks, better for summarization

chunk_overlap=10-15% of chunk_size is a good rule:
  chunk_size=500  → chunk_overlap=50
  chunk_size=1000 → chunk_overlap=100
  chunk_size=2000 → chunk_overlap=200

Most used in production:
  RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
""")