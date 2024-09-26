#documentation about that module
#https://python.langchain.com/docs/how_to/document_loader_pdf/


from langchain_community.document_loaders import PyPDFLoader

def load_document(file_path):
    '''This function loads pdf file and returns vector db'''
    pass

file_path = 'uploads/NIPS-2017-attention-is-all-you-need-Paper.pdf'
loader = PyPDFLoader(
    file_path = file_path,
    #password = "my-pasword",
    extract_images = True,
    # headers = None
    # extraction_mode = "plain",
    # extraction_kwargs = None,
)

docs = []
a = loader.lazy_load()
for page in a:
    docs.append(a)
