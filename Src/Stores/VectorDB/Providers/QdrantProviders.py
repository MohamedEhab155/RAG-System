from qdrant_client import QdrantClient, models
import logging
from Stores.VectorDB.VectorDBInterface import VectorDBInterface
from ..VectorDBEnums import DistanceMethodEnums
from Models.db_Schema.ChunkDtata import RetrievedDocument

class QdrantProviders(VectorDBInterface):
    def __init__(self, distance_method, db_path):
        self.db_path = db_path
        self.client = None

        if distance_method == DistanceMethodEnums.COSINE.value:
            self.distance_method = models.Distance.COSINE
        elif distance_method == DistanceMethodEnums.DOT.value:
            self.distance_method = models.Distance.DOT

        self.logger = logging.getLogger(__name__)

    def connection(self):
        self.client = QdrantClient(path=self.db_path)

    def disconnection(self):
        return NotImplemented

    def CreateCollection(self, collection_name: str, embedding_size: int, do_reset: bool = False):
        if self.client is None:
            self.logger.error("Client is not initialized")
            return False

        # reset collection
        if do_reset and self.is_collection_existed(collection_name):
            self.delete_collection(collection_name)

        # create if not exist:
        if not self.is_collection_existed(collection_name):
            self.client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=embedding_size,
                    distance=self.distance_method
                ),
            )
            return True

        return True  # collection already exists

    def is_collection_existed(self, collection_name: str) -> bool:
        return self.client.collection_exists(collection_name=collection_name)

    def delete_collection(self, collection_name: str):
        self.client.delete_collection(collection_name=collection_name)
        return True

    def list_all_collections(self):
        return self.client.get_collections()

    def insert_one(self, collection_name: str, text: str, vector: list, metadata: dict, record_id: int):
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

    def insert_many(self, collection_name: str, texts: list, vectors: list, metadatas=None, record_ids=None, batch_size=50):
        if metadatas is None:
            metadatas = [None] * len(texts)
        if record_ids is None:
            record_ids = [None] * len(texts)

        for i in range(0, len(texts), batch_size):
            batch_points = []
            for j in range(i, min(i+batch_size, len(texts))):
                batch_points.append(
                    models.PointStruct(
                        id=record_ids[j],
                        vector=vectors[j],
                        payload={
                            "text": texts[j],
                            "metadata": metadatas[j]
                        }
                    )
                )

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
        results= self.client.query_points(
            collection_name=collection_name,
            query=vector,
            limit=limit,
            with_payload=True
        )
            

      

        return [
            RetrievedDocument(
                score=point.score,       
                text=point.payload["text"]  
            )
            for point in results.points     
        ]
    def get_collection_info(self, collection_name: str):
        return self.client.get_collection(collection_name=collection_name)
