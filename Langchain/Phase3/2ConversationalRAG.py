"""
Phase 3 · Lesson 2 — Conversational RAG
RAG pipeline with conversation memory
"""

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.messages import HumanMessage, AIMessage
from langchain_community.chat_message_histories import ChatMessageHistory
import os

load_dotenv()

PDF_PATH = "Phase2/NEW_SYNOPSIS (Autosaved).pdf"


def build_vector_store():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    if os.path.exists("Phase2/faiss_index"):
        store = FAISS.load_local(
            "Phase2/faiss_index",
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ Vector store loaded!")
    else:
        loader = PyPDFLoader(PDF_PATH)
        docs = loader.load()
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        chunks = splitter.split_documents(docs)
        store = FAISS.from_documents(chunks, embeddings)
        store.save_local("Phase2/faiss_index")
        print("✅ Vector store created!")

    return store


def build_conversational_rag(store):

    retriever = store.as_retriever(search_kwargs={"k": 3})
    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0, max_tokens=500)

    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful assistant answering questions about a research document on UPI digital payments.

Answer ONLY from the context provided.
If answer is not in context say "I don't have enough information."
Be concise and mention page numbers when possible.

Context from document:
{context}"""),
        MessagesPlaceholder("chat_history"),
        ("human", "{question}"),
    ])

    def format_docs(docs):
        formatted = []
        for doc in docs:
            page = doc.metadata.get('page', 'N/A')
            formatted.append(f"[Page {page}]\n{doc.page_content}")
        return "\n\n---\n\n".join(formatted)

    def get_question(x):
        return x["question"]

    def get_history(x):
        return x.get("chat_history", [])

    rag_chain = (
        {
            "context": RunnableLambda(get_question) | retriever | format_docs,
            "question": RunnableLambda(get_question),
            "chat_history": RunnableLambda(get_history),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    return rag_chain


def chat(rag_chain, history, question):
    response = rag_chain.invoke({
        "question": question,
        "chat_history": history.messages,
    })

    history.add_user_message(question)
    history.add_ai_message(response)

    return response


if __name__ == "__main__":
    print("Setting up Conversational RAG...")
    store = build_vector_store()
    rag_chain = build_conversational_rag(store)
    history = ChatMessageHistory()

    print("\n" + "="*60)
    print("  Conversational RAG — UPI Study Document")
    print("="*60)

    conversations = [
        "What is the sample size of this study?",
        "Why was this specific sample size chosen?",
        "What formula was used to calculate it?",
        "What are the hypotheses?",
        "Tell me more about hypothesis 2 specifically.",
    ]

    for question in conversations:
        print(f"\nYou: {question}")
        answer = chat(rag_chain, history, question)
        print(f"Bot: {answer}")
        print()

    print("="*60)
    print("Full conversation history stored in memory:")
    for msg in history.messages:
        role = "You" if isinstance(msg, HumanMessage) else "Bot"
        print(f"  {role}: {msg.content[:80]}...")