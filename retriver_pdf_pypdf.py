#https://python.langchain.com/docs/how_to/document_loader_pdf/
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import CharacterTextSplitter

file_path = ("layout-parser-paper.pdf")

loader = PyPDFLoader(file_path)
docs = loader.load()
'''
whole_pages = []
for i in range(len(docs)):
    whole_pages.append((docs[i].page_content))
joined_strings = '/n'.join(whole_pages)
'''

text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
texts = text_splitter.split_documents(docs)

embeddings = OpenAIEmbeddings()
vectorstore = FAISS.from_documents(texts, embeddings)

