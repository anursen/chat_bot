#documentation about that module
#https://python.langchain.com/docs/how_to/document_loader_pdf/
from sample_pdf_genarator import create_random_invoices
from langchain_community.document_loaders import PyPDFLoader
import ollama
import chromadb

create_random_invoices(50)

def load_document(file_path):
    '''This function loads pdf file and returns vector db'''
    pass

file_path = 'uploads/invoices.pdf'
loader = PyPDFLoader(
    file_path = file_path,
    #password = "my-pasword",
    extract_images = True,
    # headers = None
    # extraction_mode = "plain",
    # extraction_kwargs = None,
)

loader = PyPDFLoader(file_path)
pages = []
async for page in loader.alazy_load():
    pages.append(page)

print(pages[0].page_content)

a = ollama.embeddings(
  model='mxbai-embed-large:latest',
  prompt=pages[0].page_content)
a



documents = [
  "Llamas are members of the camelid family meaning they're pretty closely related to vicuñas and camels",
  "Llamas were first domesticated and used as pack animals 4,000 to 5,000 years ago in the Peruvian highlands",
  "Llamas can grow as much as 6 feet tall though the average llama between 5 feet 6 inches and 5 feet 9 inches tall",
  "Llamas weigh between 280 and 450 pounds and can carry 25 to 30 percent of their body weight",
  "Llamas are vegetarians and have very efficient digestive systems",
  "Llamas live to be about 20 years old, though some only live for 15 years and others live to be 30 years old",
]

client = chromadb.Client()
collection = client.create_collection(name="docs")

# store each document in a vector embedding database
for i, d in enumerate(pages):
  response = ollama.embeddings(model="mxbai-embed-large", prompt=d)
  embedding = response["embedding"]
  collection.add(
    ids=[str(i)],
    embeddings=[embedding],
    documents=[d]
  )

for _,a in enumerate(['a','b','c']):
    print(_,a)
    print(['a','b','c'][_]