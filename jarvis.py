import requests
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
import os
from dotenv import load_dotenv
from utils.logger import logger
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.docstore.document import Document
import json
from langchain_core.tools import tool
from typing import List

def jarvis(human_message,system_message,chosen_model,user_id,user_storage):

    # Load environment variables from the .env file
    load_dotenv()
    # Get the Home Assistant token
    token = os.getenv('HA_TOKEN')
    states_url = os.getenv('HA_STATES_URL')
    services_url = os.getenv('HA_SERVICES_URL')

    if chosen_model == 'ollama':
        model = OllamaLLM(model='llama3.1:8b')
    elif chosen_model == 'gpt4':
        model = ChatOpenAI(model="gpt-4o-mini")
    else:
        logger.error(f"Invalid model choice: {chosen_model}")

    from langchain_core.documents import Document
    #from langchain.docstore.document import Document
    response = query_home_assistant(states_url, token)

    processed_response = []
    for i in response:
        processed_response.append(json.dumps(i, separators=(',', ':')))

    # Document object is made of  dictionary with two keys
    # 'page_content'  : we will place the string here
    # 'metadata'      : {'source':'local'}
    # You can create a multiple "page" Document object by creating a list of Document objects
    documents = []
    for i in processed_response:
        a = Document(page_content=i, metadata={})
        documents.append(a)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    splits = text_splitter.split_documents(documents)
    vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
    retriever = vectorstore.as_retriever()

    prompt = hub.pull("rlm/rag-prompt")

    def format_docs(docs):
        return "\n\n".join(doc.page_content for doc in docs)

    rag_chain = (
            {"context": retriever | format_docs, "question": RunnablePassthrough()}
            | prompt
            | model
            | StrOutputParser()
    )

    return   rag_chain.invoke(human_message)



@tool
def query_home_assistant() -> dict:
    """Query Home Assistant API to get all the current states from all the sensors.

    Returns:
        The JSON response from the API.
    """

    load_dotenv()
    # Get the Home Assistant token
    token = os.getenv('HA_TOKEN')
    states_url = os.getenv('HA_STATES_URL')
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(states_url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        logger.critical(f"Api call failed to home asistant with {api_url}")
        pass
@tool
def ha_get_entities() -> dict:
    """
    Connects to the Home Assistant API to retrieve information about entities in the home.
    The function queries the Home Assistant API to fetch the current state of all entities.
    It processes the response to build a dictionary that contains metadata (friendly name and entity type)
    for each entity identified by its unique entity_id.

    Returns:
        dict: A dictionary where the keys are entity_ids, and the values are dictionaries with:
              - 'friendly_name': The human-readable name of the entity.
              - 'entity_type': The type of the entity, determined by splitting the entity_id.

    Example:
        {
            "light.living_room": {"friendly_name": "Living Room Light", "entity_type": "light"},
            "sensor.temperature_kitchen": {"friendly_name": "Kitchen Temperature", "entity_type": "sensor"}
        }
    """
    # Load environment variables such as the Home Assistant token from the .env file.
    load_dotenv()

    # Retrieve the Home Assistant API token from the environment variables.
    token = os.getenv('HA_TOKEN')

    # Set the request headers including the authorization token and content type.
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Define the Home Assistant API endpoint URL to query for the entity states.
    api_url = 'http://192.168.86.12:8123/api/states'

    # Make the GET request to the Home Assistant API to fetch the current state of all entities.
    response = requests.get(api_url, headers=headers)

    # Check if the API request was successful (status code 200).
    if response.status_code == 200:
        # Parse the JSON response from the API.
        result = response.json()

        # Create a dictionary to hold the entity metadata.
        entity_dict = {}
        for item in result:
            # Get the unique entity_id for each item (representing an entity).
            entity_id = item.get('entity_id')

            # Retrieve the 'friendly_name' attribute of the entity, defaulting to 'Not Available' if not found.
            friendly_name = item['attributes'].get('friendly_name', 'Not Available')

            # Extract the entity type from the entity_id by splitting at the period ('.').
            entity_type = entity_id.split('.')[0]

            # Store the entity metadata (friendly_name and entity_type) in the dictionary.
            entity_dict[entity_id] = {'friendly_name': friendly_name, 'entity_type': entity_type}

        # Return the final dictionary containing all entities and their metadata.
        return entity_dict

    else:
        # Log a critical error if the API request fails (status code not 200).
        logger.critical(f"API call failed to Home Assistant with URL: {api_url}, Status Code: {response.status_code}")

        # Return an empty dictionary in case of an API failure.
        return {}
@tool
def ha_get_state_of_a_specific_sensor(entity_id) -> dict:
    """
    Retrieves the current state of a specific sensor from the Home Assistant API.

    Args:
        entity_id (str): The entity ID of the sensor in Home Assistant (e.g., 'zone.neda').

    Returns:
        dict: A dictionary containing the state information of the specified sensor, or an empty dictionary if the API call fails.

    Raises:
        Critical: Logs a critical message if the API call to Home Assistant fails.
    """
    # Load environment variables, including the Home Assistant token
    load_dotenv()

    # Get the Home Assistant token from environment variables
    token = os.getenv('HA_TOKEN')

    # Define the request headers with authorization and content type
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Construct the API URL using the provided entity_id
    api_url = f"http://192.168.86.12:8123/api/states/{entity_id}"

    # Make a GET request to the Home Assistant API to retrieve the sensor state
    response = requests.get(api_url, headers=headers)

    # If the API call is successful, return the response as a JSON object
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        # Log a critical error if the API call fails and return an empty dictionary
        logger.critical(
            f"API call failed to Home Assistant with URL: {api_url}, Status Code: {response.status_code}")
        return {}

@tool
def ha_get_all_the_entity_names_in_a_specific_class(class_name) -> dict:
    """
      Retrieve all entity names and their friendly names for a specified entity class from Home Assistant.

      Args:
          class_name: The class name (e.g., 'person', 'sensor', 'light') for which the entities should be returned.

      Returns:
          dict: A dictionary containing the entities of the specified class.
      """
    # Load environment variables (for HA_TOKEN)
    load_dotenv()
    token = os.getenv('HA_TOKEN')

    # Define headers for the API request
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # API URL to retrieve all entity states from Home Assistant
    api_url = "http://192.168.86.12:8123/api/states"

    # Make a GET request to Home Assistant API
    response = requests.get(api_url, headers=headers)

    # Check if the response is successful
    if response.status_code == 200:
        # Parse the JSON response
        entities = response.json()
        # Initialize an empty dictionary to hold class-specific entities
        entity_dict = {}
        # Loop through the list of entities
        for entity in entities:
            entity_id = entity.get('entity_id')
            entity_type = entity_id.split('.')[0]
            friendly_name = entity['attributes'].get('friendly_name', 'Not Available')

            if entity_type not in entity_dict:
                entity_dict[entity_type] = {}

                # Add the entity_id and friendly_name to the appropriate class in the dictionary
            entity_dict[entity_type][entity_id] = {'friendly_name': friendly_name}

        # Return the final dictionary containing the entities for the specified class
        if class_name in entity_dict:
            return entity_dict[class_name]
        else:
            logger.critical(f"API call failed to Home Assistant with URL: {api_url}, Status Code: {response.status_code}")
            return {}

@tool
def ha_get_all_the_entities_in_a_specific_class_short(class_name) -> List:
    """
      Retrieve all entity names for a specified entity class from Home Assistant.

      Args:
          class_name: The class name (e.g., 'person', 'sensor', 'light') for which the entities should be returned.

      Returns:
          list: A list containing the entities of the specified class.
      """
    # Load environment variables (for HA_TOKEN)
    load_dotenv()
    token = os.getenv('HA_TOKEN')

    # Define headers for the API request
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # API URL to retrieve all entity states from Home Assistant
    api_url = "http://192.168.86.12:8123/api/states"

    # Make a GET request to Home Assistant API
    response = requests.get(api_url, headers=headers)

    # Check if the response is successful
    if response.status_code == 200:
        # Parse the JSON response
        entities = response.json()
        # Initialize an empty dictionary to hold class-specific entities
        results = []
        entity_dict = {}
        # Loop through the list of entities
        for entity in entities:
            entity_id = entity.get('entity_id')
            entity_type = entity_id.split('.')[0]
            if entity_type == class_name:
                results.append(entity_id)

        # Return the final list  containing the entities for the specified class
        return results

    else:
        logger.critical(f"API call failed to Home Assistant with URL: {api_url}, Status Code: {response.status_code}")
        return []

