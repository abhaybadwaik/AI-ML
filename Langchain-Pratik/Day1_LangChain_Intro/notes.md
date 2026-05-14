# Day 1 — Introduction to LangChain

## What is the concept?
LangChain is an open-source Python framework that helps you build AI-powered applications by connecting Large Language Models (LLMs) with external data, tools, APIs, databases, and memory systems.

## Why do we use it?
Without LangChain, you'd have to manually wire together API calls, prompt formatting, memory management, and output parsing. LangChain provides ready-made building blocks so you can focus on your app logic instead of low-level plumbing.

## Small Explanation
LangChain wraps an LLM (like GPT-4 or Llama) and adds powerful layers on top:
- **Prompts** — structured templates to control what you ask the AI
- **Chains** — connect multiple steps (load → ask → parse → save)
- **Memory** — remember past conversations
- **Agents** — let the AI decide what tools to use
- **Document Loaders** — read PDFs, CSVs, websites
- **Vector Stores** — store and search knowledge semantically

## Real-Life Use Cases
- Customer support chatbot that reads your company's FAQ documents
- AI assistant that queries your database and answers in plain English
- Resume screener that reads PDFs and ranks candidates
- Code review bot that remembers previous feedback in a session
- Research assistant that searches the web and summarizes answers

## Important Keywords
| Term | Meaning |
|------|---------|
| `LLM` | Large Language Model (the AI brain, e.g. Llama, GPT) |
| `Chain` | A sequence of steps linked together |
| `Prompt` | The structured message sent to the AI |
| `Agent` | AI that can pick and use tools to solve a task |
| `RAG` | Retrieval Augmented Generation — search docs, then answer |
| `Vector Store` | Database that stores embeddings for semantic search |
| `Embedding` | A number-vector that captures the meaning of text |
| `Groq` | Fast LLM inference provider used in your projects |

## Your Setup (from your code files)
```python
# Your LLM of choice — Groq with Llama 3
from langchain_groq import ChatGroq

chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="your_api_key"
)

# Simple test
response = chat.invoke("What is LangChain?")
print(response.content)
```

## LangChain Core Architecture (Big Picture)
```
Your Question
     ↓
[Prompt Template]      ← formats your question
     ↓
[LLM (Groq/Llama)]    ← processes and generates answer
     ↓
[Output Parser]        ← converts AI output to clean string
     ↓
Final Answer
```

## Learning Progression in Your Project
```
Day 1  → LangChain basics + setup
Day 2  → Prompts (PromptTemplate, ChatPromptTemplate, Few-Shot)
Day 3  → Memory (Buffer, Window, Summary)
Day 4  → Document Loaders + Text Splitters
Day 5  → Embeddings + Vector Databases (FAISS, Chroma)
Day 6  → Full RAG Pipeline (agent.py, agent1.py)
Day 7  → Streaming responses
Day 8  → Async + Parallel calls
Day 9  → Agents with Tools (Database, REST API, combined)
```

## Beginner-Friendly Explanation
Think of LangChain like a kitchen:
- **LLM** = the chef (does the smart work)
- **PromptTemplate** = the recipe (tells the chef what to cook and how)
- **Chain** = the assembly line (prep → cook → plate → serve)
- **Memory** = the chef's notepad (remembers what you ordered before)
- **Agent** = a smart chef who can decide what tool to pick from the kitchen

You assemble these pieces and LangChain connects them all together. 🍳
