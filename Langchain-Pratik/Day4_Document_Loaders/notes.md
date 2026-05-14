# Day 4 — Document Loaders & Text Splitters

## What is the concept?
**Document Loaders** read data from files (PDFs, CSVs, websites) and convert them into LangChain `Document` objects.  
**Text Splitters** break large documents into smaller, manageable chunks so they can be processed by an LLM or stored in a vector database.

## Why do we use it?
LLMs have a **context window limit** (max tokens they can process). A 100-page PDF won't fit. We must:
1. Load the file into structured `Document` objects
2. Split them into chunks the LLM can handle
3. Feed only the relevant chunks to the AI

## Real-Life Use Cases
- Legal document analyzer that reads contracts (PDFs)
- Instagram analytics tool that reads your CSV report
- News aggregator that loads and summarizes articles from the web
- Internal HR policy bot that reads company PDF handbooks

---

## Part 1: Document Loaders

### PyPDFLoader — Load PDFs

**From your code (`Document/PDFs.py`)**
```python
from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader("Data/1.pdf")
documents = loader.load()

print("Total pages loaded:", len(documents))
print("First page content:", documents[0].page_content[:300])
print("Metadata:", documents[0].metadata)
# Metadata includes: {'source': 'Data/1.pdf', 'page': 0}
```

Each page becomes one `Document` object with:
- `.page_content` → the text
- `.metadata` → source file, page number

---

### CSVLoader — Load CSV Files

**From your code (`Document/CSV.py`)**
```python
from langchain_community.document_loaders.csv_loader import CSVLoader

loader = CSVLoader(file_path="Data/Instagram_Analytics.csv")
documents = loader.load()

print("Total rows loaded:", len(documents))
print(documents[0].page_content)   # each row = one Document
print(documents[0].metadata)       # {'source': 'file.csv', 'row': 0}
```

> Each row in the CSV becomes a separate `Document`. Your Instagram CSV had many rows — each row = one analytics entry.

---

### WebBaseLoader — Load Websites

**From your code (`Document/Web.py`)**
```python
from langchain_community.document_loaders import WebBaseLoader
from bs4 import SoupStrainer

loader = WebBaseLoader(
    web_paths=("https://en.wikipedia.org/wiki/Cricket",),
    bs_kwargs={"parse_only": SoupStrainer("p")}  # only paragraph text
)

documents = loader.load()
print(documents[0].page_content[:500])
```

> `SoupStrainer("p")` filters only `<p>` tags — skips navigation menus, headers, and footers. Very useful for clean text extraction.

---

## Part 2: Text Splitters

After loading, documents are often too large. We split them into **chunks**.

---

### CharacterTextSplitter — Basic Splitter

Splits text at a single separator character (space, newline, etc.)

**From your code (`splitters/CharacterTextSplitter.py`)**
```python
from langchain_text_splitters import CharacterTextSplitter

splitter = CharacterTextSplitter(
    separator=" ",      # split on spaces
    chunk_size=200,     # max 200 characters per chunk
    chunk_overlap=50    # 50-char overlap between consecutive chunks
)

chunks = splitter.split_text(text)
```

> `chunk_overlap=50` is important — it ensures context isn't lost at chunk boundaries. The last 50 characters of one chunk appear at the start of the next.

---

### RecursiveCharacterTextSplitter — Smart Splitter (Recommended)

Tries separators in order: `\n\n` → `\n` → ` ` → character-by-character.  
This keeps paragraphs and sentences together as much as possible.

**From your code (`splitters/RecursiveCharacterTextSplitter.py`)**
```python
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30
)

chunks = splitter.split_text(text)
```

---

## Part 3: Full Pipeline (Load → Split)

**From your code (`Full-Pipeline.py`)**
```python
# Step 1 — Load PDF
loader = PyPDFLoader("Data/1.pdf")
documents = loader.load()
print(f"Loaded {len(documents)} pages")

# Step 2 — Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)
print(f"Total chunks created: {len(chunks)}")

# See a sample chunk
print(chunks[0].page_content[:300])
print(chunks[0].metadata)   # {'source': '...', 'page': 0}
```

---

## Comparison: CharacterTextSplitter vs RecursiveCharacterTextSplitter

| Feature | CharacterTextSplitter | RecursiveCharacterTextSplitter |
|---------|-----------------------|-------------------------------|
| Split strategy | Single separator | Tries `\n\n` → `\n` → ` ` → char |
| Sentence integrity | May cut mid-sentence | Tries to keep sentences whole |
| Recommended for | Simple text | ✅ PDFs, docs, any structured text |
| Control | More manual | Smarter defaults |

---

## Important Keywords
| Keyword | Meaning |
|---------|---------|
| `Document` | LangChain object: `.page_content` + `.metadata` |
| `page_content` | The actual text content of the document/chunk |
| `metadata` | Dict with info like `source`, `page`, `row` |
| `chunk_size` | Maximum characters per chunk |
| `chunk_overlap` | Characters shared between consecutive chunks |
| `PyPDFLoader` | Loads PDF files, one page = one Document |
| `CSVLoader` | Loads CSV files, one row = one Document |
| `WebBaseLoader` | Loads web pages as Documents |
| `BeautifulSoup` | HTML parser used by WebBaseLoader internally |

---

## Beginner-Friendly Summary
Think of it like processing a textbook:
1. **Loader** = Scanner that digitizes each page of the book
2. **Text Splitter** = Scissors that cut pages into index cards
3. **chunk_size** = How big each index card is
4. **chunk_overlap** = Each card repeats the last line of the previous card so you don't lose context

Then later, you search those index cards (chunks) to find relevant answers. 📚
