from Stores.VectorDB.VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
from qdrant_client import  models ,QdrantClient
import logging
class QdrantProviders(VectorDBInterface):
    def __init__(self,distance_method,db_path):
        self.db_path=db_path
        self.client=None


        
        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        logger=logging.getLogger(__name__)
    def connection(self):
        self.client=QdrantClient(path=self.db_path)

    def disconnection(self):
        return NotImplemented

    def CreateCollection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if self.client is None :
            logging.error("client is was not found")
        

        if do_reset ==True:
            self.delete_collection(collection_name=collection_name)
        
        if not self.is_collection_existed:
            self.client.create_collection(
            collection_name="{collection_name}",
            vectors_config=models.VectorParams(size=embedding_size, distance=self.distance_method),)
            return True
        return False


    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name="{collection_name}")


    def delete_collection(self, collection_name: str):
        if self.client is None :
            logging.error("client is was not found")
        self.client.delete_collection(collection_name="{collection_name}")
        
    def list_all_collections(self) -> list:
       return self.client.get_collections()

    def insert_one(self, collection_name: str, text: list,vector:list, metadata: dict,record_id:int):
        try:
         self.client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=record_id, 
                    vector=vector,
                    payload={
                        "text": text,
                        "metadata": metadata
                    }
                )
            ]
        )
        except Exception as e:
            self.logger.error(f"Error while inserting record: {e}")
            return False

        return True

    def insert_many(self, collection_name: str, texts: list,vectors:list, metadatas: list=None,record_id:int=None,batch_size: int = 50):
       if metadata is None:
        metadata = [None] * len(texts)

        if record_ids is None:
            record_ids = [None] * len(texts)

        for i in range(0, len(texts), batch_size):
            batch_end = i + batch_size

            batch_texts = texts[i:batch_end]
            batch_vectors = vectors[i:batch_end]
            batch_metadata = metadata[i:batch_end]
            batch_ids = record_ids[i:batch_end]

            batch_points = [
                models.PointStruct(
                    id=batch_ids[x],  # None → Qdrant يولد تلقائي
                    vector=batch_vectors[x],
                    payload={
                        "text": batch_texts[x],
                        "metadata": batch_metadata[x]
                    }
                )
                for x in range(len(batch_texts))
            ]

            try:
                self.client.upsert(
                    collection_name=collection_name,
                    points=batch_points
                )
            except Exception as e:
                self.logger.error(f"Error while inserting batch: {e}")
                return False

       return True

    def search_by_vector(self, collection_name: str, vector: list, limit: int):
        
        return self.client.search_points(
            collection_name="collection_name",
            query_vector=vector,
            limit=5
        )