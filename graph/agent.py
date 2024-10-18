from typing import Annotated, Literal
from typing_extensions import TypedDict
from PIL import Image
from langgraph.prebuilt import ToolNode
from langchain_core.messages import HumanMessage
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.checkpoint.memory import MemorySaver
#from langchain_ollama import ChatOllama
from langchain_openai import ChatOpenAI
from tools import get_job,get_resume

#model = ChatOllama(model= 'llama2:7b-chat-q2_K')
model = ChatOpenAI(model='gpt-4o-mini')

tools = [get_job,get_resume]

model = model.bind_tools(tools)

def expert(state: MessagesState):
    ''' Expert node function to use tools'''
    system_message = '''  You are a resume expert. You are tasked with improving the user resume based on a job description.
        You can access the resume and job data using the provided tools.

        You must NEVER provide information that the user does not have.
        These include, skills or experiences that are not in the resume. Do not make things up.
        '''
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
        print('tools returned')
        return "tools"
    print('end returned')
    return END


graph = StateGraph(MessagesState)

graph.add_node('expert',expert)
graph.add_node('tools',tool_node)

graph.add_edge(START,'expert')
graph.add_conditional_edges('expert',should_continue)
graph.add_edge('tools','expert')

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
