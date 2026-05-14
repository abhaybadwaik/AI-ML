from langchain_community.document_loaders import WebBaseLoader
from bs4 import SoupStrainer

loader = WebBaseLoader(
    web_paths=("https://en.wikipedia.org/wiki/Cricket",),
    bs_kwargs={
        "parse_only": SoupStrainer("p")   # only paragraph text
    }
)

documents = loader.load()

print(documents[0].page_content[:500])
