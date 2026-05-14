from langchain_core.prompts import ChatPromptTemplate
from langchain_groq import ChatGroq

chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are an expert {role}. Always answer in {language}."),
    ("human", "{question}")
])

chain = prompt | chat

response = chain.invoke({
    "role": "Doctor",
    "stype":"technical",
    "language": "English",
    "question": "What causes fever?"
})

print(response.content)
