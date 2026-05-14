# Day 6 — RAG Pipeline (Retrieval Augmented Generation)

## What is the concept?
**RAG (Retrieval Augmented Generation)** is a technique where the AI searches through your documents to find relevant information BEFORE generating an answer. Instead of relying only on its training data, the AI uses *your* data to answer questions.

## Why do we use it?
LLMs don't know about your company's policies, your private documents, or events after their training cutoff. RAG solves this by:
1. Searching your documents for relevant chunks
2. Passing those chunks as context to the LLM
3. LLM answers based only on YOUR data

## Real-Life Use Cases
- Company HR bot that answers policy questions from internal PDFs
- Legal assistant that answers from uploaded contracts
- Product support chatbot that reads from documentation
- Medical assistant that references clinical papers
- **Your project**: HR assistant that answers leave policy questions

---

## The Full RAG Architecture (from your `agent.py`)

```
User Question
     ↓
[Contextualize Prompt]  ← Rewrites vague question using chat history
     ↓                     "Can I carry them forward?" → "Can I carry annual leave forward?"
[LLM Contextualizer]
     ↓
[Retriever]             ← Searches vector store for top-k relevant chunks
     ↓
[Context Docs]          ← The actual policy text found
     ↓
[QA Prompt]             ← System: "Answer ONLY from context" + history + user question
     ↓
[LLM (Groq)]            ← Generates answer grounded in context
     ↓
[StrOutputParser]       ← Clean string output
     ↓
Final Answer
```

---

## Part 1: Basic RAG Chain (`agent.py`)

**Manually tracking chat history as a list**

```python
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from operator import itemgetter

# 1. Documents (your knowledge base)
documents = [
    Document(page_content="Annual leave: Employees get 20 days per year."),
    Document(page_content="Annual leave carry forward: Unused leave can be carried forward up to 5 days."),
    Document(page_content="Sick leave: Employees get 10 days per year."),
    Document(page_content="Sick leave carry forward: Sick leave cannot be carried forward."),
]

# 2. Vector store + retriever
vectorstore = FAISS.from_documents(documents, embeddings_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# 3. Contextualize prompt — rewrites vague follow-up questions
contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system", """Rewrite the question as a clear standalone question.
Examples:
- "Can I carry them forward?" → "Can I carry annual leave forward?"
- "What about sick leave?" → "How many days of sick leave do I get?"
Only return the rewritten question."""),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

contextualizer = contextualize_prompt | chat | StrOutputParser()

# 4. QA Prompt — answers only from context
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an HR assistant.
Answer ONLY from the context. If not found, say 'Not in policy'.
Context: {context}"""),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

# 5. Full RAG chain
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

rag_chain = (
    {
        "input": itemgetter("input"),
        "chat_history": itemgetter("chat_history"),
        "context": contextualizer | retriever | format_docs
    }
    | qa_prompt
    | chat
    | StrOutputParser()
)

# 6. Chat loop with manual history
chat_history = []

def chat_with_docs(question):
    response = rag_chain.invoke({
        "input": question,
        "chat_history": chat_history
    })
    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=response))
    return response

# Test
print(chat_with_docs("How many days of annual leave do I get?"))
print(chat_with_docs("Can I carry them forward?"))   # "them" resolved to "annual leave"
print(chat_with_docs("What about sick leave?"))
print(chat_with_docs("Can I carry that forward?"))   # "that" resolved to "sick leave"
```

---

## Part 2: RAG with ConversationSummaryBufferMemory (`agent1.py`)

**Uses LangChain's Memory object instead of manual list** — handles summarization automatically for long conversations.

```python
from langchain.memory import ConversationSummaryBufferMemory

memory = ConversationSummaryBufferMemory(
    llm=chat,
    max_token_limit=500,       # summarize after 500 tokens
    return_messages=True,      # return as message objects
    memory_key="chat_history"  # matches prompt placeholder
)

def chat_with_docs(question):
    # Load from memory
    history = memory.load_memory_variables({})["chat_history"]
    
    # Run chain
    response = rag_chain.invoke({"input": question, "chat_history": history})
    
    # Auto-save to memory (handles summarization internally)
    memory.save_context({"input": question}, {"output": response})
    
    return response
```

> **agent.py** = manual history (simpler, good for learning)  
> **agent1.py** = `ConversationSummaryBufferMemory` (production-ready, handles long conversations)

---

## The Contextualization Step — Key Insight

This is the smartest part of your RAG pipeline. Without it, follow-up questions fail:

| Turn | User asks | Without contextualization | With contextualization |
|------|-----------|--------------------------|------------------------|
| 1 | "How many annual leave days?" | Works fine | Works fine |
| 2 | "Can I carry **them** forward?" | Searches for "them" → no results | Rewrites to "Can I carry annual leave forward?" → finds answer |
| 3 | "What about sick leave?" | Ambiguous | Rewrites to "How many sick leave days?" → finds answer |
| 4 | "Can I carry **that** forward?" | Searches for "that" → fails | Rewrites to "Can sick leave be carried forward?" → finds answer |

---

## Important Keywords
| Keyword | Meaning |
|---------|---------|
| `RAG` | Retrieval Augmented Generation |
| `retriever` | Component that searches vector store for relevant docs |
| `as_retriever()` | Converts vector store into a retriever object |
| `search_kwargs={"k": 3}` | Return top 3 most relevant documents |
| `contextualize_prompt` | Prompt that rewrites vague questions into standalone ones |
| `format_docs()` | Helper that joins retrieved docs into one string |
| `itemgetter()` | Extracts a specific key from a dict (used in chains) |
| `ConversationSummaryBufferMemory` | Smart memory: recent messages raw + older ones summarized |
| `save_context()` | Saves a question-answer pair to memory |
| `load_memory_variables()` | Retrieves stored history from memory |

---

## Beginner-Friendly Summary
RAG is like an open-book exam:
- **Without RAG** = AI answers from what it memorized during training (closed book)
- **With RAG** = AI searches YOUR documents first, then answers (open book exam)

The contextualization step is like a smart friend who clarifies your vague questions:
- You: "Can I carry them forward?"
- Smart friend: "Do you mean annual leave? Let me check the policy..." ✅

Your HR bot (`agent.py` and `agent1.py`) is a complete production-ready RAG system! 🎉
