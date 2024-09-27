from pydoc_data.topics import topics

from sample_pdf_genarator import create_random_invoices
from multiple_page_single_pdf_loader_retriever import Mpsdlr
import asyncio

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import OllamaLLM
from logger import logger

#create_random_invoices(50)

#Sample Usage
ollama_model_name = 'mxbai-embed-large:latest'

file_path = 'uploads/invoices.pdf'
query = "What Steven Web bought from us"

b = Mpsdlr(model=ollama_model_name)

# Load the PDF asynchronously
asyncio.run(b.load_data_pdf(path=file_path))

#Query  db
b.query_data('Amy Macias',5)

1111111111111111111111111111111111111111111111111111111

from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI


model = ChatOpenAI(model="gpt-4o-mini")
prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")

chain = prompt | model | StrOutputParser()

chain.invoke({'topic':'base'})


prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("user", "Tell me a joke about {topic}")
])

prompt_template.invoke({"topic": "cats"})
