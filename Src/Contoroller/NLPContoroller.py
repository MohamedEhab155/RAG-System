from .BaseContoroller import BaseContoroller 
from models.db_Schema import Project,ChunkData
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
    
    def create_collection_name(self, project_id: str):
        return f"collection_{self.vectordb_client.default_vector_size}_{project_id}".strip()

    async def index_into_vector_db(self,project:Project,chunks:List[ChunkData], chunks_ids: List[int],do_reset:bool=False): 
        coollection_name= self.create_collection_name(project_id=project.project_id)

        texts=[
        c.chunk_text   for c in chunks
        ]

        metadata=[
            m.chunk_meta_data
            for m in chunks
        ]
        vectors =  self.embedding_client.embed_text(texts=texts,document_type=DocumentTypeEnum.DOCUMENT.value)
        await self.vectordb_client.CreateCollection(coollection_name,self.embedding_client.embedding_size)
        _=await self.vectordb_client.insert_many(coollection_name,texts,vectors,metadata,chunks_ids)



        return True 
    


    async def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)

        if not self.vectordb_client.is_collection_existed(collection_name):
            await self.vectordb_client.CreateCollection(collection_name, self.embedding_client.embedding_size)

        collection_info = await self.vectordb_client.get_collection_info(collection_name=collection_name)

        return json.loads(
            json.dumps(collection_info, default=lambda x: x.__dict__)
        )


    async def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):
        collection_name = self.create_collection_name(project_id=project.project_id)
        quary_vector=None

        if not await self.vectordb_client.is_collection_existed(collection_name):
            await self.vectordb_client.CreateCollection(collection_name, self.embedding_client.embedding_size)

        vector = self.embedding_client.embed_text(
            texts=text,
            document_type=DocumentTypeEnum.QUERY.value
        )

        if not vector or len(vector) == 0:
            return False
        if isinstance(vector, list):
            quary_vector = vector[0]
        
        if not quary_vector:
            return False
        

        results = await self.vectordb_client.search_by_vector(
            collection_name=collection_name,
            vector=quary_vector,
            limit=limit
        )

        return json.loads(
            json.dumps(results, default=lambda x: x.__dict__)
        )


    async def answer_rag_question (self,project,query,limit:int=5):

        answer, full_prompt, chat_history = None, None, None

        results= await self.search_vector_db_collection(project=project,text=query)
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