from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)

embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# Step 1 — Load PDF
print("Step 1: Loading PDF...")
loader = PyPDFLoader("C:/Users/Desk-68/Desktop/Agents/Langchain/Data/1.pdf")
documents = loader.load()
print(f"Loaded {len(documents)} pages")

# Step 2 — Split into chunks
print("Step 2: Splitting into chunks...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)
chunks = splitter.split_documents(documents)
print(f"Total chunks: {len(chunks)}")

# Step 3 — Create vector store
print("Step 3: Creating vector store...")
vectorstore = FAISS.from_documents(chunks, embeddings_model)
print("Vector store ready!")
print()

# Step 4 — Search
queries = [
    "What is insurance?",
"What is the meaning of premium?",
"What is meant by making a loss whole?",
"Who are the insured and insurer?",
"What is a claim in insurance?"
]

for query in queries:
    print(f"Query: {query}")
    results = vectorstore.similarity_search(query, k=1)
    print(f"Best match: {results[0].page_content[:200]}")
    print(f"Source: Page {results[0].metadata['page'] + 1}")
    print()

