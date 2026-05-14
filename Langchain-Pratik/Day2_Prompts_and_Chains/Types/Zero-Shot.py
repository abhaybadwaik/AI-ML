from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate

chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)

# ---- ZERO SHOT ----
# No examples, just ask directly
zero_shot_prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify sentiment as Positive, Negative, or Neutral only."),
    ("human", "{text}")
])

chain = zero_shot_prompt | chat

response = chain.invoke({"text": "The food was okay but service was terrible."})
print("Zero-Shot Output:", response.content)