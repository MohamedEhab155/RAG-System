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
    def insert_one(self, collection_name: str, text: list,vector:list, metadata: dict,record_id:int):
        pass


    @abstractmethod
    def insert_many(self, collection_name: str, texts: list,vectors:list, metadatas: list,record_id:int,batch_size: int = 50):
        pass

    def is_collection_existed(self, collection_name: str) -> bool:
        pass

    @abstractmethod
    def search_by_vector(self, collection_name: str, vector: list, limit: int):
        pass
    @abstractmethod
    def get_collection_info(self, collection_name: str) -> dict:
        return self.client.get_collection(collection_name=collection_name)