from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_groq import ChatGroq

chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "Tell me one interesting fact about {topic}.")
])

# StrOutputParser converts AIMessage object to plain string
parser = StrOutputParser()

# Chain: prompt → model → parser
chain = prompt | chat | parser

response = chain.invoke({"topic": "black holes"})
print(response)
print(type(response))

