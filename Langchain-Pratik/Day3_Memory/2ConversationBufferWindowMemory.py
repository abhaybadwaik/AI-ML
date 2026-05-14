from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_groq import ChatGroq

# Model
chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)

# Prompt with history
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chain = prompt | chat

# Store memory
store = {}

# ✅ Window memory (k=2)
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    
    history = store[session_id]
    
    # Keep only last 2 exchanges (4 messages: human+AI)
    history.messages = history.messages[-4:]
    
    return history

# Add memory to chain
chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

config = {"configurable": {"session_id": "user1"}}

# Turn 1
res = chain_with_memory.invoke({"input": "My name is Pratik."}, config=config)
print("Turn 1 - AI:", res.content)

# Turn 2
res = chain_with_memory.invoke({"input": "I am from Hyderabad."}, config=config)
print("Turn 2 - AI:", res.content)

# Turn 3
res = chain_with_memory.invoke({"input": "I love cricket."}, config=config)
print("Turn 3 - AI:", res.content)

# Turn 4 (name may be forgotten)
res = chain_with_memory.invoke({"input": "What is my name?"}, config=config)
print("Turn 4 - AI:", res.content)

print("\n=== MEMORY CONTENTS (last 2 exchanges) ===")
print(store["user1"].messages)