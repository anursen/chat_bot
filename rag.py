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

import asyncio
import nest_asyncio
from multiple_page_single_pdf_loader_retriever import Mpsdlr
question = 'Where does our customer Amy Macias live?'
# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

async def main(question,number_of_results):
    ollama_model_name = 'mxbai-embed-large:latest'
    file_path = 'uploads/invoices.pdf'
    vector_db = Mpsdlr(model=ollama_model_name)
    await vector_db.load_data_pdf(path=file_path)
    
    # Add the query at the end
    results = vector_db.query_data(question, number_of_results)
    return results

# Directly await the main coroutine
results = asyncio.run(main(question=question,number_of_results=30))
print(results)
results

333333333333333333333333333333333333333333333333333333

from langchain_openai import ChatOpenAI
from system_messages import system_message_rag,human_message_rag
system_message_rag
from langchain_core.prompts.chat import HumanMessagePromptTemplate,SystemMessagePromptTemplate,ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

model = ChatOpenAI(model= "gpt-4o-mini")

system_message_prompt  = SystemMessagePromptTemplate.from_template(system_message_rag)
human_message_prompt = HumanMessagePromptTemplate.from_template(human_message_rag)

prompt = ChatPromptTemplate.from_messages(
    [system_message_prompt, human_message_prompt]
)

chain = prompt | model 

chain.invoke(input={'context':results,'question' : question})

