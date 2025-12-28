import asyncio
from fastapi import FastAPI
from Routers import base, data,NLP
from Helper.config import get_settings
from Stores.LLM.LLMProviderFactory import LLMProviderFactory
from Stores.VectorDB.VectorDBProviderFactory import VectorDBProviderFactory
from Stores.LLM import TempleteParser
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
app = FastAPI()

async def startup_span():
    settings = get_settings()
    
    postgres_conn = f"postgresql+asyncpg://{settings.POSTGRES_USERNAME}:{settings.POSTGRES_PASSWORD}@{settings.POSTGRES_HOST}:{settings.POSTGRES_PORT}/{settings.POSTGRES_MAIN_DATABASE}"

    app.db_engine = create_async_engine(postgres_conn)
    app.db_client = sessionmaker(
        bind=app.db_engine,
        class_=asyncio.Future,
        expire_on_commit=False,
    )

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

    
    app.template_parser = TempleteParser(
        language=settings.PRIMARY_LANG,
        default_language=settings.DEFAULT_LANG,
    )

async def shutdown_span():
    app.db_engine.dispose()
    app.vectordb_client.disconnection()

    
app.on_event("startup")(startup_span)
app.on_event("shutdown")(shutdown_span)

app.include_router(base.base_router)
app.include_router(data.data_router)
app.include_router(NLP.nlp_router)