from langchain.chains import (
    create_history_aware_retriever,
    create_retrieval_chain
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_ollama import OllamaLLM
from utils.logger import logger
import os
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from utils.logger import  logger
from langchain_community.document_loaders import PyPDFLoader



# Attach user file to the session based on user_id and document path
def process_user_files(user_id: str):
    #To store multiple texts I created all_splits array
    #For now this function only process pdf files
    all_splits = []
    retriever = None
    user_folder = os.path.join('uploads', user_id)

    for file_name in os.listdir(user_folder):
        file_path = os.path.join(user_folder,file_name)
        if file_name.lower().endswith('.pdf'):
            loader = PyPDFLoader(file_path=file_path, extract_images=True)
            docs = loader.load()
            text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
            splits = text_splitter.split_documents(docs)
            all_splits.extend(splits)

            if all_splits:
                vectorstore = Chroma.from_documents(documents=all_splits, embedding=OpenAIEmbeddings())
                #TODO we should save the vector storage itself to a local db to save on tokens
                retriever = vectorstore.as_retriever()
    if not retriever:
        raise ValueError("No PDF files processed or no splits generated.")

    return retriever

# Main function for performing the RAG-based Q&A with user session and documents
def chatbot_rag_qa_call(chosen_model: str, human_message: str,system_message,
                   user_id: str, user_storage: dict):
    # Choose the model based on user input
    if chosen_model == 'ollama':
        model = OllamaLLM(model='llama3.1:8b')
        logger.debug(f"model : {chosen_model}, query :{human_message},for user {user_id}")
    elif chosen_model == 'gpt4':
        model = ChatOpenAI(model="gpt-4o-mini")
        logger.debug(f"model : {chosen_model}, query :{human_message},for user {user_id}")
    else:
        logger.error(f"Invalid model choice: {chosen_model}")
        return None

    logger.debug(f'Chosen model: {chosen_model}')

    # Retrieve session history or create a new one if it doesn't exist
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in user_storage:
            user_storage[session_id] = ChatMessageHistory()
        return user_storage[session_id]

    retriever = process_user_files(user_id)
    # Prompt to contextualize the user's query based on chat history
    contextualize_q_system_prompt = (
        "Using the provided chat history and the most recent user question,"
        "which may refer to earlier context,"
        "reword the question to be self-contained and understandable without needing the chat history."
        "Do NOT answer the question, simply rephrase it if necessary or return it unchanged."
    )

    contextualize_q_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

    # Create the history-aware retriever using the retriever and contextualization prompt
    history_aware_retriever = create_history_aware_retriever(
        model, retriever, contextualize_q_prompt
    )

    # QA system prompt to retrieve the answer from the context
    system_prompt = (
        "You are an assistant for question-answering tasks. "
        "Use the following pieces of retrieved context to answer "
        "the question. If you don't know the answer, say that you "
        "don't know. Answer in a polite tone. \n\n"
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            "system", system_prompt,
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )
    logger.critical(f"qa_prompt{qa_prompt}")
    # Create the final chain for combining documents and QA
    question_answer_chain = create_stuff_documents_chain(model, qa_prompt)
    rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

    # Use RunnableWithMessageHistory to manage chat history during the process
    conversational_rag_chain = RunnableWithMessageHistory(
        rag_chain,
        get_session_history,
        input_messages_key="input",
        history_messages_key="chat_history",
        output_messages_key="answer"
    )

    # Invoke the chain with user input and session configuration
    result = conversational_rag_chain.invoke(
        {"input": human_message},  # Input query
        {"configurable": {"session_id": user_id}}  # Configuration with session ID
    )

    # Return the final answer
    #return result
    return result.get('answer', "No answer could be generated.")