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
import sqlite3
from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

human_message = 'Hi My name is Abdur' 
system_message = 'desciriptive'
chosen_model = 'ollama'
user_id = 'user_id_1'
if not os.path.exists('state_db'):
    os.makedirs('state_db')
db_path = "state_db/example.db"
conn = sqlite3.connect(db_path, check_same_thread=False)
# Here is our checkpointer
memory = SqliteSaver(conn)
user_storage = memory

llm = ChatOpenAI(model="gpt-4o-mini")

@tool
def ha_get_entities_containing(filter: str) -> list:
        """
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
tools = [ha_get_entities_containing]

llm_with_tools = llm.bind_tools(tools)

    # System message
sys_msg = SystemMessage(content="You are Jarvis, a smart home assistant designed to help with managing home devices and providing information about their statuses. "
                "You have access to the Home Assistant API through various tools. "
                "You can perform the following tasks: "
                f"Always provide accurate and concise information while ensuring a {system_message} tone.")

# Node
def assistant(state: MessagesState):
    print('Asistant node run.')
    print(state)
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

    # Run
messages = react_graph_memory.invoke({"messages": messages},config)
#for m in messages['messages']:
#    m.pretty_print()


return messages['messages'][-1].content

