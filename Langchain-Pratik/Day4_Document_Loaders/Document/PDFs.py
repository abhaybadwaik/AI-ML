from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader

chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)

# Load a PDF file
loader = PyPDFLoader("C:/Users/Desk-68/Desktop/Agents/Langchain/Data/1.pdf")
documents = loader.load()

# See what we got
print("Total pages loaded:", len(documents))
print()
print("=== First Page Content (first 300 chars) ===")
print(documents[0].page_content[:300])
print()
print("=== Metadata of first page ===")
print(documents[0].metadata)