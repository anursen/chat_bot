#documentation about that module
#https://python.langchain.com/docs/how_to/document_loader_pdf/
from langchain_community.document_loaders import PyPDFLoader
import ollama
import chromadb
import asyncio
from logger import  logger



class Mpsdlr:
    #Multi Page Single PDF Loader Retrieve
    def __init__(self, model):
        self.pages = [] # store pages of Pdfs
        self.model = model
        self.client = chromadb.Client()
        self.collection = self.client.create_collection(name="docs")

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

        return results
