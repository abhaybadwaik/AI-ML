"""
Phase 3 · Lesson 5 — RAG Evaluation
Measuring RAG pipeline quality automatically

WHAT WE ARE TRYING TO ACHIEVE:
We built a RAG pipeline but how do we know if it's good?
RAG Evaluation measures quality automatically using metrics.

Three key metrics:
Faithfulness     → is answer supported by context? (no hallucination)
Answer Relevancy → does answer address the question?
Context Recall   → did retriever find right chunks?
"""

from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_classic.retrievers import EnsembleRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
import json

load_dotenv()


# ── Setup ─────────────────────────────────────────────────────
print("Setting up RAG pipeline...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=300)

loader = PyPDFLoader("Phase2/NEW_SYNOPSIS (Autosaved).pdf")
docs = loader.load()
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
chunks = splitter.split_documents(docs)

faiss_store = FAISS.load_local(
    "Phase2/faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)

semantic_retriever = faiss_store.as_retriever(search_kwargs={"k": 3})
bm25_retriever = BM25Retriever.from_documents(chunks)
bm25_retriever.k = 3

hybrid_retriever = EnsembleRetriever(
    retrievers=[semantic_retriever, bm25_retriever],
    weights=[0.5, 0.5]
)

prompt = ChatPromptTemplate.from_messages([
    ("system", """Answer from context only. If not in context say 'I dont have enough information.'
Context: {context}"""),
    ("human", "{question}"),
])

def format_docs(docs):
    seen = set()
    unique = []
    for doc in docs:
        if doc.page_content not in seen:
            seen.add(doc.page_content)
            unique.append(doc)
    return "\n\n".join(
        f"[Page {doc.metadata.get('page', 'N/A')}]\n{doc.page_content}"
        for doc in unique
    )

rag_chain = (
    {
        "context": hybrid_retriever | format_docs,
        "question": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)

print("✅ RAG pipeline ready!")
print()


# ── Test dataset ──────────────────────────────────────────────
# In real projects you create 50-100 question-answer pairs
# from your document to evaluate your RAG

test_data = [
    {
        "question": "What is the sample size of this study?",
        "ground_truth": "The sample size is 150 respondents",
        "keywords": ["150", "sample size", "respondents"]
    },
    {
        "question": "What formula was used to calculate the sample size?",
        "ground_truth": "Cochran's Sample Size Formula was used",
        "keywords": ["cochran", "formula", "sample size"]
    },
    {
        "question": "What are the objectives of the study?",
        "ground_truth": "To identify UPI awareness, analyze demographic impact, evaluate drivers and barriers",
        "keywords": ["objectives", "awareness", "adoption", "barriers"]
    },
    {
        "question": "What statistical tools are used?",
        "ground_truth": "Chi-Square Test and One-Way ANOVA",
        "keywords": ["chi-square", "anova", "statistical"]
    },
    {
        "question": "What is the geographical scope?",
        "ground_truth": "The study is confined to Maharashtra, India",
        "keywords": ["maharashtra", "geographical", "scope"]
    },
]


# ── Evaluation functions ──────────────────────────────────────

def evaluate_faithfulness(answer: str, context: str, llm) -> float:
    """
    Checks if every claim in the answer is supported by context.
    Score: 0.0 to 1.0 (1.0 = fully faithful, no hallucination)
    """
    eval_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an evaluator. Check if the answer is fully supported by the context.
Rate faithfulness from 0.0 to 1.0:
1.0 = every claim in answer is in context
0.5 = some claims supported, some not
0.0 = answer contains claims not in context (hallucination)
Reply with ONLY a number like 0.8"""),
        ("human", f"Context:\n{context}\n\nAnswer:\n{answer}\n\nFaithfulness score:"),
    ])

    score = (eval_prompt | llm | StrOutputParser()).invoke({})
    try:
        return float(score.strip())
    except:
        return 0.0


def evaluate_answer_relevancy(question: str, answer: str, llm) -> float:
    """
    Checks if answer actually addresses the question.
    Score: 0.0 to 1.0
    """
    eval_prompt = ChatPromptTemplate.from_messages([
        ("system", """You are an evaluator. Check if the answer addresses the question asked.
Rate relevancy from 0.0 to 1.0:
1.0 = answer directly and completely addresses the question
0.5 = answer partially addresses the question
0.0 = answer doesn't address the question at all
Reply with ONLY a number like 0.7"""),
        ("human", f"Question: {question}\n\nAnswer: {answer}\n\nRelevancy score:"),
    ])

    score = (eval_prompt | llm | StrOutputParser()).invoke({})
    try:
        return float(score.strip())
    except:
        return 0.0


def evaluate_context_recall(answer: str, ground_truth: str, keywords: list) -> float:
    """
    Simple keyword based check — did retrieved context contain key information?
    Score: 0.0 to 1.0
    """
    answer_lower = answer.lower()
    if "dont have enough information" in answer_lower or "don't have enough information" in answer_lower:
        return 0.0

    matched = sum(1 for kw in keywords if kw.lower() in answer_lower)
    return round(matched / len(keywords), 2)


# ── Run Evaluation ────────────────────────────────────────────
print("="*60)
print("=== RAG Evaluation Results ===")
print("="*60)

results = []

for i, item in enumerate(test_data, 1):
    question    = item["question"]
    ground_truth = item["ground_truth"]
    keywords    = item["keywords"]

    # get RAG answer and context
    retrieved_docs = hybrid_retriever.invoke(question)
    context = format_docs(retrieved_docs)
    answer = rag_chain.invoke(question)

    # evaluate
    faithfulness    = evaluate_faithfulness(answer, context, llm)
    relevancy       = evaluate_answer_relevancy(question, answer, llm)
    context_recall  = evaluate_context_recall(answer, ground_truth, keywords)

    results.append({
        "question": question,
        "answer": answer,
        "faithfulness": faithfulness,
        "relevancy": relevancy,
        "context_recall": context_recall,
    })

    print(f"\nQ{i}: {question}")
    print(f"Answer     : {answer[:120]}...")
    print(f"Faithfulness   : {faithfulness:.2f}")
    print(f"Relevancy      : {relevancy:.2f}")
    print(f"Context Recall : {context_recall:.2f}")
    print("-"*50)


# ── Overall scores ────────────────────────────────────────────
avg_faithfulness   = sum(r["faithfulness"] for r in results) / len(results)
avg_relevancy      = sum(r["relevancy"] for r in results) / len(results)
avg_context_recall = sum(r["context_recall"] for r in results) / len(results)
overall            = (avg_faithfulness + avg_relevancy + avg_context_recall) / 3

print("\n" + "="*60)
print("=== Overall RAG Score ===")
print("="*60)
print(f"Faithfulness   : {avg_faithfulness:.2f} / 1.0")
print(f"Answer Relevancy: {avg_relevancy:.2f} / 1.0")
print(f"Context Recall : {avg_context_recall:.2f} / 1.0")
print(f"Overall Score  : {overall:.2f} / 1.0")
print()

if overall >= 0.8:
    print("🟢 Excellent RAG pipeline!")
elif overall >= 0.6:
    print("🟡 Good pipeline, room for improvement")
elif overall >= 0.4:
    print("🟠 Average — needs tuning")
else:
    print("🔴 Poor — check chunking and retrieval")

print("""
=== How to improve low scores ===
Low Faithfulness   → LLM is hallucinating → add stricter prompt
Low Relevancy      → answers off topic → improve prompt or retriever
Low Context Recall → retriever missing chunks → fix chunking or use hybrid search

Production RAG evaluation:
  Run evaluation on 50-100 questions
  Track scores over time as you improve pipeline
  Target: Faithfulness > 0.8, Relevancy > 0.8
""")