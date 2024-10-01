import bs4
from langchain import hub
from langchain_chroma import Chroma
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


from langchain_community.document_loaders import PyPDFLoader

loader = PyPDFLoader('uploads/NIPS-2017-attention-is-all-you-need-Paper.pdf')
pages = []
async for page in loader.alazy_load():
    pages.append(page)


text_splitter = RecursiveCharacterTextSplitter(chunk_size=100, chunk_overlap=20)

splits = text_splitter.split_documents([pages[0]])


splits


vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())

# Retrieve and generate using the relevant snippets of the blog.
retriever = vectorstore.as_retriever()
from langchain_openai import ChatOpenAI


llm = ChatOpenAI(model="gpt-4o-mini")
llm.invoke("What is Task Decomposition?")