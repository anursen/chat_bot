from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from utils.logger import logger


# Retrieve session history or create a new one if it doesn't exist
def get_session_history(session_id: str, user_storage: dict) -> ChatMessageHistory:
    if session_id not in user_storage:
        user_storage[session_id] = ChatMessageHistory()
    return user_storage[session_id]


# Function to generate a response with user history
def generate_one_time_response(human_message, system_message, choosen, user_id, user_storage):
    global model

    # Choose the model based on user input
    if choosen == 'ollama':
        model = OllamaLLM(model='llama3.1:8b')
        logger.debug(f'chosen model {choosen}')
    elif choosen == 'gpt4':
        model = ChatOpenAI(model="gpt-4o-mini")
        logger.debug(f'chosen model {choosen}')
    else:
        logger.error(f"Invalid model choice: {choosen}")
        return None

    # Get the session history for the user
    chat_history = get_session_history(user_id, user_storage)

    # Add the system message to the history if present
    if system_message:
        chat_history.add_message(SystemMessage(content=system_message))

    # Add the human message (query) to the history
    chat_history.add_message(HumanMessage(content=human_message))

    logger.critical(f"returning response for '{human_message}' with '{system_message}' tone")

    # Retrieve the full chat history as a string for context
    full_chat_history = "\n".join(message.content for message in chat_history.messages)

    # Get the response from the model, including the chat history
    response = model.invoke(f"{full_chat_history}\n{human_message}")

    # Process response based on the chosen model
    if choosen == 'ollama':
        response_text = response
    elif choosen == 'gpt4':
        response_text = response.content

    # Optionally, you can add the model's response back into the chat history
    chat_history.add_message(AIMessage(content=response_text))

    return response_text
