from langchain_core.prompts import PromptTemplate

prompt_template = PromptTemplate.from_template("Tell me a joke about {topic}")

prompt_template.invoke({"topic": "cats"})


from langchain_core.prompts import ChatPromptTemplate

prompt_template = ChatPromptTemplate.from_messages([
    ("system", "You are a {system_message} assistant"),
    ("user", "Tell me a joke about {topic}")
])

prompt_template.invoke({"topic": "cats"})

prompt_template.input_variables
prompt_template.format_messages(topic='aaa',system_message = 'aaa')

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate

model = ChatOpenAI(model="gpt-4o-mini")

prompt = ChatPromptTemplate.from_template("tell me a joke about {topic}")

chain = prompt | model | StrOutputParser()

chain.input_schema
chain.get_input_schema

<bound method RunnableSequence.get_input_schema of ChatPromptTemplate(
input_variables=['topic'], input_types={}, partial_variables={}, 
messages = [HumanMessagePromptTemplate(
    prompt=PromptTemplate(
    input_variables=['topic'],
    input_types={},
    partial_variables={},
    template='tell me a joke about {topic}'),
    additional_kwargs={})])
| ChatOpenAI(client=<openai.resources.chat.completions.Completions object at 0x114b2b610>, 
             async_client=<openai.resources.chat.completions.AsyncCompletions object at 0x114b50610>, 
             root_client=<openai.OpenAI object at 0x114af6750>,
             root_async_client=<openai.AsyncOpenAI object at 0x114b2b190>, 
             model_name='gpt-4o-mini',
             model_kwargs={},
             openai_api_key=SecretStr('**********'))
| StrOutputParser()>