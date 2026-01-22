from attr import dataclass
from .BaseContoroller import BaseContoroller
import os 
from langchain_community.document_loaders import PyMuPDFLoader,TextLoader
from .ProjectContoroller import ProjectContoroller 
from Models import ProcessingEnum
from langchain_text_splitters import RecursiveCharacterTextSplitter
from typing import List

@dataclass
class Document:
    page_content: str
    metadata: dict

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

        if not os.path.exists(file_path):
            return None


        if file_ext ==ProcessingEnum.TXT.value :
             return TextLoader(file_path, encoding="utf-8")
        
        if file_ext ==ProcessingEnum.TXT.value:
            return PyMuPDFLoader(file_path=file_path,encoding="utf-8")
        
        return None 
    
    def get_file_content (self,file_id): 

        file_content=self.get_file_load(file_id=file_id)
        
        if file_content :
            return file_content.load()
        return None 
     
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

        chunks = self.process_simpler_splitter(
            texts=file_content_texts,
            metadatas=file_content_metadata,
            chunk_size=chunk_size,
        )
        return chunks 

    def process_simpler_splitter(self, texts: List[str], metadatas: List[dict], chunk_size: int, splitter_tag: str="\n"):
        
        full_text = " ".join(texts)

        # split by splitter_tag
        lines = [ doc.strip() for doc in full_text.split(splitter_tag) if len(doc.strip()) > 1 ]

        chunks = []
        current_chunk = ""

        for line in lines:
            current_chunk += line + splitter_tag
            if len(current_chunk) >= chunk_size:
                chunks.append(Document(
                    page_content=current_chunk.strip(),
                    metadata={}
                ))

                current_chunk = ""

        if len(current_chunk) >= 0:
            chunks.append(Document(
                page_content=current_chunk.strip(),
                metadata={}
            ))

        return chunks
