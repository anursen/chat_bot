#https://python.langchain.com/docs/how_to/document_loader_pdf/
from langchain_community.document_loaders import PyPDFLoader

file_path = (
    "layout-parser-paper.pdf"
)


loader = PyPDFLoader(file_path)
docs = loader.load()
docs[0].metadata
docs[0].page_content
docs[0]