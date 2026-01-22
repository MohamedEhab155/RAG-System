from .Providers.QdrantProviders import QdrantProviders
from.Providers.PgVectorProviders import PgVectorProviders
from .VectorDBEnums import VectorDBEnums
from Contoroller.BaseContoroller import BaseContoroller
from sqlalchemy.orm import sessionmaker

class VectorDBProviderFactory:
    def __init__(self,config,db_client:sessionmaker=None):
            self.config = config
            self.base_controller = BaseContoroller()
            self.db_client = db_client

    def create(self, provider: str):
        if provider == VectorDBEnums.QDRANT.value:
            qdrant_db_client = self.base_controller.get_db_path(provider_name=self.config.VECTOR_DB_PATH)

            return QdrantProviders(
                db_path=qdrant_db_client,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
            )
        if provider == VectorDBEnums.PGVECTOR.value:
            return PgVectorProviders(
                db_client=self.db_client,
                distance_method=self.config.VECTOR_DB_DISTANCE_METHOD,
                default_vector_size=self.config.DEFAULT_VECTOR_SIZE ,
                index_threshold=self.config.VECTOR_DB_THRESHOLD_INDEXING
            )        
        return None 