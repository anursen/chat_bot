from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import OllamaLLM
from logger import logger


def generate_one_time_response(human_message,system_message,choosen,history):
    global model
    from langchain_openai import ChatOpenAI

    #ollama
    #gpt4
    if choosen =='ollama':
        model = OllamaLLM(model='llama3.1:8b')
        logger.debug(f'choseen model {choosen}')
    elif choosen == 'gpt4':
        model = ChatOpenAI(model="gpt-4o-mini")
        logger.debug(f'choseen model {choosen}')
    messages = [
        SystemMessage(content=system_message),
        HumanMessage(content=human_message),

    ]
    logger.critical(f"returning response for '{human_message}' for'{system_message}' tone")

    response = model.invoke(messages)

    if choosen == 'ollama':
        response_text = response
    if choosen == 'gpt4':
        response_text = response.content

    return response_text



