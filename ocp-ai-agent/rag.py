import os
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.groq import Groq
from config import settings

# ─────────────────────────────────────────────
# Setup LlamaIndex with Groq + HuggingFace
# HuggingFace embeddings = free, no API key needed
# ─────────────────────────────────────────────
def initialize_rag():
    """Initialize LlamaIndex RAG pipeline over incidents folder."""
    print("  [RAG] Initializing LlamaIndex...")

    # Use HuggingFace for embeddings (free)
    Settings.embed_model = HuggingFaceEmbedding(
        model_name="BAAI/bge-small-en-v1.5"
    )

    # Use Groq as the LLM
    Settings.llm = Groq(
        model=settings.llm_model,
        api_key=settings.groq_api_key
    )

    # Load all incident files
    incidents_path = os.path.join(os.path.dirname(__file__), "incidents")
    documents = SimpleDirectoryReader(incidents_path).load_data()
    print(f"  [RAG] Loaded {len(documents)} incident documents")

    # Build vector index
    index = VectorStoreIndex.from_documents(documents)
    query_engine = index.as_query_engine(similarity_top_k=2)
    print("  [RAG] Vector index ready!")

    return query_engine


def find_similar_incidents(failure_message: str, query_engine) -> str:
    """Search past incidents for similar issues and resolutions."""
    try:
        query = f"Find similar past incidents and resolution steps for: {failure_message}"
        response = query_engine.query(query)
        return str(response)
    except Exception as e:
        print(f"  [RAG] Query failed: {e}")
        return "No similar past incidents found."