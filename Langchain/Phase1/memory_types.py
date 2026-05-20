"""
Phase 1 · Lesson 5 — Memory
Real-world scenario: TechStore support chatbot with memory

WHAT WE ARE TRYING TO ACHIEVE:
In Lesson 1 we managed conversation history manually.
Memory classes do this automatically.

Three types:
ChatMessageHistory             → stores full history automatically
With manual trimming           → stores only last N messages
With summarization             → summarizes old messages to save tokens
"""

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.chat_message_histories import ChatMessageHistory

load_dotenv()

llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=300)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful support agent for TechStore."),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

chain = prompt | llm | StrOutputParser()

# conversations to simulate
conversations = [
    "Hi, my laptop hasn't arrived yet.",
    "My order number is ORDER-9821.",
    "I need it urgently for work.",
    "What are my options?",
]


# ── 1. ConversationBufferMemory ───────────────────────────────
# Stores full history — every message kept
# Use when: short conversations, demos
# Problem: grows forever, hits token limit in long conversations

print("=== ConversationBufferMemory ===")
print("Stores full history — every message kept")
print()

buffer_history = ChatMessageHistory()   # stores all messages automatically

for user_input in conversations:
    # get full history
    history = buffer_history.messages

    # invoke chain
    response = chain.invoke({
        "input": user_input,
        "chat_history": history,
    })

    # save to memory automatically
    buffer_history.add_user_message(user_input)
    buffer_history.add_ai_message(response)

    print(f"Customer: {user_input}")
    print(f"Bot     : {response}")
    print()

# show what memory stored
print("Memory contents:")
for msg in buffer_history.messages:
    role = "Human" if isinstance(msg, HumanMessage) else "AI"
    print(f"  {role}: {msg.content[:60]}...")
print()


# ── 2. Window Memory ──────────────────────────────────────────
# Stores only last N messages — older ones dropped automatically
# Use when: limit context size, save tokens
# Real world: most common in production chatbots

print("=== Window Memory (last 2 exchanges only) ===")
print("Stores only last K messages — older ones dropped")
print()

window_history = ChatMessageHistory()
k = 2   # keep only last 2 exchanges = 4 messages

for user_input in conversations:
    # get only last k exchanges
    all_messages = window_history.messages
    history = all_messages[-(k * 2):]   # last k*2 messages (human+ai pairs)

    response = chain.invoke({
        "input": user_input,
        "chat_history": history,
    })

    window_history.add_user_message(user_input)
    window_history.add_ai_message(response)

    print(f"Customer: {user_input}")
    print(f"Bot     : {response}")
    print()

# show only last k exchanges
all_msgs = window_history.messages
print(f"Memory contents (only last {k} exchanges):")
for msg in all_msgs[-(k * 2):]:
    role = "Human" if isinstance(msg, HumanMessage) else "AI"
    print(f"  {role}: {msg.content[:60]}...")
print()


# ── 3. Summary Memory ─────────────────────────────────────────
# Summarizes old messages instead of storing all of them
# Use when: very long conversations, production apps
# Real world: best for production — never hits token limit

print("=== Summary Memory ===")
print("Summarizes old messages — never hits token limit")
print()

summary_history = ChatMessageHistory()
summary = ""   # running summary of old messages

summary_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful support agent for TechStore."),
    ("system", "Summary of conversation so far: {summary}"),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

summary_chain = summary_prompt | llm | StrOutputParser()

for user_input in conversations:
    # use summary + last 2 messages as context
    recent = summary_history.messages[-2:] if len(summary_history.messages) >= 2 else summary_history.messages

    response = summary_chain.invoke({
        "input": user_input,
        "chat_history": recent,
        "summary": summary,
    })

    summary_history.add_user_message(user_input)
    summary_history.add_ai_message(response)

    # update summary after every 2 exchanges
    if len(summary_history.messages) % 4 == 0:
        summarize_prompt = f"""
Summarize this conversation in 2 lines:
{chr(10).join([f"{type(m).__name__}: {m.content}" for m in summary_history.messages])}
"""
        summary = llm.invoke([HumanMessage(content=summarize_prompt)]).content

    print(f"Customer: {user_input}")
    print(f"Bot     : {response}")
    print()

print(f"Final Summary: {summary if summary else 'Not generated yet — need more messages'}")
print()


# ── Summary ───────────────────────────────────────────────────
print("""
=== When to use which memory ===
Buffer Memory  → store everything, short conversations, demos
Window Memory  → keep last N messages, save tokens, production bots
Summary Memory → summarize old messages, very long conversations

Key point:
  All three use MessagesPlaceholder to inject history into prompt
  All three use add_user_message() and add_ai_message() to save
  You never manually manage the conversation list anymore
""")