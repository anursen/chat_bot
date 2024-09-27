#documentation about that module
#https://python.langchain.com/docs/how_to/document_loader_pdf/
from sample_pdf_genarator import create_random_invoices
from langchain_community.document_loaders import PyPDFLoader
import ollama
import chromadb
#from logger import  logger

#create_random_invoices(50)

class Vector_Storage:
    def __init__(self, model, path):
        self.pages = [] # store pages of Pdfs
        self.model = model
        self.path = path
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(name="docs")

    async def load_data_pdf(self):
        ''' load pdfs to the loader '''
        loader = PyPDFLoader( file_path=self.path, extract_images=True )
        async for page in loader.alazy_load():
            self.pages.append(page)
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





ollama_model_name = 'mxbai-embed-large:latest'
file_path = 'uploads/invoices.pdf'
query = "What Steven Web bought from us"

a = Vector_Storage(model=ollama_model_name,path=file_path)

