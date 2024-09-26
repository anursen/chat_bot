from langchain_core.prompts.chat import ChatPromptTemplate,HumanMessagePromptTemplate
from system_messages import system_message_friendly


def return_initial_prompt(text,sytem_template):
    return ChatPromptTemplate({'user message':HumanMessagePromptTemplate(text),'system message': system_message_friendly})

a = return_initial_prompt('merhabe',system_message_friendly)
a.pretty_print()
a.


from langchain_core.messages import HumanMessage, SystemMessage

messages = [
    SystemMessage(content="Translate the following from English into Italian"),
    HumanMessage(content="hi!"),
]

model.invoke(messages)