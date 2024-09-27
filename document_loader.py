#documentation about that module
#https://python.langchain.com/docs/how_to/document_loader_pdf/
from sample_pdf_genarator import create_random_invoices
from langchain_community.document_loaders import PyPDFLoader
import ollama
import chromadb
import asyncio
from logger import  logger



class Vector_Storage:
    def __init__(self, model):
        self.pages = [] # store pages of Pdfs
        self.model = model
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(name="docs")
        #self.client.delete_collection(name='docs1')
        #self.collection = self.client.create_collection(name="docs1")

    async def load_data_pdf(self,path):
        loader = PyPDFLoader( file_path = path, extract_images=True )
        async for page in loader.alazy_load():
            self.pages.append(page)
        self.add_to_table()
    # store each document in a vector embedding database
    def add_to_table(self):
        for i, d in enumerate(self.pages):
            response = ollama.embeddings(model=self.model
                                         ,prompt=d.page_content)
            embedding = response["embedding"]
            self.collection.add(
                ids=[str(i)]
                , embeddings=[embedding]
                , metadatas=d.metadata
                , documents=d.page_content
            )

    def query_data(self,query,returned_document_count):
        human_question_response = ollama.embeddings(
            prompt=query,
            model=self.model
        )

        results = self.collection.query(
            query_embeddings=[human_question_response["embedding"]],
            n_results=returned_document_count
        )

        return results['documents']





#Sample Usage
#create_random_invoices(50)
ollama_model_name = 'mxbai-embed-large:latest'
file_path = 'uploads/invoices.pdf'
query = "What Steven Web bought from us"


b = Vector_Storage(model=ollama_model_name)

# Load the PDF asynchronously
asyncio.run(b.load_data_pdf(path=file_path))


#Query  db
b.query_data('Lake Davidmouth',5)
