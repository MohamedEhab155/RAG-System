from fastapi import FastAPI
from Routers import base, data,NLP
from motor.motor_asyncio import AsyncIOMotorClient
from Helper.config import get_settings
from Stores.LLM.LLMProviderFactory import LLMProviderFactory
from Stores.VectorDB.VectorDBProviderFactory import VectorDBProviderFactory

app = FastAPI()

async def startup_span():
    settings = get_settings()
    app.mongo_conn = AsyncIOMotorClient(settings.MONGO_URL)
    app.db_client = app.mongo_conn[settings.MONGODB_DATABASE]

    # define factory 
    llm_provider_factory = LLMProviderFactory(settings)
    vectordb_provider_factory=VectorDBProviderFactory(settings)

    
    app.generation_client = llm_provider_factory.create(provider=settings.GENERATION_BACKEND)
    app.generation_client.set_generation_model(model_id = settings.GENERATION_MODEL_ID)

   
    app.embedding_client = llm_provider_factory.create(provider=settings.EMBEDDING_BACKEND)
    app.embedding_client.set_embedding_model(model_id=settings.EMBEDDING_MODEL_ID,
                                             embedding_size=settings.EMBEDDING_MODEL_SIZE)
    

    app.vectordb_client=vectordb_provider_factory.create(provider=settings.VECTOR_DB_BACKEND)
    app.vectordb_client.connection()

async def shutdown_span():
    app.mongo_conn.close()

    app.vectordb_client.disconnection()
app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(NLP.nlp_router)