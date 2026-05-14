from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

sentence = "I love playing cricket "
vector = embeddings_model.embed_query(sentence)

print("Sentence:", sentence)
print("Vector length:", len(vector))
print("First 10 numbers:", vector[:10])