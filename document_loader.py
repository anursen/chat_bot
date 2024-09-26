#documentation about that module
#https://python.langchain.com/docs/how_to/document_loader_pdf/
from sample_pdf_genarator import create_random_invoices
from langchain_community.document_loaders import PyPDFLoader
import ollama
import chromadb

create_random_invoices(50)
model_name = 'mxbai-embed-large:latest'

def load_document(file_path):
    '''This function loads pdf file and returns vector db'''
    pass

file_path = 'uploads/invoices.pdf'
loader = PyPDFLoader(
    file_path = file_path
    ,extract_images = True
    )

loader = PyPDFLoader(file_path)
pages = []
async for page in loader.alazy_load():
    pages.append(page)


client = chromadb.Client()
collection = client.create_collection(name="docs")

# store each document in a vector embedding database
for i, d in enumerate(pages):
  response = ollama.embeddings(model = model_name
                              ,prompt = d.page_content)
  embedding = response["embedding"]
  collection.add(
    ids=[str(i)]
    ,embeddings=[embedding]
    ,metadatas=d.metadata
    ,documents=d.page_content
  )


22222222222222222

# an example prompt
prompt = "What Steven Web bought from us"

# generate an embedding for the prompt and retrieve the most relevant doc
response = ollama.embeddings(
  prompt=prompt,
  model=model_name
)

results = collection.query(
  query_embeddings=[response["embedding"]],
  n_results=10
)

data = results['documents'][0][0]
data
results
