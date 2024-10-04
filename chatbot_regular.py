from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from utils.logger import logger

# Function to generate a response with user history
def generate_one_time_response(human_message, system_message, chosen_model, user_id, user_storage):
    global model

    # Choose the model based on user input
    if chosen_model == 'ollama':
        model = OllamaLLM(model='llama3.1:8b')
    elif chosen_model == 'gpt4':
        model = ChatOpenAI(model="gpt-4o-mini")
    else:
        logger.error(f"Invalid model choice: {chosen_model}")
        return None

    prompt = ChatPromptTemplate.from_messages(
        [
            (
                "system",
                "You're an assistant that gives answers in  {tone} tone. Respond in 20 words or fewer",
            ),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}"),
        ]
    )
    runnable = prompt | model

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        if session_id not in user_storage:
            user_storage[session_id] = ChatMessageHistory()
        return user_storage[session_id]

    with_message_history = RunnableWithMessageHistory(
        runnable,
        get_session_history,
        input_messages_key="input",
        history_messages_key="history",
    )

    response = with_message_history.invoke(
        input = {"tone": system_message, "input": human_message},
        config={"configurable": {"session_id": user_id}},
    )
    logger.debug(f"response from the chat bot{response}")
    #print(response)
    if chosen_model == 'gpt4':
        response = response.content
    return response