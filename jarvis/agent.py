from typing import Annotated, Literal
from typing_extensions import TypedDict
from PIL import Image
from langgraph.prebuilt import ToolNode
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import MessagesState
from langchain_core.messages import HumanMessage, SystemMessage


from langchain_ollama import ChatOllama
#from langchain_openai import ChatOpenAI
from jarvis.tools import (ha_get_all_the_entities_in_a_specific_class_short
                         ,ha_get_all_the_entity_names_in_a_specific_class
                         ,ha_get_state_of_a_specific_entity
                          ,ha_get_entities_containing)


system_message = SystemMessage(content='''Your name is Jarvis. You are a home assistant that answers questions about the user's home. 
 Follow these steps to provide accurate responses:

 1. Use the tool **ha_get_entities_containing** to retrieve a list of all entities that match the query term. 
    **Example: If the user asks for the temperature, you would query ha_get_entities_containing('temperature') to get a list of all temperature-related entities.**

 2. Once the entities are retrieved, **do not create or assume entity names**. 
    Always use the exact entity names from the result of Step 1. For example, if you retrieve:
    [
       "sensor.bedroom_sensor_temperature", 
       "sensor.fridge_temperature"
    ], use these specific entity names for the next step.

 3. To get the details or state of a specific entity, call **ha_get_state_of_a_specific_sensor**. 
    **Example: If you need the state of "sensor.bedroom_sensor_temperature", the API call should be: 
    ha_get_state_of_a_specific_sensor('sensor.bedroom_sensor_temperature').** 
    Do not attempt to fabricate or alter entity names.

 4. Based on the collected information, formulate your response. 
    Always use user-friendly names in your responses but ensure that these names correspond exactly to the entity IDs used in the API calls.

 Important: Never make up entity names. Use only those returned by the first API call.''')

# Node


model = ChatOllama(model= 'llama3.1:8b')
#model = ChatOpenAI(model='gpt-4o-mini')

#tools = [ha_get_entities
tools =[ha_get_state_of_a_specific_entity,
        ha_get_entities_containing]

model = model.bind_tools(tools)

def jarvis(state: MessagesState):
    ''' Expert node function to use tools'''

#def assistant(state: MessagesState):
#    return {"messages": [llm_with_tools.invoke([sys_msg] + state["messages"])]}

    # Define the system message with the refined instructions

    messages = state['messages']
    response = model.invoke([system_message] + messages)

    return {'messages': [response]}

tool_node = ToolNode(tools)

def should_continue(state: MessagesState) -> Literal["tools", END]:
    messages = state['messages']
    #print(messages)
    last_message = messages[-1]
    #print('this is last message',last_message)
    if last_message.tool_calls:
        print('last message has tools calls. For that reason it WILL CONTINUE WITH TOOL CALLS')
        return "tools"
    print('end returned')
    return END


graph = StateGraph(MessagesState)

graph.add_node('jarvis',jarvis)
graph.add_node('tools',tool_node)

graph.add_edge(START,'jarvis')
graph.add_conditional_edges('jarvis',should_continue)
graph.add_edge('tools','jarvis')

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

from langchain_core.runnables.graph import CurveStyle, MermaidDrawMethod, NodeStyles

# Save the image to a file
with open("graph_output.png", "wb") as f:
    f.write(
        app.get_graph().draw_mermaid_png(
            draw_method=MermaidDrawMethod.API,
        )
    )

while True:
    user_input = input('>> ')
    if user_input.lower() in ('quit','exit','stop'):
        break
    else:
        response = app.invoke({
            'messages' : [HumanMessage(content = user_input)]},
            config = {'configurable' : {'thread_id': 1}})
        print(response['messages'][-1].content)
