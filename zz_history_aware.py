#Sample_code
# https://python.langchain.com/docs/how_to/prompts_composition/
# https://python.langchain.com/v0.2/docs/how_to/qa_chat_history_how_to/



import bs4
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_chroma import Chroma
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain.chains import LLMChain

from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chat_models import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage

# Define the system message prompt
contextualize_q_system_prompt = (
    "Given a chat history and the latest user question, "
    "which might reference context in the chat history, "
    "formulate a standalone question that can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed, and otherwise return it as is."
)

# Define the prompt template using the system prompt and placeholders
contextualize_q_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", contextualize_q_system_prompt),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}")
    ]
)

# Initialize the LLM (language model)
model = ChatOpenAI(model="gpt-4")

# Create the sequence using prompt and LLM
chain = contextualize_q_prompt | model

# Define chat history and input
input_text = 'aaa'
chat_history = [
    {"role": "user", "content": "Hello, how can I improve my resume?"},
    {"role": "assistant", "content": "You can start by including relevant work experiences."}
]

# Prepare the formatted chat history as a list of messages
formatted_chat_history = [
    HumanMessage(content=msg["content"]) if msg["role"] == "user" else SystemMessage(content=msg["content"])
    for msg in chat_history
]

# Invoke the chain with input and chat history
response = chain.invoke({
    "input": input_text,
    "chat_history": formatted_chat_history
})

print(response)

333333333333333333333333333333333333333


### Statefully manage chat history ###
store = {}


def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]


conversational_rag_chain = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer",
)


conversational_rag_chain.invoke(
    {"input": "What is Task Decomposition?"},
    config={
        "configurable": {"session_id": "abc123"}
    },  # constructs a key "abc123" in `store`.
)["answer"]


store
chat_history
formatted_chat_history

444444444444444444444444444444444444444
