from langgraph.graph import START, StateGraph
from langgraph.prebuilt import tools_condition, ToolNode
from IPython.display import Image, display
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama
from langgraph.checkpoint.memory import MemorySaver
from  dotenv import load_dotenv
from langchain_core.tools import tool
from langgraph.graph import MessagesState
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from markdown_it.rules_inline import entity
from requests import post
import os
import requests
from datetime import datetime, timedelta
import json
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from utils.logger import logger


def jarvis_with_memory(human_message:str,system_message,chosen_model,user_id,user_storage):
    print(user_storage)
    '''User Storage is a MemorySaver '''
    #TODO Implement Ollama to that as well
    #TODO memory storage only available in session level. No hard memory available
    #TODO No session level memory available,
    if chosen_model == 'ollama':
        llm = ChatOllama(model="llama3.1:8b")
    else:
        llm = ChatOpenAI(model="gpt-4o-mini")

    #@tool
    def ha_get_entities_containing(filter: str) -> list:
        """
        Retrieve all entity names from Home Assistant and filter the ones that contain the specified value.

        Args:
            filter: A string to filter the entity names by using the __contains__() method.

        Returns:
            list: A list of entity names that contain the specified value.
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
        print(f"[TOOL][Api call] => ha_get_entities_containing({filter})")
        # Check if the response is successful
        if response.status_code == 200:
            # Parse the JSON response
            entities = response.json()
            # Initialize an empty list to hold filtered entity names
            filtered_entities = []

            # Loop through the list of entities
            for entity in entities:
                entity_id = entity.get('entity_id')

                # Add the entity_id to the list if it contains the specified value
                if filter in entity_id:
                    filtered_entities.append(entity_id)

            return filtered_entities
        else:
            logger.critical(f"'ha_get_entities_containing' API call failed to Home Assistant with URL: {api_url}, Status Code: {response.status_code}")
            return []
    @tool
    def ha_get_state_of_a_specific_entity(entity_id) -> dict:
        """
        Retrieves the current state of a specific entity from the Home Assistant API.

        Args:
            entity_id (str): The entity ID of the sensor in Home Assistant (e.g., 'zone.neda').

        Returns:
            dict: A dictionary containing the state information of the specified sensor, or an empty dictionary if the API call fails.

        Raises:
            Critical: Logs a critical message if the API call to Home Assistant fails.
        """
        print(f"[TOOL][Api call] => get_state_of_specific_entity({entity_id})")
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
                f"ha_get_state_of_a_specific_sensor(entity_id) API call failed to Home Assistant with URL: {api_url}, Status Code: {response.status_code}")
            return {}
    @tool
    def ha_set_state_of_a_specific_entity(entity_id,data) -> dict:
        """
        Unfinished Function
        """
        print(f"[TOOL][Api call] => set_state_of_specific_entity({entity_id})")
        # Load environment variables, including the Home Assistant token
        load_dotenv()
        # Get the Home Assistant token from environment variables
        token = os.getenv('HA_TOKEN')
        # Define the request headers with authorization and content type
        headers = {"Authorization": f"Bearer {token}","Content-Type": "application/json"}
        # Construct the API URL using the provided entity_id
        api_url = f"http://192.168.86.12:8123/api/states/{entity_id}"
        response = post(api_url, headers=headers, json=data)
        # If the API call is successful, return the response as a JSON object
        if response.status_code == 200:
            result = response.json()
            return result
        else:
            # Log a critical error if the API call fails and return an empty dictionary
            logger.critical(
                f"ha_get_state_of_a_specific_sensor(entity_id) API call failed to Home Assistant with URL: {api_url}, Status Code: {response.status_code}")
            return {}
    @tool
    def ha_get_entity_history(entity_id):
        """
         Fetches the past 10 days of state history for the specified Home Assistant entity.

         Parameters:
         -----------
         entity_id : str
             The unique ID of the Home Assistant entity to retrieve history for.

         Returns:
         --------
         list of dict or None
             A list of dictionaries with each entry containing:
               - 'state': str - The entity's state at a specific time.
               - 'when': str - The timestamp of the state change.
             Returns None if the request fails.
         """
        print(f"[TOOL][Api call] => get_history_of_a_specific_entity({entity_id})")
        # Load environment variables, including the Home Assistant token
        load_dotenv()
        # Get the Home Assistant token from environment variables
        token = os.getenv('HA_TOKEN')
        ha_url = os.getenv('HA_URL')
        # Define the request headers with authorization and content type
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        # Construct the API URL using the provided entity_id
        # 10 days before in UTC format to get the history for the last 10 days
        start_time = (datetime.now() - timedelta(days=10)).isoformat(timespec='seconds') + 'Z'
        # Current time as start_time in the specified format
        end_time = datetime.now().astimezone().isoformat(timespec='seconds')
        api_url = f"{ha_url}/api/history/period/{start_time}?filter_entity_id={entity_id}&end_time={end_time}&no_attributes"
        print(api_url)

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json", }

        response = requests.get(api_url, headers=headers)
        # Check if the request was successful
        if response.status_code == 200:
            result = response.json()
            compacted_data = []
            for record_group in result:
                for record in record_group:
                    compacted_data.append({
                        'state': record['state']
                        , 'when': record['last_changed']
                    })
            if len(compacted_data) > 100:
                return compacted_data[-100:]
            return compacted_data
        else:
            logger.critical(
                f"ha_get_state_of_a_specific_sensor(entity_id) API call failed to Home Assistant with URL: {api_url}, Status Code: {response.status_code}")
            return None
    @tool
    def ha_get_logbook(entity_id=None, days=0.1):
        """
        Fetches logbook records for a specified Home Assistant entity or all entities within a given timeframe.

        Parameters:
        -----------
        entity_id : str, optional
            The unique ID of the Home Assistant entity to retrieve logs for. If None, retrieves logs for all entities.
        days : int, optional
            Number of past days to include in the log records. Default is 0.1.

        Returns:
        --------
        list of dict or None
            A list of dictionaries, each containing:
              - 'name': str - The entity's friendly name or event name.
              - 'message': str - A description of the event.
              - 'when': str - The timestamp of the log entry.
            Returns None if the request fails.
        """
        print(f"[TOOL][Api call] => ha_get_logbook(entitiy_id:{entity_id}, days:{days})")
        load_dotenv()
        token = os.getenv('HA_TOKEN')
        ha_url = os.getenv('HA_URL')

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Construct time range for logs
        start_time = (datetime.now() - timedelta(days=days)).isoformat(timespec='seconds') + 'Z'
        api_url = f"{ha_url}/api/logbook/{start_time}"

        # Include entity_id filter if provided
        if entity_id:
            api_url += f"?entity={entity_id}"

        response = requests.get(api_url, headers=headers)

        # Process the response
        if response.status_code == 200:
            log_data = response.json()
            compacted_logs = []
            for log in log_data:
                compacted_logs.append({
                    'name': log.get('name')
                    ,'state': log.get('state')
                    ,'message': log.get('message')
                    ,'when': log.get('when')
                })
            return compacted_logs
        else:
            logger.critical(
                f"ha_get_logbook() API call failed to Home Assistant with URL: {api_url}, Status Code: {response.status_code}")
            return None

    tools = [ha_get_entities_containing
            ,ha_get_state_of_a_specific_entity
            ,ha_get_entity_history
            ,ha_get_logbook]

    llm_with_tools = llm.bind_tools(tools)

    # System message
    sys_msg = SystemMessage(
        content="You are Jarvis, a smart home assistant designed to help with managing home devices and providing information about their statuses. "
                "You have access to the Home Assistant API through various tools. "
                "You can perform the following tasks: "
                "1. Query Home Assistant for a list of entities in the home. "
                "2. Retrieve the current status of any entity. "
                "3. Get the historical data of an entity to analyze past behaviors. "
                f"Always provide accurate and concise information while ensuring a {system_message} tone.")

    # Node
    def assistant(state: MessagesState):
       print('Asistant node run.')
       return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}
       

    # Graph
    builder = StateGraph(MessagesState)

    # Define nodes: these do the work
    builder.add_node("assistant", assistant)
    builder.add_node("tools", ToolNode(tools))

    # Define edges: these determine how the control flow moves
    builder.add_edge(START, "assistant")
    builder.add_conditional_edges(
        "assistant",
        # If the latest message (result) from assistant is a tool call -> tools_condition routes to tools
        # If the latest message (result) from assistant is a not a tool call -> tools_condition routes to END
        tools_condition,
    )
    builder.add_edge("tools", "assistant")

    react_graph_memory = builder.compile(checkpointer=user_storage)

    # Display the graph
    #png_image = react_graph_memory.get_graph().draw_mermaid_png()
    # Save the PNG to a file
    #with open("jarvis_with_memory.png", "wb") as f:
    #    f.write(png_image)


    # Specify a thread
    config = {"configurable": {"thread_id": user_id}}

    # Specify an input
    messages = [HumanMessage(content=human_message)]
    print(messages)
    print(react_graph_memory.get_state(config))


        # Run
    messages = react_graph_memory.invoke({"messages": messages},config)
    #for m in messages['messages']:
    #    m.pretty_print()


    return messages['messages'][-1].content

