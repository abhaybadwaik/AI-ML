from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain.memory import ConversationSummaryBufferMemory
from operator import itemgetter

# -----------------------------
# 1. LLM
# -----------------------------
chat = ChatGroq(
    model="llama-3.3-70b-versatile",  # upgraded model
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
# 4. Memory — ConversationSummaryBufferMemory
# This keeps recent messages raw + summarizes older ones
# So context is never lost even in long conversations
# -----------------------------
memory = ConversationSummaryBufferMemory(
    llm=chat,
    max_token_limit=500,
    return_messages=True,     # returns as message objects not plain string
    memory_key="chat_history" # must match prompt placeholder name
)

# -----------------------------
# 5. Prompts
# -----------------------------
contextualize_prompt = ChatPromptTemplate.from_messages([
    ("system", """Given chat history and latest question,
rewrite it into a clear standalone question.
Focus on what the user is ACTUALLY asking right now.

Examples:
- "Can I carry them forward?" → "Can I carry annual leave forward?"
- "What about sick leave?" → "How many days of sick leave do I get?"
- "Can I carry that forward?" → "Can sick leave be carried forward?"
- "How many days?" → "How many days of annual leave do I get?"

Only return the rewritten question. Nothing else."""),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", """You are an HR assistant.
Answer ONLY from the context below.
If answer not found say 'Not in policy'.

Context:
{context}"""),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}")
])

# -----------------------------
# 6. Helper
# -----------------------------
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# -----------------------------
# 7. Chains
# -----------------------------
contextualizer = contextualize_prompt | chat | StrOutputParser()

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

# -----------------------------
# 8. Chat function using Memory
# -----------------------------
def chat_with_docs(question):

    # Load history from memory
    history = memory.load_memory_variables({})["chat_history"]

    # Run RAG chain
    response = rag_chain.invoke({
        "input": question,
        "chat_history": history
    })

    # Save this turn to memory automatically
    memory.save_context(
        {"input": question},
        {"output": response}
    )

    return response

# -----------------------------
# 9. Test — all 4 questions
# -----------------------------
q1 = chat_with_docs("How many days of annual leave do I get?")
print("Q1:", q1)

q2 = chat_with_docs("Can I carry them forward?")
print("Q2:", q2)

q3 = chat_with_docs("What about sick leave?")
print("Q3:", q3)

q4 = chat_with_docs("Can I carry that forward?")
print("Q4:", q4)

# See what memory stored
print()
print("=== MEMORY CONTENTS ===")
print(memory.load_memory_variables({})["chat_history"])