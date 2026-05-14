from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)

# Without streaming — waits for full response
print("=== WITHOUT STREAMING ===")
response = chat.invoke("Explain what is machine learning in 5 lines.")
print(response.content)
print()

# With streaming — prints word by word as it arrives
print("=== WITH STREAMING ===")
for chunk in chat.stream("Explain what is machine learning in 5 lines."):
    print(chunk.content, end="", flush=True)
print()

