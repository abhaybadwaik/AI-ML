from langchain_community.document_loaders.csv_loader import CSVLoader

# Load a CSV file
loader = CSVLoader(file_path="C:/Users/Desk-68/Desktop/Agents/Langchain/Data/Instagram_Analytics.csv")
documents = loader.load()

print("Total rows loaded:", len(documents))
print()
print("=== First row as Document ===")
print(documents[0].page_content)
print()
print("=== Metadata ===")
print(documents[0].metadata)
