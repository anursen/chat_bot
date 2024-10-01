from langchain_core.messages import HumanMessage, SystemMessage
from langchain_ollama import OllamaLLM
from logger import logger
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

    from langchain_core.prompts import ChatPromptTemplate
    from langchain_ollama.llms import OllamaLLM

    template = """Question: {question}

    Answer: Let's think step by step."""

    prompt = ChatPromptTemplate.from_template(template)

    model = OllamaLLM(model="llama3.1")

    chain = prompt | model

    chain.invoke({"question": "What is LangChain?"})

    logger.critical(f"returning response for '{human_message}' for'{system_message}' tone")

    response = model.invoke(messages)

    if choosen == 'ollama':
        response_text = response
    if choosen == 'gpt4':
        response_text = response.content

    return response_text
