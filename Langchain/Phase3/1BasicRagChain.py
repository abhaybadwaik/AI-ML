"""
Phase 3 · Lesson 1 — Basic RAG Chain
Complete Q&A system over your own PDF document

WHAT WE ARE TRYING TO ACHIEVE:
Combine all Phase 2 pieces into one clean RAG chain.
User asks question → retriever finds chunks → LLM answers from chunks.
This is a complete production ready RAG pipeline.
"""

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os

load_dotenv()

PDF_PATH = "Phase2/NEW_SYNOPSIS (Autosaved).pdf"


# ── Step 1: Build or Load Vector Store ───────────────────────
def build_vector_store():
    print("Loading document...")
    loader = PyPDFLoader(PDF_PATH)
    docs = loader.load()

    print("Splitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50
    )
    chunks = splitter.split_documents(docs)
    print(f"Total chunks: {len(chunks)}")

    print("Creating embeddings...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    if os.path.exists("Phase2/faiss_index"):
        print("Loading FAISS from disk...")
        store = FAISS.load_local(
            "Phase2/faiss_index",
            embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        print("Creating FAISS store...")
        store = FAISS.from_documents(chunks, embeddings)
        store.save_local("Phase2/faiss_index")

    return store, embeddings


# ── Step 2: Build RAG Chain ───────────────────────────────────
def build_rag_chain(store):

    # retriever — finds top 3 relevant chunks
    retriever = store.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 3}
    )

    # LLM
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=500)

    # prompt — tells LLM to answer from context only
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant that answers questions based on the provided document context.

Rules:
- Answer ONLY from the context provided
- If answer is not in context, say "I don't have enough information to answer this"
- Be concise and accurate
- Mention which section/page the answer comes from if possible

Context:
{context}"""),
        ("human", "{question}"),
    ])

    # format retrieved chunks into one string
    def format_docs(docs):
        formatted = []
        for doc in docs:
            page = doc.metadata.get('page', 'N/A')
            formatted.append(f"[Page {page}]\n{doc.page_content}")
        return "\n\n---\n\n".join(formatted)

    # full RAG chain
    rag_chain = (
        {
            "context": retriever | format_docs,
            "question": RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


# ── Step 3: Run Q&A ───────────────────────────────────────────
def run_qa(rag_chain):
    print("\n" + "="*60)
    print("  RAG Q&A System — UPI Study Document")
    print("="*60)

    questions = [
        "What is the main topic of this research?",
        "What is the sample size used in this study?",
        "What are the hypotheses of this study?",
        "What statistical tools are used for data analysis?",
        "What are the limitations of this study?",
    ]

    for q in questions:
        print(f"\nQ: {q}")
        answer = rag_chain.invoke(q)
        print(f"A: {answer}")
        print("-"*50)


# ── Main ──────────────────────────────────────────────────────
if __name__ == "__main__":
    store, embeddings = build_vector_store()
    rag_chain = build_rag_chain(store)
    run_qa(rag_chain)

    print("""
=== What we built ===
Complete RAG pipeline:
  PDF → chunks → embeddings → FAISS → retriever → LLM → answer

Key improvement over Phase 2:
  Phase 2 → separate pieces, manual steps
  Phase 3 → one clean pipeline, production ready

Next → Lesson 2: Conversational RAG with memory
       So users can ask follow up questions!
""")