#documentation about that module
#This is multiple_page_single_pdf_loader_retriever 

#https://python.langchain.com/docs/how_to/document_loader_pdf/
from langchain_community.document_loaders import PyPDFLoader
import ollama
import chromadb
from langchain_chroma import Chroma
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from utils.logger import  logger

class Mpsdlr:
    #Multi Page Single PDF Loader Retrieve
    def __init__(self, model,user_id):
        self.model = model
        self.client = chromadb.Client()
        self.table = self.client.get_or_create_collection(name=user_id)
        logger.critical(f"Mpsdlr object created {user_id}")

    def load_data_pdf(self,path):
        loader = PyPDFLoader( file_path = path, extract_images=True )
        self.pages = loader.lazy_load()
        self.add_to_table()
    # store each document in a vector embedding database
    def add_to_table(self):
        for i, d in enumerate(self.pages):
            response = ollama.embeddings(model=self.model
                                         ,prompt=d.page_content)
            embedding = response["embedding"]
            self.table.add(
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

        results = self.table.query(
            query_embeddings=[human_question_response["embedding"]],
            n_results=returned_document_count
        )

        return results

        #
    def return_retriever(self,path):
        '''This is the default function to return a a table as a retriver object
        This returns a chainable object.'''
        loader = PyPDFLoader( file_path = path, extract_images=True )
        docs = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        splits = text_splitter.split_documents(docs)
        vectorstore = Chroma.from_documents(documents=splits, embedding=OpenAIEmbeddings())
        self.retriever = vectorstore.as_retriever()
        return self.retriever

#TODO Seems like this retriever is loading data two times.
