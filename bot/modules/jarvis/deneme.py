import pprint
from langchain_openai import ChatOpenAI
from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import create_react_agent
import jarvis_with_memory 
import ha_get_entities_containing
from typing import TypedDict
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

model = ChatOpenAI(model="gpt-4o-mini")

class State(TypedDict):
    some_key: str
    messages : str

tools = [ha_get_entities_containing]

graph = create_react_agent(model, tools)
message = 'Whats is the sensor related with temperature?'

response =  graph.invoke({'messages':message})

for line in response['messages']:
    pprint.pp(line.content)
pprint.pprint