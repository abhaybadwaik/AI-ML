from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_groq import ChatGroq

# Model (used for chat + summarization)
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

# Store
store = {}
summary_store = {}

# Function to summarize conversation
def summarize(messages):
    text = "\n".join([m.content for m in messages])
    summary_prompt = f"""
You are a strict information extractor.

ONLY include facts that are explicitly stated by the user.
DO NOT add explanations.
DO NOT add definitions.
DO NOT infer or assume anything.
DO NOT include any information not directly mentioned.

Return output in short bullet points only.

Conversation:
{text}
"""
    return chat.invoke(summary_prompt).content

# Custom memory (summary-based)
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
        summary_store[session_id] = ""
    
    history = store[session_id]

    # If too long → summarize
    if len(history.messages) > 4:
        summary = summarize(history.messages)
        summary_store[session_id] = summary
        
        # Replace full history with summary
        history.messages = [
            # keep summary as a system message
            type(history.messages[0])(content=summary)
        ]

    return history

# Attach memory
chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

config = {"configurable": {"session_id": "user1"}}

# Multiple turns
chain_with_memory.invoke(
    {"input": "Hi, I am Pratik, a software developer from Hyderabad."},
    config=config
)
chain_with_memory.invoke(
    {"input": "I have 3 years of experience in Python and React."},
    config=config
)
chain_with_memory.invoke(
    {"input": "I am currently learning LangChain and AI development."},
    config=config
)
chain_with_memory.invoke(
    {"input": "My goal is to become an AI engineer in the next 6 months."},
    config=config
)

# Show summary
print("=== SUMMARY MEMORY ===")
print(summary_store["user1"])

print()

# Ask question
response = chain_with_memory.invoke(
    {"input": "Can you give me a learning plan based on what I told you?"},
    config=config
)

print("AI:", response.content)