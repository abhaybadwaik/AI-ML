from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_groq import ChatGroq
from langchain_core.prompts import MessagesPlaceholder


# Create model
chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)

# Prompt

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),   # ✅ ADD THIS
    ("human", "{input}")
])

# Store memory for each session
store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

# Create chain with memory
chain = prompt | chat

chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

# Session ID (important)
config = {"configurable": {"session_id": "user1"}}

# Turn 1
response = chain_with_memory.invoke(
    {"input": "Hi, my name is Pratik and I work in Hyderabad."},
    config=config
)
print("AI:", response.content)
print()

# Turn 2
response = chain_with_memory.invoke(
    {"input": "I love cricket and my favourite player is Kohli."},
    config=config
)
print("AI:", response.content)
print()

# Turn 3
response = chain_with_memory.invoke(
    {"input": "What do you know about me so far?"},
    config=config
)
print("AI:", response.content)
print()

# View memory
print("=== MEMORY CONTENTS ===")
print(store["user1"].messages)