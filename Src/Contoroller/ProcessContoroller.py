from .BaseContoroller import BaseContoroller
import os 
from langchain_community.document_loaders import PyMuPDFLoader,TextLoader
from .ProjectContoroller import ProjectContoroller 
from Models import ProcessingEnum
from langchain_text_splitters import RecursiveCharacterTextSplitter
class processContoroller (BaseContoroller): 
    def __init__(self,project_id):
        super().__init__()

        self.project_id=project_id 
        self.path_file=ProjectContoroller().get_project_path(project_id=project_id)

    
    def get_file_extension(self,file_id):

        return os.path.splitext(file_id)[-1]
    
    def get_file_load (self,file_id): 
        file_ext=self.get_file_extension(file_id=file_id)
        file_path=os.path.join(self.path_file,file_id)

        if file_ext ==ProcessingEnum.TXT.value :
             return TextLoader(file_path, encoding="utf-8")
        
        if file_ext ==ProcessingEnum.TXT.value:
            return PyMuPDFLoader(file_path=file_path,encoding="utf-8")
        
        return None 
    
    def get_file_content (self,file_id): 

        file_content=self.get_file_load(file_id=file_id)

        return file_content.load()
     
    def process_file_content(self,file_content:list ,chunk_size,chunk_overlap,file_id):


        text_splitter  = RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
        file_content_texts = [
            rec.page_content
            for rec in file_content
        ]

        file_content_metadata = [
            rec.metadata
            for rec in file_content
        ]

        chunk =text_splitter.create_documents(file_content_texts,metadatas=file_content_metadata)

        return chunk 

    