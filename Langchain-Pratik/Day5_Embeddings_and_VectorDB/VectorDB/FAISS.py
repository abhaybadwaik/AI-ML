from langchain_groq import ChatGroq
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)

embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Sample documents — imagine these came from a PDF or CSV
documents = [
    Document(page_content="Virat Kohli is an Indian cricketer known for his aggressive batting.", metadata={"source": "cricket.pdf", "page": 1}),
    Document(page_content="Rohit Sharma is the captain of the Indian cricket team.", metadata={"source": "cricket.pdf", "page": 1}),
    Document(page_content="Python is a popular programming language used in data science.", metadata={"source": "tech.pdf", "page": 1}),
    Document(page_content="LangChain is a framework for building AI applications.", metadata={"source": "tech.pdf", "page": 2}),
    Document(page_content="The Eiffel Tower is located in Paris, France.", metadata={"source": "travel.pdf", "page": 1}),
    Document(page_content="Hyderabad is known for its biryani and the Charminar monument.", metadata={"source": "travel.pdf", "page": 2}),
]

# Step 1 — Create FAISS vector store from documents
# This converts all documents to vectors and stores them
print("Creating FAISS vector store...")
vectorstore = FAISS.from_documents(documents, embeddings_model)
print("Vector store created successfully!")
print()

# Step 2 — Search by meaning (semantic search)
query = "Who is the captain of India?"
print(f"Query: {query}")
print()

results = vectorstore.similarity_search(query, k=2)  # k = top 2 results

for i, doc in enumerate(results):
    print(f"Result {i+1}:")
    print(f"Content: {doc.page_content}")
    print(f"Metadata: {doc.metadata}")
    print()