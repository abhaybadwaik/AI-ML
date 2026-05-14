from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
# -----------------------------
# 1. Create Embedding Model
# -----------------------------
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------
# 2. Sample Documents
# -----------------------------
documents = [
    Document(page_content="LangChain is a framework for building AI applications."),
    Document(page_content="Virat Kohli is an Indian cricketer known for aggressive batting."),
    Document(page_content="Rohit Sharma is the captain of the Indian cricket team."),
    Document(page_content="Python is widely used in AI, machine learning and data science."),
    Document(page_content="FAISS is a library used for efficient similarity search."),
]

# -----------------------------
# 3. Create Vector Store
# -----------------------------
print("\n🔹 Creating FAISS vector store...")
vectorstore = FAISS.from_documents(documents, embeddings)
print("✅ Vector store created!\n")

# -----------------------------
# 4. Query
# -----------------------------
query = "Tell me about the captain of India cricket team"

print("🔍 Query:", query)
print("\n🔎 Searching...\n")

# -----------------------------
# 5. Similarity Search with Score
# -----------------------------
results = vectorstore.similarity_search_with_score(query, k=3)

# -----------------------------
# 6. Display Results
# -----------------------------
for i, (doc, score) in enumerate(results, 1):
    print(f"Result {i}")
    print(f"Score (distance): {score:.4f}  → (lower = more relevant)")
    print(f"Content: {doc.page_content}")
    print("-" * 60)