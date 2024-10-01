from langchain.chains import (
    create_history_aware_retriever,
    create_retrieval_chain
)
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_ollama import OllamaLLM
from sub_functions.invoice_retriever import Mpsdlr
from utils.logger import logger


# Attach user file to the session based on user_id and document path
def attach_user_file(user_id: str, path: str, user_files: dict):
    vector_storage = Mpsdlr(model='mxbai-embed-large:latest', user_id=user_id)
    retriever = vector_storage.return_retriever(path)
    user_files[user_id] = retriever


# Main function for performing the RAG-based Q&A with user session and documents
def chatbot_rag_qa_call(file_path: str, chosen_model: str, query: str,
                   user_id: str, user_files: dict, user_storage: dict):
    # Choose the model based on user input
    if chosen_model == 'ollama':
        model = OllamaLLM(model='llama3.1:8b')
    elif chosen_model == 'gpt4':
        model = ChatOpenAI(model="gpt-4o-mini")
    else:
        logger.error(f"Invalid model choice: {chosen_model}")
        return None

    logger.debug(f'Chosen model: {chosen_model}')

    # Retrieve session history or create a new one if it doesn't exist
    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in user_storage:
            user_storage[session_id] = ChatMessageHistory()
        return user_storage[session_id]

    # Attach the user file to the session, if applicable
    if file_path:
        if user_id not in user_files:
            attach_user_file(user_id, file_path, user_files)
            logger.debug(f"Created new file for user {user_id}")
        retriever = user_files[user_id]
        logger.debug(f"Using file for user {user_id} from storage")

    # Prompt to contextualize the user's query based on chat history
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
        "don't know. Use three sentences maximum and keep the "
        "answer concise.\n\n"
        "{context}"
    )

    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}")
        ]
    )

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
        {"input": query},  # Input query
        {"configurable": {"session_id": user_id}}  # Configuration with session ID
    )

    # Return the final answer
    return result
    #return result.get('answer', "No answer could be generated.")


