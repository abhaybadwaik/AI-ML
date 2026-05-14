from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from langchain_groq import ChatGroq

from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# -----------------------------
# 1. LLM
# -----------------------------
chat = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key="YOUR_GROQ_API-KEY"
)

# -----------------------------
# 2. Embeddings + Documents
# -----------------------------
embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

documents = [
    Document(page_content="Annual leave policy: Employees get 20 days of annual leave per year."),
    Document(page_content="Annual leave carry forward: Unused annual leave can be carried forward up to 5 days."),
    Document(page_content="Sick leave policy: Employees get 10 days of sick leave per year."),
    Document(page_content="Sick leave carry forward: Sick leave cannot be carried forward to next year."),
]

# -----------------------------
# 3. Vector Store + Retriever
# -----------------------------
vectorstore = FAISS.from_documents(documents, embeddings_model)
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})

# -----------------------------
# 4. Prompt (handles context + history)
# -----------------------------
qa_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an HR assistant.

Answer ONLY from the context.
If answer not found, say 'Not in policy'.

Context:
{context}"""),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

# -----------------------------
# 5. Helper to format docs
# -----------------------------
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# -----------------------------
# 6. RAG PIPELINE (NEW WAY)
# -----------------------------
from operator import itemgetter
from operator import itemgetter

contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system", """Given chat history and latest question,
rewrite it into a clear standalone question.
Focus on what the user is ACTUALLY asking right now, not previous topic.

Examples:
- "Can I carry them forward?" → "Can I carry annual leave forward?"
- "What about sick leave?" → "How many days of sick leave do I get?"
- "Can I carry that forward?" → "Can sick leave be carried forward?"
- "How many days?" → "How many days of annual leave do I get?"

Only return the rewritten question. Nothing else."""),

    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

contextualizer = (
    contextualize_prompt
    | chat
    | StrOutputParser()
)
rag_chain = (
    {
        "input": itemgetter("input"),
        "chat_history": itemgetter("chat_history"),
        "context": (
            contextualizer
            | retriever
            | format_docs
        )
    }
    | qa_prompt
    | chat
    | StrOutputParser()
)

# -----------------------------
# 7. Chat loop
# -----------------------------
chat_history = []

def chat_with_docs(question):
    response = rag_chain.invoke({
        "input": question,
        "chat_history": chat_history
    })

    chat_history.append(HumanMessage(content=question))
    chat_history.append(AIMessage(content=response))

    return response

# -----------------------------
# 8. Test conversation
# -----------------------------
print(chat_with_docs("How many days of annual leave do I get?"))
print(chat_with_docs("Can I carry them forward?"))
print(chat_with_docs("What about sick leave?"))
print(chat_with_docs("Can I carry that forward?"))