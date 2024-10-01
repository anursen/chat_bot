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


#Debug Part
'''
path = 'uploads/invoices.pdf'
model = 'ollama'
question = "who is our customer from Bouvet Island (Bouvetoya)"
user_id = "user_session_1"
chatbot_rag_qa(path,model,question,user_id)
# Test the setup with a sample question and session ID


model = 'llama3.1:8b'
chatbot_rag_qa(path,model,'who is in charge','user_id_1')


# Initialize the LLM
model = OllamaLLM(model='llama3.1:8b')
#model = ChatOpenAI(model="gpt-4o-mini")

# Assume you have some invoices PDF or document data to load for your retriever
# For example purposes, let's assume we have text documents
# You should replace this with your PDF document loading mechanism

vector_storage = Mpsdlr(model = 'mxbai-embed-large:latest')
retriever = vector_storage.return_retriever(path)  # Assuming this returns documents


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

### Statefully manage chat history ###
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in user_storage:
        user_storage[session_id] = ChatMessageHistory()
    return user_storage[session_id]

# Use RunnableWithMessageHistory to manage history statefully
conversational_rag_chain = RunnableWithMessageHistory(
    rag_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)

# Test the setup with a sample question and session ID
session_id = "user_session_1"
question = "who is our customer from Bouvet Island (Bouvetoya)"

# Run the conversational chain and provide the question with the session_id in the config
result = conversational_rag_chain.invoke(
    {"input": question},  # Input for the chain
    {"configurable": {"session_id": session_id}}  # Config with session_id
)

# Print the result
print(result['answer'])

question = "what did he bought?"
result2 = conversational_rag_chain.invoke(
    {"input": question},  # Input for the chain
    {"configurable": {"session_id": session_id}}  # Config with session_id
)
print(result2['answer'])

session_id = "user_session_2"
question = "what did he bought?"
result3 = conversational_rag_chain.invoke(
    {"input": question},  # Input for the chain
    {"configurable": {"session_id": session_id}}  # Config with session_id
)
print(result3['answer'])


#question
#store This is the variable to store user history
#conversational_rag_chain RunnableWithMessageHistory()
#input_messages_key="input",
#history_messages_key="chat_history",
#output_messages_key="answer",
contextualize_q_prompt
conversational_rag_chain
qa_prompt.messages[0]
#SystemMessagePromptTemplate(prompt=PromptTemplate(input_variables=['context'], input_types={}, partial_variables={}, template="You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. If you don't know the answer, say that you don't know. Use three sentences maximum and keep the answer concise.\n\n{context}"), additional_kwargs={})
qa_prompt.messages[1]
qa_prompt.messages[2]
#HumanMessagePromptTemplate(prompt=PromptTemplate(input_variables=['input'], input_types={}, partial_variables={}, template='{input}'), additional_kwargs={})
result.keys()
result['input']
result['chat_history']
result['context']
result['answer']
'''