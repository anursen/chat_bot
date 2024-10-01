# https://python.langchain.com/docs/how_to/prompts_composition/

from langchain_core.prompts import PromptTemplate
from langchain_core.prompts import ChatPromptTemplate

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant"),
    ("user", "Tell me a joke about {topic}")
])

prompt_template.invoke({"topic": "cats"})




