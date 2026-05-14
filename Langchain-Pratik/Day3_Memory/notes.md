# Day 3 — Conversation Memory

## What is the concept?
Memory in LangChain allows a chatbot to **remember previous messages** across multiple turns of a conversation. Without memory, every question you ask is treated as brand new — the AI has no idea what was said before.

## Why do we use it?
A chatbot without memory is frustrating — you'd have to repeat your name, context, and history every single time. Memory makes conversations feel natural and intelligent.

## Real-Life Use Cases
- Customer support bot that remembers your order number throughout the chat
- AI tutor that recalls what topics you've already covered
- HR chatbot (like your project) that remembers your name, role, and questions
- Personal assistant that learns your preferences over a session

---

## The 4 Memory Types You Learned

---

### Type 1: ConversationBufferMemory
**Stores the entire conversation history** — every single message, from start to finish.

**When to use:** Short conversations where you need perfect recall.  
**Problem:** Gets expensive/slow with very long chats (too many tokens).

**From your code (`1ConversationBufferMemory.py`)**
```python
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.chat_history import InMemoryChatMessageHistory

store = {}

def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]

chain_with_memory = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="history"
)

config = {"configurable": {"session_id": "user1"}}

# Turn 1
chain_with_memory.invoke({"input": "Hi, my name is Pratik from Hyderabad."}, config=config)
# Turn 2
chain_with_memory.invoke({"input": "My favourite player is Kohli."}, config=config)
# Turn 3
chain_with_memory.invoke({"input": "What do you know about me so far?"}, config=config)
# AI remembers EVERYTHING from Turn 1 and Turn 2!
```

---

### Type 2: ConversationBufferWindowMemory
**Keeps only the last K exchanges** — older messages are dropped automatically.

**When to use:** Medium-length chats where only recent context matters.  
**Example:** Customer service — only the last 2 replies are needed.

**From your code (`2ConversationBufferWindowMemory.py`)**
```python
def get_session_history(session_id: str):
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    history = store[session_id]
    # Keep only last 2 exchanges (4 messages: human + AI per exchange)
    history.messages = history.messages[-4:]
    return history
```
> Turn 1: "My name is Pratik" ✅ remembered  
> Turn 4: "What is my name?" ❌ May be forgotten if window slid past Turn 1

---

### Type 3: ConversationSummaryMemory
**Summarizes the conversation** when it gets too long, then keeps the summary instead of raw messages.

**When to use:** Long conversations where you need key facts but not word-for-word history.

**From your code (`3ConversationSummaryMemory.py`)**
```python
def summarize(messages):
    text = "\n".join([m.content for m in messages])
    summary_prompt = f"""
You are a strict information extractor.
ONLY include facts explicitly stated.
Return bullet points only.
Conversation: {text}
"""
    return chat.invoke(summary_prompt).content

def get_session_history(session_id: str):
    history = store[session_id]
    # If history is too long → summarize and replace
    if len(history.messages) > 4:
        summary = summarize(history.messages)
        history.messages = [type(history.messages[0])(content=summary)]
    return history
```
> After 5+ turns, history becomes: "• Pratik is a software developer from Hyderabad  
> • Has 3 years Python + React experience  
> • Goal: become AI engineer in 6 months"

---

### Type 4: ConversationSummaryBufferMemory (Hybrid — Best of Both)
**Keeps recent messages raw + summarizes older ones** — the smartest memory approach.

**When to use:** Production chatbots, long-running assistants.

**From your code (`4ConversationSummaryBufferMemory.py`)**
```python
MAX_MESSAGES = 6

def get_session_history(session_id: str):
    history = store[session_id]
    if len(history.messages) > MAX_MESSAGES:
        old_messages = history.messages[:-MAX_MESSAGES]
        summary = summarize(old_messages)
        # Keep: [summary] + last 6 recent messages
        history.messages = [
            type(history.messages[0])(content=summary)
        ] + history.messages[-MAX_MESSAGES:]
    return history
```

---

## Comparison Table
| Memory Type | Stores | Best For | Weakness |
|-------------|--------|----------|----------|
| Buffer | All messages | Short chats | Token limit hit fast |
| Window (k=2) | Last K turns | Medium chats | Forgets old context |
| Summary | Compressed summary | Long chats | May lose detail |
| Summary Buffer | Summary + recent raw | Production apps | More complex logic |

---

## Important Keywords
| Keyword | Meaning |
|---------|---------|
| `RunnableWithMessageHistory` | Wrapper that injects memory into any chain |
| `InMemoryChatMessageHistory` | Simple in-RAM message store |
| `MessagesPlaceholder` | Placeholder in prompt where history is injected |
| `session_id` | Unique ID per user/conversation |
| `store` | Python dict that holds all session histories |
| `configurable` | Config dict passed to `invoke()` to identify session |

---

## Beginner-Friendly Summary
Think of memory types like note-taking styles:
- **Buffer** = Write down every single word said (transcript)
- **Window** = Only keep the last 2 pages of notes (sticky notes)
- **Summary** = Highlight the key points in bullet form (notes summary)
- **Summary Buffer** = Bullet summary of old + full notes of last 6 messages (smartest approach) ✅
