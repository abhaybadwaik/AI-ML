from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_groq import ChatGroq

# Model
chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)

# Prompt
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

chain = prompt | chat

# Stores
store = {}
summary_store = {}

MAX_MESSAGES = 6   # buffer size (~recent messages)

# Summarization function
def summarize(messages):
    text = "\n".join([m.content for m in messages])
    summary_prompt = f"""
You are a strict information extractor.
ONLY include facts explicitly mentioned.
Do NOT assume anything.

{text}
"""
    return chat.invoke(summary_prompt).content


# Hybrid memory function
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
        summary_store[session_id] = ""

    history = store[session_id]

    # If too many messages → summarize old ones
    if len(history.messages) > MAX_MESSAGES:
        old_messages = history.messages[:-MAX_MESSAGES]
        summary = summarize(old_messages)

        summary_store[session_id] = summary

        # Keep summary + recent messages
        history.messages = [
            type(history.messages[0])(content=summary)
        ] + history.messages[-MAX_MESSAGES:]

    return history


# Attach memory
chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

config = {"configurable": {"session_id": "user1"}}

# Conversations
chain_with_memory.invoke({"input": "I am Pratik, software developer from Hyderabad."}, config=config)
chain_with_memory.invoke({"input": "I have experience in Python, React, and SQL."}, config=config)
chain_with_memory.invoke({"input": "I am learning LangChain for AI development."}, config=config)
chain_with_memory.invoke({"input": "I want to build a RAG based chatbot for my company."}, config=config)
chain_with_memory.invoke({"input": "The chatbot should answer questions from our internal documents."}, config=config)
chain_with_memory.invoke({"input": "The documents are mostly PDFs and Word files."}, config=config)

# Output
print("=== SUMMARY BUFFER MEMORY ===")
print("Summary:", summary_store["user1"])
print("\nRecent Messages:", store["user1"].messages)