from langchain_text_splitters import RecursiveCharacterTextSplitter

text = """
LangChain is a framework for developing applications powered by language models.
It provides tools to connect language models with external data sources.
You can build chatbots, question answering systems, and much more.

LangChain has several core components.
The first component is Models which includes LLMs and Chat Models.
The second component is Prompts which help structure input to models.
The third component is Chains which connect multiple steps together.
The fourth component is Memory which helps maintain conversation context.
The fifth component is Agents which can take autonomous actions.
"""

# RecursiveCharacterTextSplitter tries these separators in order:
# first tries paragraph breaks \n\n
# then tries newlines \n
# then tries spaces
# then splits by character
splitter = RecursiveCharacterTextSplitter(
    chunk_size=200,
    chunk_overlap=30
)

chunks = splitter.split_text(text)

print("Total chunks:", len(chunks))
print()
for i, chunk in enumerate(chunks):
    print(f"=== Chunk {i+1} ({len(chunk)} chars) ===")
    print(chunk)
    print()

