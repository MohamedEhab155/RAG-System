from abc import ABC , abstractmethod 


class VectorDBInterface(ABC): 
    

    @abstractmethod
    def connection(self):
        pass

    @abstractmethod
    def disconnection(self):
        pass

    @abstractmethod 
    def CreateCollection(self, collection_name: str, embedding_size: int,do_reset: bool = False):
        pass

    @abstractmethod
    def delete_collection(self, collection_name: str):
        pass

    @abstractmethod
    def list_all_collections(self) -> list:
        pass

    @abstractmethod
    def insert_one(self, collection_name: str, embedding: list, metadata: dict):
        pass


    @abstractmethod
    def insert_many(self, collection_name: str, embeddings: list, metadatas: list,batch_size: int = 50):
        pass

    @abstractmethod
    def search_by_vector(self, collection_name: str, vector: list, limit: int):
        pass
    
    