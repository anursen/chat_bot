from operator import ifloordiv
from IPython.testing.plugin.pytest_ipdoctest import pytest_collect_file
from langchain.chains.question_answering.refine_prompts import chat_qa_prompt_template
from sympy.solvers.diophantine.diophantine import diop_known
from sample_pdf_genarator import create_random_invoices
from multiple_page_single_pdf_loader_retriever import Mpsdlr
import asyncio
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import OllamaLLM
from logger import logger
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from system_messages import system_message_rag


#create_random_invoices(50)

import asyncio
import nest_asyncio
from multiple_page_single_pdf_loader_retriever import Mpsdlr
question = 'Where does our customer Amy Macias live?'
# Apply nest_asyncio to allow nested event loops
nest_asyncio.apply()

async def get_related_results(question,number_of_results):
    ollama_model_name = 'mxbai-embed-large:latest'
    file_path = 'uploads/invoices.pdf'
    vector_db = Mpsdlr(model=ollama_model_name)
    await vector_db.load_data_pdf(path=file_path)
    
    # Add the query at the end
    results = vector_db.query_data(question, number_of_results)
    return results

#Sample Usage
#ollama_model_name = 'mxbai-embed-large:latest'

#file_path = 'uploads/invoices.pdf'
#query = "What Steven Web bought from us"

def qa_with_rag(query,choosen_model,system_message,chat_message,pdf_path,number_of_results):
    if choosen_model =='ollama':
        model = OllamaLLM(model='llama3.1:8b')
        logger.debug(f'choseen model {choosen_model}')

    elif choosen_model == 'gpt4':
        model = ChatOpenAI(model="gpt-4o-mini")
        logger.debug(f'choseen model {choosen_model}')

    template = ChatPromptTemplate.from_template(system_message_rag)
    retrived_results = get_related_results(question, number_of_results)
    from langchain_core.messages import HumanMessage, SystemMessage
    human_message = template.invoke({'context':retrived_results})
    chain = prompt | model
    chain.invoke({"question": query, 'context': retrived_results})

    logger.critical(f"returning response for '{human_message}' for'{system_message}' tone")

    response = model.invoke(messages)
    return response




# Directly await the main coroutine
results = asyncio.run(get_related_results(question=question,number_of_results=30))





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

