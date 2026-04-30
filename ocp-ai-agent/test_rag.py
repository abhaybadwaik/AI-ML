from rag import initialize_rag, find_similar_incidents

print("Testing LlamaIndex RAG...\n")

engine = initialize_rag()

result = find_similar_incidents(
    "Prometheus running without persistent storage",
    engine
)

print("\n─── RAG Result ───")
print(result)
print("\nRAG working!")