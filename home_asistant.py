
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiIyZGM0YzZkOTNlNTY0YzExOWY5YjE2ZGI4ODYyMDNkNyIsImlhdCI6MTcyODQ0NjU1MywiZXhwIjoyMDQzODA2NTUzfQ.nnqhx_FCZL6WoHmaxyaW-dUr79qdjG_1QdX8X6f6cv0'
api_url = "http://192.168.86.12:8123/api/states"

from langchain_core.tools import tool
import pprint
import requests
from langchain import hub
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

def query_home_assistant(api_url: str, token: str) -> dict:
    """Query Home Assistant API.

    Args:
        api_url: The API endpoint of Home Assistant.
        token: The Bearer token for authorization.

    Returns:
        The JSON response from the API.
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        result = response.json()
        return result
    else:
        raise Exception(f"API call failed with status code {response.status_code}")

query_home_assistant(api_url,token)


from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
from langchain.prompts import ChatPromptTemplate

#llm = ChatOpenAI(model="gpt-4o-mini")
llm = OllamaLLM(model="llama3.2:3b")



from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain.docstore.document import Document

response = query_home_assistant(api_url,token)
from langchain.docstore.document import Document

from langchain_core.documents import Document
import json
processed_response = []
for i in response:
    processed_response.append(json.dumps(i,separators=(',', ':')))


#Document object is made of  dictionary with two keys
#'page_content'  : we will place the string here
#'metadata'      : {'source':'local'}
# You can create a multiple "page" Document object by creating a list of Document objects
documents = []
for i in processed_response:
    a = Document(page_content=i,metadata={})
    documents.append(a)

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
splits = text_splitter.split_documents(documents)
vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
retriever = vectorstore.as_retriever()

prompt = hub.pull("rlm/rag-prompt")

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    {"context": retriever | format_docs ,"question": RunnablePassthrough()}
    | prompt
    | llm
    | StrOutputParser()
)

question = 'Whats the temp in guestroom'
question = 'Whats the average humidity in my house? Also show me the basis for your answer?'
question = 'Where is Abdurrahim'
question = 'Whats should be the avarage regular household humidity?'
question = 'How much electricity did Tesla used on his last charge?'
question = 'How much electricity did tesla wall connector used than?'
question = 'Whats the cost of this charge?'
question = 'which light are on in my home right now?'
rag_chain.invoke(question)


