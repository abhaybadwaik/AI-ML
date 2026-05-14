from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters  import RecursiveCharacterTextSplitter

chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)

# Step 1 — Load PDF
print("Step 1: Loading PDF...")
loader = PyPDFLoader("C:/Users/Desk-68/Desktop/Agents/Langchain/Data/1.pdf")
documents = loader.load()
print(f"Loaded {len(documents)} pages")
print()

# Step 2 — Split into chunks
print("Step 2: Splitting into chunks...")
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(documents)
print(f"Total chunks created: {len(chunks)}")
print()

# Step 3 — See sample chunks
print("=== Sample Chunk 1 ===")
print("Content:", chunks[0].page_content[:300])
print("Metadata:", chunks[0].metadata)
print()

print("=== Sample Chunk 2 ===")
print("Content:", chunks[1].page_content[:300])
print("Metadata:", chunks[1].metadata)