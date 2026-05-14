# 🦜 LangChain Learning Journal — Complete 9-Day Course

> **Your personal, organized LangChain learning path** — built from your real project files, code, and practice work.

---

## 📁 Folder Structure

```
LangchainLearning/
│
├── Day1_LangChain_Intro/          ← What is LangChain? Big picture + setup
│   └── notes.md
│
├── Day2_Prompts_and_Chains/       ← PromptTemplate, ChatPromptTemplate, Chains
│   ├── PromptTemplate.py
│   ├── ChatPromptTemplate.py
│   ├── Chain/
│   │   ├── Basic-Chain.py
│   │   └── Sequential-Chain.py
│   ├── Types/
│   │   ├── Zero-Shot.py
│   │   ├── Few-Shot.py
│   │   └── Few-Shot-2.py
│   └── notes.md
│
├── Day3_Memory/                   ← Conversation memory types
│   ├── 1ConversationBufferMemory.py
│   ├── 2ConversationBufferWindowMemory.py
│   ├── 3ConversationSummaryMemory.py
│   ├── 4ConversationSummaryBufferMemory.py
│   └── notes.md
│
├── Day4_Document_Loaders/         ← PDF, CSV, Web loaders + Text Splitters
│   ├── Document/
│   │   ├── PDFs.py
│   │   ├── CSV.py
│   │   └── Web.py
│   ├── Splitters/
│   │   ├── CharacterTextSplitter.py
│   │   └── RecursiveCharacterTextSplitter.py
│   ├── Full-Pipeline.py
│   └── notes.md
│
├── Day5_Embeddings_and_VectorDB/  ← HuggingFace Embeddings + FAISS + Chroma
│   ├── Embeddings/
│   │   ├── Embeddings.py
│   │   └── similarity.py
│   ├── VectorDB/
│   │   ├── FAISS.py
│   │   ├── chroma.py
│   │   └── faiss_similarity.py
│   ├── Full-Pipeline.py
│   └── notes.md
│
├── Day6_RAG_Pipeline/             ← Full RAG with contextual retrieval + memory
│   ├── agent.py
│   ├── agent1.py
│   └── notes.md
│
├── Day7_Streaming/                ← Real-time streaming responses
│   ├── Streaming.py
│   ├── Streaming_chain.py
│   └── notes.md
│
├── Day8_Async_Parallel/           ← Async + parallel LLM calls with asyncio
│   ├── async_parallel.py
│   └── notes.md
│
└── Day9_Agents_and_Tools/         ← ReAct Agents + Database + REST API Tools
    ├── Database.py
    ├── REST_API.py
    ├── combine.py
    └── notes.md
```

---

## 🗺️ Learning Roadmap

| Day | Topic | Key Concepts | Your Files |
|-----|-------|-------------|-----------|
| 1 | **LangChain Intro** | LLM, Chain, Agent, RAG, Groq | Setup only |
| 2 | **Prompts & Chains** | PromptTemplate, ChatPromptTemplate, LCEL `\|`, Zero-Shot, Few-Shot | 7 files |
| 3 | **Memory** | Buffer, Window, Summary, SummaryBuffer | 4 files |
| 4 | **Document Loaders** | PyPDFLoader, CSVLoader, WebBaseLoader, Text Splitters | 7 files |
| 5 | **Embeddings & VectorDB** | HuggingFace, cosine similarity, FAISS, Chroma | 6 files |
| 6 | **RAG Pipeline** | Contextual retrieval, ConversationSummaryBufferMemory, full RAG | 2 files |
| 7 | **Streaming** | `stream()`, `astream()`, `flush=True` | 2 files |
| 8 | **Async & Parallel** | `asyncio`, `await`, `ainvoke()`, `gather()` | 1 file |
| 9 | **Agents & Tools** | `@tool`, ReAct, `create_react_agent`, AgentExecutor, REST API, SQLite | 3 files |

---

## 🔑 Key Libraries Used

```
langchain-core          — Core LangChain: prompts, chains, parsers
langchain-community     — Loaders, vector stores, HuggingFace embeddings
langchain-groq          — Groq LLM provider (ChatGroq)
langchain-text-splitters — CharacterTextSplitter, RecursiveCharacterTextSplitter
langchain               — Memory, Agents (legacy + modern)
faiss-cpu               — FAISS vector database
chromadb                — Chroma persistent vector database
sentence-transformers   — HuggingFace embedding model
scikit-learn            — cosine_similarity calculation
requests                — REST API calls (weather)
sqlite3                 — Python built-in SQLite database
asyncio                 — Python built-in async library
```

---

## ⚡ The Full RAG Pipeline (What You Built)

```
📄 PDF / CSV / Website
        ↓
[Document Loader]         Day 4
        ↓
[Text Splitter]           Day 4  (chunk_size=500, overlap=50)
        ↓
[Embedding Model]         Day 5  (all-MiniLM-L6-v2)
        ↓
[Vector Store]            Day 5  (FAISS or Chroma)
        ↓
[Retriever]               Day 6  (semantic search, top-k)
        ↓
[Contextualize Question]  Day 6  (rewrite vague follow-ups)
        ↓
[LLM + Context]           Day 2  (ChatGroq + prompt)
        ↓
[Memory]                  Day 3  (ConversationSummaryBuffer)
        ↓
Final Answer ✅
```

---

## 🚀 Quick Reference — Most Used Patterns

### Basic Chain
```python
chain = prompt | chat | StrOutputParser()
response = chain.invoke({"question": "..."})
```

### With Memory
```python
chain_with_memory = RunnableWithMessageHistory(chain, get_session_history, ...)
chain_with_memory.invoke({"input": "..."}, config={"configurable": {"session_id": "u1"}})
```

### RAG Search
```python
vectorstore = FAISS.from_documents(chunks, embeddings_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
results = retriever.invoke("your question")
```

### Streaming
```python
for chunk in chain.stream({"question": "..."}):
    print(chunk, end="", flush=True)
```

### Async Parallel
```python
tasks = [chain.ainvoke({"question": q}) for q in questions]
results = await asyncio.gather(*tasks)
```

### Agent with Tools
```python
agent = create_react_agent(llm=chat, tools=[tool1, tool2], prompt=react_prompt)
executor = AgentExecutor(agent=agent, tools=tools, verbose=True)
result = executor.invoke({"input": "complex question"})
```

---

## 📚 Read the `notes.md` in Each Folder!

Every day folder has a `notes.md` file with:
- ✅ What the concept is
- ✅ Why you use it
- ✅ Real-life use cases
- ✅ Code examples from YOUR actual files
- ✅ Comparison tables
- ✅ Beginner-friendly analogies
- ✅ Important keywords glossary

---

*Happy learning! You've covered a full professional LangChain curriculum. 🎓*
