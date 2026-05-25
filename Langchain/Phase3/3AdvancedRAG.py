"""
Phase 3 · Lesson 3 — Advanced RAG
Better retrieval using Multi-query and HyDE techniques
"""

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_classic.retrievers import MultiQueryRetriever
import os
import logging

load_dotenv()


# ── Setup ─────────────────────────────────────────────────────
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=500)

store = FAISS.load_local(
    "Phase2/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)
print("✅ Vector store loaded!")
print()

base_retriever = store.as_retriever(search_kwargs={"k": 3})


# ── 1. Basic RAG — for comparison ────────────────────────────
print("=== Basic RAG (for comparison) ===")

basic_prompt = ChatPromptTemplate.from_messages([
    ("system", """Answer from context only. If not in context say 'I dont have enough information.'
Context: {context}"""),
    ("human", "{question}"),
])

def format_docs(docs):
    return "\n\n".join(
        f"[Page {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}"
        for doc in docs
    )

basic_chain = (
    {
        "context": base_retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | basic_prompt
    | llm
    | StrOutputParser()
)

question = "What is hypothesis 2 about?"
print(f"Q: {question}")
print(f"Basic RAG: {basic_chain.invoke(question)}")
print()


# ── 2. MultiQueryRetriever ────────────────────────────────────
print("=== MultiQueryRetriever ===")

logging.basicConfig()
logging.getLogger("langchain.retrievers.multi_query").setLevel(logging.INFO)

multi_query_retriever = MultiQueryRetriever.from_llm(
    retriever=base_retriever,
    llm=llm,
)

multi_query_chain = (
    {
        "context": multi_query_retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | basic_prompt
    | llm
    | StrOutputParser()
)

print(f"Q: {question}")
print(f"MultiQuery RAG: {multi_query_chain.invoke(question)}")
print()


# ── 3. HyDE ──────────────────────────────────────────────────
print("=== HyDE (Hypothetical Document Embeddings) ===")

hyde_prompt = ChatPromptTemplate.from_messages([
    ("system", """Generate a hypothetical answer to this question as if you found it in a research document.
Write it as a factual statement, 2-3 sentences.
Write confidently as if from a document."""),
    ("human", "{question}"),
])

def hyde_retriever(question):
    hypo_answer = (hyde_prompt | llm | StrOutputParser()).invoke({"question": question})
    print(f"  Hypothetical answer: {hypo_answer[:150]}...")
    docs = store.similarity_search(hypo_answer, k=3)
    return docs

hyde_chain = (
    {
        "context": RunnableLambda(lambda x: format_docs(hyde_retriever(x))),
        "question": RunnablePassthrough(),
    }
    | basic_prompt
    | llm
    | StrOutputParser()
)

print(f"Q: {question}")
print(f"HyDE RAG: {hyde_chain.invoke(question)}")
print()


# ── 4. Side by side comparison ────────────────────────────────
print("="*60)
print("=== Side by side comparison ===")
print("="*60)

test_questions = [
    "What is hypothesis 2 about?",
    "What barriers prevent UPI adoption?",
]

for q in test_questions:
    print(f"\nQuestion: {q}")
    print(f"Basic     : {basic_chain.invoke(q)[:150]}...")
    print(f"MultiQuery: {multi_query_chain.invoke(q)[:150]}...")
    print(f"HyDE      : {hyde_chain.invoke(q)[:150]}...")
    print()

print("""
=== Summary ===
Basic RAG   → one question → one search → may miss chunks
MultiQuery  → generates 3-5 query versions → searches all → better recall
HyDE        → generates hypothetical answer → searches using that

When to use:
  Basic RAG   → simple questions, good keyword overlap
  MultiQuery  → vague questions, when basic RAG misses answers
  HyDE        → complex questions, technical documents
""")