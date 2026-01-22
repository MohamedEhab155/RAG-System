from typing import List
import json
from Models.db_Schema.minirag.schemes.ChunkData import RetrievedDocument
from ..VectorDBInterface import VectorDBInterface 
from ..VectorDBEnums import (VectorDBEnums, PgVectorDistanceMethodEnums, 
                             PgVectorTableSchemeEnums,PgVectorIndexTypeEnums,DistanceMethodEnums)

from sqlalchemy import  text as sql_text 
import logging


class PgVectorProviders(VectorDBInterface):
    def __init__(self,db_client,distance_method: str,index_threshold=100,default_vector_size:int = 768,index_type:str =PgVectorIndexTypeEnums.HNSW.value):
        super().__init__()

        self.db_client=db_client 
        self.default_vector_size=default_vector_size
        self.index_type=index_type
        self.prefix=PgVectorTableSchemeEnums._PREFIX.value
        self.logger=logging.getLogger("uvicorn")
        self.default_index_name=lambda collection_name: f"{collection_name}_vector_index"
        self.index_threshold=index_threshold

        if distance_method == DistanceMethodEnums.COSINE.value:
            distance_method = PgVectorDistanceMethodEnums.COSINE.value
        elif distance_method == DistanceMethodEnums.DOT.value:
            distance_method = PgVectorDistanceMethodEnums.DOT.value
        self.distance_method = distance_method

    async def connection(self):
        async with self.db_client() as session:
            async with session.begin() :
                await session.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))

    async def disconnection(self):
        pass


    async def is_collection_existed(self, collection_name: str) -> bool:
        async with self.db_client()as session:
            async with session.begin(): 

                list_table=sql_text("SELECT * FROM pg_tables WHERE tablename= :collection_name")
                resulte = await session.execute(list_table,{"collection_name":collection_name})
                record = resulte.scalar_one_or_none()
        
        return record 
    
    async def list_all_collections(self) -> list:

        records=[]
        async with self.db_client()as session:
            async with session.begin():
                list_tabel=sql_text ("SELECT tablename FROM pg_tables WHERE tablename  LIKE :prefix ")
                resulte = await session.execute(list_tabel,{"prefix":self.prefix})

                records=resulte.scalars().all()
        
        return records 




    async def get_collection_info(self, collection_name: str) -> dict:
        async with self.db_client() as session:
            async with session.begin():

                table_info_sql = sql_text("""
                    SELECT schemaname, tablename, tableowner, tablespace, hasindexes
                    FROM pg_tables
                    WHERE schemaname = 'public'
                    AND tablename = :collection_name
                """)

                table_info = await session.execute(
                    table_info_sql,
                    {"collection_name": collection_name}
                )

                table_data = table_info.fetchone()
                if not table_data:
                    return None   

         
                count_sql = sql_text(
                    f'SELECT COUNT(*) FROM public."{collection_name}"'
                )

                record_count = await session.execute(count_sql)

                return {
                    "table_info": {
                        "schemaname": table_data[0],
                        "tablename": table_data[1],
                        "tableowner": table_data[2],
                        "tablespace": table_data[3],
                        "hasindexes": table_data[4],
                    },
                    "record_count": record_count.scalar_one(),
                }

       

    async def delete_collection(self, collection_name: str):
        async with self.db_client() as session:
            async with session.begin():
                self.logger.info(f"Deleting collection: {collection_name}")

                delete_sql = sql_text(f'DROP TABLE IF EXISTS {collection_name}')
                await session.execute(delete_sql)
        
        return True

    async def CreateCollection(self, collection_name: str, embedding_size: int,do_reset: bool = False):
         if do_reset:
                    _=self.delete_collection(collection_name=collection_name)
                
         is_exited = await self.is_collection_existed(collection_name=collection_name)

         if not is_exited : 
             self.logger.info(f"Creating collection: {collection_name}")
             async with self.db_client() as session:
                async with session.begin():
                    # ensure pgvector extension is available before creating tables
                    await session.execute(sql_text("CREATE EXTENSION IF NOT EXISTS vector"))
                    create_sql = sql_text(
                        f'CREATE TABLE {collection_name} ('
                            f'{PgVectorTableSchemeEnums.ID.value} bigserial PRIMARY KEY,'
                            f'{PgVectorTableSchemeEnums.TEXT.value} text, '
                            f'{PgVectorTableSchemeEnums.VECTOR.value} vector({embedding_size}), '
                            f'{PgVectorTableSchemeEnums.METADATA.value} jsonb DEFAULT \'{{}}\', '
                            f'{PgVectorTableSchemeEnums.CHUNK_ID.value} integer, '
                            f'FOREIGN KEY ({PgVectorTableSchemeEnums.CHUNK_ID.value}) REFERENCES chunk_data(chunk_id)'
                        ')'
                    )
                    await session.execute(create_sql)
             return True
         return False
    

    async def is_index_existed(self, collection_name: str) -> bool:
        index_name = self.default_index_name(collection_name)
        async with self.db_client() as session:
            async with session.begin():
                index_check_sql = sql_text(
                         """ 
                        SELECT 1 
                        FROM pg_indexes 
                        WHERE tablename = :collection_name
                        AND indexname = :index_name
                                    """)
                
                result = await session.execute(index_check_sql, {"collection_name": collection_name, "index_name": index_name})
                return bool(result.scalar_one_or_none())
    
    
    async def create_vector_index(self, collection_name: str,
                                        index_type: str = PgVectorIndexTypeEnums.HNSW.value):
        is_index_existed = await self.is_index_existed(collection_name=collection_name)
        if is_index_existed:
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                count_sql = sql_text(f'SELECT COUNT(*) FROM {collection_name}')
                result = await session.execute(count_sql)
                records_count = result.scalar_one()

                if records_count < self.index_threshold:
                    return False
                
                self.logger.info(f"START: Creating vector index for collection: {collection_name}")
                
                index_name = self.default_index_name(collection_name)
                create_idx_sql = sql_text(
                                            f'CREATE INDEX {index_name} ON {collection_name} '
                                            f'USING {index_type} ({PgVectorTableSchemeEnums.VECTOR.value} {self.distance_method})'
                                          )

                await session.execute(create_idx_sql)

                self.logger.info(f"END: Created vector index for collection: {collection_name}")

    async def insert_one(self, collection_name: str, text: list,vector:list, metadata: dict,record_id:int):

        is_exited = await self.is_collection_existed(collection_name=collection_name)
        if not is_exited :
             self.logger.error(f"Collection {collection_name} does not exist.")
             return False
        
        if not record_id :
            self.logger.error(f"Record ID is  non found , it is required for insertion.")
            return False
        
        async with self.db_client() as session:
            async with session.begin():
                insert_sql = sql_text(
                    f'INSERT INTO {collection_name} '
                    f'({PgVectorTableSchemeEnums.TEXT.value}, {PgVectorTableSchemeEnums.VECTOR.value}, '
                    f'{PgVectorTableSchemeEnums.METADATA.value}, {PgVectorTableSchemeEnums.CHUNK_ID.value}) '
                    f'VALUES (:text, :vector, :metadata, :chunk_id)'
                )

                metadata=json.dumps(metadata,ensure_ascii=False) if metadata is not None else json.dumps({},ensure_ascii=False)
                await session.execute(insert_sql, {
                    "text": text,
                    "vector": "["+ ",".join([str(v)  for v in vector]) +"]",
                    "metadata": metadata,
                    "chunk_id": record_id
                })
                await session.commit()
            await self.create_vector_index(collection_name=collection_name)
        return True


                    
    async def insert_many(self, collection_name: str, texts: list,vectors:list, metadatas: list,record_id:int,batch_size: int = 50):

        is_exited = await self.is_collection_existed(collection_name=collection_name)
        if not is_exited :
             self.logger.error(f"Collection {collection_name} does not exist.")
             return False

        if len (record_id) != len(vectors):
            self.logger.error(f"Record ID length {len(record_id)} does not match vectors length {len(vectors)}.")
            return False
        
        async with self.db_client() as session:
            async with session.begin():

                for start_idx in range(0, len(vectors), batch_size):
                    end_idx = min(start_idx + batch_size, len(vectors))
                    batch_texts = texts[start_idx:end_idx]
                    batch_vectors = vectors[start_idx:end_idx]
                    batch_metadatas = metadatas[start_idx:end_idx]
                    batch_record_ids = record_id[start_idx:end_idx]

                    values=[]

                    for  _text, _vector, _metadata, _chunk_id in zip(batch_texts,batch_vectors,batch_metadatas,batch_record_ids):

                        _metadata=json.dumps(_metadata,ensure_ascii=False) if _metadata is not None else json.dumps({},ensure_ascii=False)
                        values.append(
                            {"text": _text,
                             "vector": "["+ ",".join([str(v)  for v in _vector]) +"]",
                             "metadata":_metadata ,
                             "chunk_id": _chunk_id
                            }
                        )
                    batch_insert_sql = sql_text(f'INSERT INTO {collection_name} '
                                    f'({PgVectorTableSchemeEnums.TEXT.value}, '
                                    f'{PgVectorTableSchemeEnums.VECTOR.value}, '
                                    f'{PgVectorTableSchemeEnums.METADATA.value}, '
                                    f'{PgVectorTableSchemeEnums.CHUNK_ID.value}) '
                                    f'VALUES (:text, :vector, :metadata, :chunk_id)')
                        
                    await session.execute(batch_insert_sql,values)
            await self.create_vector_index(collection_name=collection_name)

            
            return True 
    async def search_by_vector(self, collection_name: str, vector: list, limit: int)->List [RetrievedDocument]:

        if not await self.is_collection_existed(collection_name=collection_name):
             self.logger.error(f"Collection {collection_name} does not exist.")
             return []
        
        vector = "[" + ",".join([ str(v) for v in vector ]) + "]"

        async with self.db_client() as session:
            search_sql = sql_text(f"""
                SELECT
                    {PgVectorTableSchemeEnums.TEXT.value} AS text,
                    1 - ({PgVectorTableSchemeEnums.VECTOR.value} <=> :vector) AS score
                FROM {collection_name}
                ORDER BY score DESC
                LIMIT :limit
            """)

            result = await session.execute(
                search_sql,
                {"vector": vector, "limit": limit}
            )

            records = result.fetchall()

            return [
                RetrievedDocument(
                    text=record.text,
                    score=record.score
                )
                for record in records
            ]
