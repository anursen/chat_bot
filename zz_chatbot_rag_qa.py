from operator import ifloordiv
from IPython.testing.plugin.pytest_ipdoctest import pytest_collect_file
from langchain.chains.question_answering.refine_prompts import chat_qa_prompt_template
from sub_functions.sample_pdf_genarator import create_random_invoices
from sub_functions.invoice_retriever import Mpsdlr
import asyncio
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import OllamaLLM
from utils.logger import logger
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from utils.prompt_templates import system_message_rag
from sub_functions.invoice_retriever import Mpsdlr
#create_random_invoices(10)


def get_related_results(question,number_of_results):
    ollama_model_name = 'mxbai-embed-large:latest'
    file_path = 'uploads/invoices.pdf'
    vector_db = Mpsdlr(model=ollama_model_name)
    vector_db.load_data_pdf(path=file_path)
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

    222222222222222222
    #Sample Usage for retriver
    from sub_functions.invoice_retriever import Mpsdlr
    question = 'Where does our customer Justin Hodge live?'
    ollama_model_name = 'mxbai-embed-large:latest'
    file_path = 'uploads/invoices.pdf'

    vector_db = Mpsdlr(model=ollama_model_name)
    vector_db.load_data_pdf(path=file_path)
    results = vector_db.query_data(question,10)
    results.get('documents')
    222222222
    
    
    template = ChatPromptTemplate.from_template(system_message_rag)
    retrived_results = get_related_results(question, number_of_results)
    
    from langchain_core.messages import HumanMessage, SystemMessage
    human_message = template.invoke({'context':retrived_results})
    chain = prompt | model
    chain.invoke({"question": query, 'context': retrived_results})
    results = get_related_results(question=question,number_of_results=30)

    logger.critical(f"returning response for '{human_message}' for'{system_message}' tone")

    response = model.invoke(messages)
    return response


from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_ollama import OllamaLLM
from sub_functions.invoice_retriever import Mpsdlr
from utils.logger import logger
#from langchain_openai import OpenAIEmbeddings
#from langchain_chroma import Chroma
#from langchain_text_splitters import RecursiveCharacterTextSplitter


def attach_user_file_to_user(user_id,path):
    vector_storage = Mpsdlr(model='mxbai-embed-large:latest',user_id=user_id)
    retriever = vector_storage.return_retriever(path)  # Assuming this returns documents
    user_files[user_id] = retriever


def chatbot_rag_qa(file_path,choosen_model, query, user_id,user_files,user_storage):

    if choosen_model == 'ollama':
        model = OllamaLLM(model='llama3.1:8b')
        logger.debug(f'choseen model {choosen_model}')
    elif choosen_model == 'gpt4':
        model = ChatOpenAI(model="gpt-4o-mini")
        logger.debug(f'choseen model {choosen_model}')

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in user_storage:
            user_storage[session_id] = ChatMessageHistory()
        return user_storage[session_id]

    #logger.critical(f"returning response for '{human_message}' for'{system_message}' tone")
    if file_path:
        if user_id in user_files:
            retriever = user_files[user_id]
            logger.critical(f"{user_id} has a file in storage, so we are using this file")
        else:
            attach_user_file_to_user(user_id,file_path)
            retriever = user_files[user_id]
            logger.critical(f"{user_id} dont have a file in storage,We created a new file")


    ### Contextualize question ###
    contextualize_q_system_prompt = (
        "Given a chat history and the latest user question "
        "which might reference context in the chat history, "
        "formulate a standalone question which can be understood "
        "without the chat history. Do NOT answer the question, "
        "just reformulate it if needed and otherwise return it as is."
    )
    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    history_aware_retriever = create_history_aware_retriever(
        model, retriever, contextualize_q_prompt
    )

    ### Answer question ###
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Use three sentences maximum and keep the "
        "answer concise."
        "\n\n"
        "{context}"
    )
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ]
    )
    question_answer_chain = create_stuff_documents_chain(model, qa_prompt)

    # Create the final retrieval-augmented generation (RAG) chain
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # Use RunnableWithMessageHistory to manage history statefully
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer",
    )



    # Run the conversational chain and provide the question with the session_id in the config
    result = conversational_rag_chain.invoke(
        {"input": query},  # Input for the chain
        {"configurable": {"session_id": user_id}}  # Config with session_id
    )

    # Print the result
    #return result['answer']
    return result

path = 'uploads/invoices.pdf'
model = 'ollama'
question = "who is our customer from Bouvet Island (Bouvetoya)"
user_id = "user_session_1"
user_files = {}
user_storage = {}
chatbot_rag_qa(path,model,question,user_id,user_files,user_storage)
