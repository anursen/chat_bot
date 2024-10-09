from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_openai import ChatOpenAI
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from utils.logger import logger
from langchain.schema import BaseChatMessageHistory, ChatMessage, HumanMessage, AIMessage
from database.database import DatabaseChatMessageHistory

def chatbot_regular(human_message, system_message, chosen_model, user_id, user_storage):
    global model

    def get_session_history(session_id: str) -> BaseChatMessageHistory:
        return DatabaseChatMessageHistory(user_id= user_id,session_id='222')

    # Load session history from the database
    message_history = get_session_history(user_id)
    message_history.add_message(HumanMessage(content=human_message)
                                ,tone=system_message
                                ,message_type="human"                  # Indicate this is a human message
                                )
    # Choose the model based on user input
    if chosen_model == 'ollama':
        model = OllamaLLM(model='llama3.1:8b')
    elif chosen_model == 'gpt4':
        model = ChatOpenAI(model="gpt-4o-mini")
    else:
        logger.error(f"Invalid model choice: {chosen_model}")
        return None

    prompt = ChatPromptTemplate.from_messages(
        [("system",
          "You're an assistant that gives answers in  {tone} tone. Respond in 20 words or fewer",
         ),MessagesPlaceholder(variable_name="history"),
           ("human", "{input}"),
        ])
    runnable = prompt | model

    def get_session_history(user_id: str) -> BaseChatMessageHistory:
        if user_id not in user_storage:
            user_storage[user_id] = ChatMessageHistory()
        return user_storage[user_id]
    #print(user_storage)
    print(get_session_history(user_id))

    with_message_history = RunnableWithMessageHistory(
        runnable,
        get_session_history = get_session_history,
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
    message_history.add_message(
        AIMessage(content=response),  # Pass only the content to AIMessage
        tone=system_message,  # Pass tone separately to add_message
        intent=None,  # If you have an intent, pass it here
        model=chosen_model,  # Pass the model used
        feedback=None,  # If there's feedback, pass it here
        language=None,  # Pass the language if needed
        message_type="ai"  # Indicate this is an AI message
    )
    return response