from .BaseContoroller import BaseContoroller 
from Models.db_Schema.Project import Project 
from Models.db_Schema.ChunkDtata import ChunkData
from typing import List
from Stores.LLM.LLMSEnums import DocumentTypeEnum
import json
class NLPContoroller(BaseContoroller):
    def __init__(self,generation_client,embedding_client,vectordb_client,TempleteParser):
        super().__init__()

        self.generation_client=generation_client 
        self.embedding_client=embedding_client
        self.vectordb_client=vectordb_client 
        self.TempleteParser=TempleteParser
    
    def collection_name(self,project_id):
        return f"collection_{project_id}".strip()


    def index_into_vector_db(self,project:Project,chunks:List[ChunkData], chunks_ids: List[int],do_reset:bool=False): 
        coollection_name=self.collection_name(project_id=project.project_id)

        texts=[
        c.chunk_text   for c in chunks
        ]

        metadata=[
            m.chunk_meta_data
            for m in chunks
        ]

        vectors = [
            self.embedding_client.embed_text(text=text, 
                                             document_type=DocumentTypeEnum.DOCUMENT.value)
            for text in texts
        ]
        self.vectordb_client.CreateCollection(coollection_name,self.embedding_client.embedding_size)
        _=self.vectordb_client.insert_many(coollection_name,texts,vectors,metadata,chunks_ids)



        return True 
    


    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.collection_name(project_id=project.project_id)

        if not self.vectordb_client.is_collection_existed(collection_name):
            self.vectordb_client.CreateCollection(collection_name, self.embedding_client.embedding_size)

        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )


    def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):
        collection_name = self.collection_name(project_id=project.project_id)

        if not self.vectordb_client.is_collection_existed(collection_name):
            self.vectordb_client.CreateCollection(collection_name, self.embedding_client.embedding_size)

        vector = self.embedding_client.embed_text(
            text=text, 
            document_type=DocumentTypeEnum.QUERY.value
        )

        if not vector or len(vector) == 0:
            return False

        results = self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=vector,
            limit=limit
        )

        return json.loads(
            json.dumps(results, default=lambda x: x.__dict__)
        )


    def answer_rag_question (self,project,query,limit:int=5):

        answer, full_prompt, chat_history = None, None, None

        results=self.search_vector_db_collection(project=project,text=query)
        documents = [
            {
                "data": result["text"]
            }
            for result in results
        ]


        print ("retrieved_documents:",documents)


        if not documents or len(documents)==0:
            return None 
        
        system_prompt=self.TempleteParser.get(group="rag",key="system_prompt")


      #  documents = "\n".join([
       ##            "doc_num": idx + 1,
           #         "chunk_text": doc["text"],
         ##   })
           # for idx, doc in enumerate(retrieved_documents)
        #])


        prompt=query
        footer_prompt = self.TempleteParser.get("rag", "footer_prompt", {
            "query": query
        })
        full_prompt = prompt + "\n\n" + footer_prompt

        # step4: Retrieve the Answer
        answer = self.generation_client.generate_text(
             prompt=full_prompt,
             system_message=system_prompt,
             documents=documents
           
        )

        return answer, full_prompt, chat_history