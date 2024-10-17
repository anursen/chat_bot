import os
from dotenv import load_dotenv

from typing import Annotated, Literal
from typing_extensions import TypedDict

from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver

from langchain_ollama import ChatOllama

from tools import process_job,process_resume

process_job()

model = ChatOllama(model= 'llama2:7b-chat-q2_K')

tools = [process_job,process_resume]

model.bind_tools(tools)

def expert(state: MessagesState):
    ''' Expert node function to use tools'''
    system_message = ''' Here is the system message for chat agent'''
    messages = state['messages']
    response = model.invoke([system_message] + messages)

    return {'messages': [response]}

tool_node = ToolNode(tools)

def should_continue(state: MessagesState) -> Literal['tools',END]:
    '''Edge between tool and expert'''
    messages = state['messages']
    last_message = messages[-1]
    
    if last_message.tool_calls:
        return 'tools'
    
    return END

graph = StateGraph(MessagesState)

graph.add_node('expert',expert)
graph.add_node('tools',tool_node)

graph.add_edge(START,'expert')
graph.add_conditional_edges('expert',should_continue)
graph.add_edge('tools','expert')

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)

while True:
    user_input = input('>> ')
    if user_input.lower() in ('quit','exit','stop'):
        break
    else:
        response = app.invoke({
            'messages' : [HumanMessage(content = user_input)]},
            config = {'configurable' : {'thread_id': 1}})
        print(response['messages'][-1].content)
