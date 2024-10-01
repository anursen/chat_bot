from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import OllamaLLM
from utils.logger import logger
from langchain_openai import ChatOpenAI

def generate_one_time_response(human_message,system_message,choosen,history):
    global model


    #ollama
    #gpt4
    if choosen =='ollama':
        model = OllamaLLM(model='llama3.1:8b')
        logger.debug(f'choseen model {choosen}')
    elif choosen == 'gpt4':
        model = ChatOpenAI(model="gpt-4o-mini")
        logger.debug(f'choseen model {choosen}')

    logger.critical(f"returning response for '{human_message}' for'{system_message}' tone")

    #TODO We should handle system messages here as well 

    response = model.invoke(human_message)

    if choosen == 'ollama':
        response_text = response
    if choosen == 'gpt4':
        response_text = response.content

    return response_text
