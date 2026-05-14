# Day 5 — Embeddings & Vector Databases (FAISS & Chroma)

## What is the concept?
**Embeddings** convert text into numerical vectors (lists of numbers) that capture the *meaning* of the text.  
**Vector Databases** store these vectors and allow you to search by meaning (semantic search) — not just by keywords.

## Why do we use it?
Traditional databases match exact keywords. If you search "cricket captain", a keyword database won't find "leader of Indian team". Vector databases **understand meaning** — they return results that are semantically similar, even if the words are different.

## Real-Life Use Cases
- Google's search engine (semantic search)
- Netflix/Spotify recommendation engine
- Chatbot that searches company documents for relevant answers (RAG)
- Resume screening: "find developers with cloud experience" → returns results even if résumé says "AWS, Azure"
- Legal search: "contract termination clause" finds relevant sections across thousands of documents

---

## Part 1: Embeddings

### What is an Embedding?
A sentence like `"I love playing cricket"` becomes a list of 384 numbers:
```
[0.0823, -0.2341, 0.1192, ... (384 numbers total)]
```
These numbers encode the *meaning* of the sentence. Similar sentences have similar vectors.

**From your code (`Embeddings/Embeddings.py`)**
```python
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

sentence = "I love playing cricket"
vector = embeddings_model.embed_query(sentence)

print("Vector length:", len(vector))   # 384
print("First 10 numbers:", vector[:10])
```

---

### Cosine Similarity — Measuring Meaning Distance

**From your code (`Embeddings/similarity.py`)**
```python
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

sentences = [
    "I love playing cricket",         # base sentence
    "Cricket is my favourite sport",  # very similar → high score
    "I enjoy watching football",      # somewhat similar → medium score
    "Python is a programming language" # unrelated → low score
]

vectors = embeddings_model.embed_documents(sentences)
base_vector = np.array(vectors[0]).reshape(1, -1)

for i in range(1, len(sentences)):
    other_vector = np.array(vectors[i]).reshape(1, -1)
    score = cosine_similarity(base_vector, other_vector)[0][0]
    print(f"'{sentences[i]}' → similarity: {score:.4f}")

# Expected output:
# 'Cricket is my favourite sport' → similarity: 0.8 (high)
# 'I enjoy watching football'     → similarity: 0.5 (medium)
# 'Python is a programming language' → similarity: 0.1 (low)
```

> **Cosine similarity**: score between -1 and 1. The closer to 1, the more similar the meaning.

---

## Part 2: FAISS Vector Database

**Facebook AI Similarity Search** — fast, in-memory vector store. Great for development and smaller datasets.

**From your code (`DB/FAISS.py`)**
```python
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

documents = [
    Document(page_content="Virat Kohli is an Indian cricketer known for aggressive batting."),
    Document(page_content="Rohit Sharma is the captain of the Indian cricket team."),
    Document(page_content="Python is a popular programming language used in data science."),
    Document(page_content="LangChain is a framework for building AI applications."),
]

# Create FAISS store (converts all docs to vectors internally)
vectorstore = FAISS.from_documents(documents, embeddings_model)

# Semantic search
query = "Who is the captain of India?"
results = vectorstore.similarity_search(query, k=2)  # top 2 results

for doc in results:
    print(doc.page_content)
# Returns: Rohit Sharma doc (even though query doesn't say "Rohit")
```

---

### FAISS with Similarity Score

**From your code (`DB/faiss_similarity.py`)**
```python
results = vectorstore.similarity_search_with_score(query, k=3)

for doc, score in results:
    print(f"Score: {score:.4f}  → (lower = more relevant)")
    print(f"Content: {doc.page_content}")
```

> FAISS uses **distance** (not similarity) — lower distance = more relevant match.

---

## Part 3: Chroma Vector Database

**Chroma** is a vector store that **persists to disk** — data survives after your program ends. Better for production use.

**From your code (`DB/chroma.py`)**
```python
from langchain_community.vectorstores import Chroma

documents = [
    Document(
        page_content="Hyderabad is famous for biryani and Charminar.",
        metadata={"source": "travel.pdf", "page": 1}
    ),
    Document(
        page_content="Chroma is a vector database used for storing embeddings.",
        metadata={"source": "tech.pdf", "page": 1}
    ),
]

vectorstore_chroma = Chroma.from_documents(
    documents=documents,
    embedding=embeddings_model,
    persist_directory="chroma_db"  # saved on disk!
)

query = "What is Hyderabad famous for?"
results = vectorstore_chroma.similarity_search(query, k=2)

for doc in results:
    print(doc.page_content)
    print(doc.metadata)
```

> Your project already has a `chroma_db/` folder with saved data from your experiments!

---

## Part 4: Full RAG Pipeline (Load → Split → Embed → Store → Search)

**From your code (`Full-Pipeline.py`)**
```python
# Step 1: Load PDF
loader = PyPDFLoader("Data/1.pdf")
documents = loader.load()

# Step 2: Split into chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(documents)

# Step 3: Create vector store
vectorstore = FAISS.from_documents(chunks, embeddings_model)

# Step 4: Semantic search
queries = [
    "What is insurance?",
    "What is the meaning of premium?",
    "Who are the insured and insurer?"
]

for query in queries:
    results = vectorstore.similarity_search(query, k=1)
    print(f"Query: {query}")
    print(f"Best match: {results[0].page_content[:200]}")
    print(f"Source: Page {results[0].metadata['page'] + 1}")
```

---

## FAISS vs Chroma Comparison

| Feature | FAISS | Chroma |
|---------|-------|--------|
| Storage | In-memory (RAM) | Disk (persistent) |
| Speed | Very fast | Fast |
| Setup | Simple | Slightly more config |
| Persistence | ❌ Lost when program ends | ✅ Saved to disk |
| Best for | Development, prototypes | Production, larger datasets |
| Similarity score | Distance (lower = better) | Similarity (higher = better) |

---

## Important Keywords
| Keyword | Meaning |
|---------|---------|
| `Embedding` | Text converted to a numerical vector |
| `all-MiniLM-L6-v2` | HuggingFace model that creates 384-dim vectors |
| `embed_query()` | Convert single sentence → vector |
| `embed_documents()` | Convert list of sentences → list of vectors |
| `cosine_similarity` | Score 0→1 measuring how similar two vectors are |
| `FAISS` | Fast in-memory vector store by Facebook |
| `Chroma` | Persistent disk-based vector store |
| `similarity_search(query, k=2)` | Find top-k most relevant documents |
| `similarity_search_with_score()` | Same + returns distance score |
| `persist_directory` | Folder where Chroma saves its data |

---

## Beginner-Friendly Summary
Imagine a library where books are organized not by title, but by *topic similarity*:
- **Embedding** = GPS coordinates of each book's meaning
- **Vector DB** = Map of the library where similar books are placed close together
- **Similarity search** = "Find me books near these coordinates" — returns closest matches
- **FAISS** = Whiteboard with sticky notes (fast, but erased when you leave)
- **Chroma** = Filing cabinet with labels (stays there when you come back tomorrow)
