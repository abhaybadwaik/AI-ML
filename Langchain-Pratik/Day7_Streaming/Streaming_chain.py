from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{question}")
])

parser = StrOutputParser()
chain = prompt | chat | parser

print("=== STREAMING WITH CHAIN ===")
print()

for chunk in chain.stream({"question": "Tell me 5 interesting facts about India."}):
    print(chunk, end="", flush=True)

print()