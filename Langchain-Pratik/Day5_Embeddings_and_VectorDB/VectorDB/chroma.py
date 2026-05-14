from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

# -----------------------------
# 1. Embedding Model
# -----------------------------
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------
# 2. Sample Documents
# -----------------------------
documents = [
    Document(
        page_content="Hyderabad is famous for biryani and Charminar.",
        metadata={"source": "travel.pdf", "page": 1}
    ),
    Document(
        page_content="Delhi is the capital of India and known for historical monuments.",
        metadata={"source": "travel.pdf", "page": 2}
    ),
    Document(
        page_content="Mumbai is the financial capital of India.",
        metadata={"source": "travel.pdf", "page": 3}
    ),
    Document(
        page_content="Chroma is a vector database used for storing embeddings.",
        metadata={"source": "tech.pdf", "page": 1}
    ),
]

# -----------------------------
# 3. Create Chroma DB
# -----------------------------
print("\n🔹 Creating Chroma Vector Store...\n")

vectorstore_chroma = Chroma.from_documents(
    documents=documents,
    embedding=embeddings_model,
    persist_directory="chroma_db"   # saved on disk
)

print("✅ Chroma vector store created and saved!\n")

# -----------------------------
# 4. Query
# -----------------------------
query = "What is Hyderabad famous for?"

print("🔍 Query:", query)
print("\n🔎 Searching...\n")

# -----------------------------
# 5. Similarity Search
# -----------------------------
results = vectorstore_chroma.similarity_search(query, k=2)

# -----------------------------
# 6. Print Results
# -----------------------------
for i, doc in enumerate(results, 1):
    print(f"Result {i}")
    print("Content:", doc.page_content)
    print("Metadata:", doc.metadata)
    print("-" * 50)