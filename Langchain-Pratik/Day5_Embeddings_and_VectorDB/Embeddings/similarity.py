from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from langchain_community.embeddings import HuggingFaceEmbeddings

embeddings_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


sentences = [
    "I love playing cricket",
    "Cricket is my favourite sport",
    "I enjoy watching football",
    "Python is a programming language"
]

vectors = embeddings_model.embed_documents(sentences)

# Compare first sentence with all others
base_vector = np.array(vectors[0]).reshape(1, -1)

print("Similarity of other sentences with 'I love playing cricket':")
print()
for i in range(1, len(sentences)):
    other_vector = np.array(vectors[i]).reshape(1, -1)
    similarity = cosine_similarity(base_vector, other_vector)[0][0]
    print(f"'{sentences[i]}' → similarity: {similarity:.4f}")