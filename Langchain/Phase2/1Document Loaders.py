"""
Phase 2 · Lesson 1 — Document Loaders
Loading data from PDF, URL, and CSV into LangChain

WHAT WE ARE TRYING TO ACHIEVE:
Before we can ask questions about our own data,
we need to load it into LangChain first.
Document Loaders do exactly this — they read files
and convert them into Document objects LangChain can work with.

Document object has two parts:
  page_content → the actual text
  metadata     → where it came from, page number etc.
"""

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader, WebBaseLoader, CSVLoader

load_dotenv()


# ── 1. PyPDFLoader — load a PDF file ─────────────────────────
# Use when: loading research papers, policy docs, manuals
# Real world: any PDF based knowledge base

print("=== PyPDFLoader ===")
print("Loading research paper PDF...")
print()

pdf_loader = PyPDFLoader("Phase2/ResearchPaper.pdf")  # path to your PDF
pdf_docs = pdf_loader.load()

print(f"Total pages loaded : {len(pdf_docs)}")
print(f"Type of each doc   : {type(pdf_docs[0]).__name__}")
print()

# look at first page
first_page = pdf_docs[0]
print("--- Page 1 ---")
print("Content preview:")
print(first_page.page_content[:300])   # first 300 chars
print()
print("Metadata:")
print(first_page.metadata)             # source, page number
print()


# ── 2. WebBaseLoader — load from a URL ───────────────────────
# Use when: loading website content, blog posts, docs
# Real world: build a bot that answers from your website

print("=== WebBaseLoader ===")
print("Loading content from Wikipedia...")
print()

web_loader = WebBaseLoader("https://en.wikipedia.org/wiki/Large_language_model")
web_docs = web_loader.load()

print(f"Total docs loaded  : {len(web_docs)}")
print(f"Content preview    : {web_docs[0].page_content[:300]}")
print()
print("Metadata:")
print(web_docs[0].metadata)
print()


# ── 3. Key observations ───────────────────────────────────────
print("=== What Document object looks like ===")
print()
print("Every loader returns a list of Document objects.")
print("Each Document has:")
print()
print("  doc.page_content → the actual text extracted")
print("  doc.metadata     → source info (filename, page, url)")
print()
print(f"PDF  doc metadata example : {pdf_docs[0].metadata}")
print(f"Web  doc metadata example : {web_docs[0].metadata}")
print()

print("""
=== When to use which loader ===
PyPDFLoader    → PDF files (research papers, manuals, policy docs)
WebBaseLoader  → Websites, Wikipedia, blog posts, documentation
CSVLoader      → CSV files (product catalogs, customer data)

Key point:
  All loaders return the same Document object format.
  page_content + metadata — always the same structure.
  This is why you can mix sources in one RAG pipeline.
""")