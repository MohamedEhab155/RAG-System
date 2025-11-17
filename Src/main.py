from fastapi import FastAPI
from Routers import base, data
from motor.motor_asyncio import AsyncIOMotorClient
from Helper.config import  get_settings

app = FastAPI()

@app.on_event("startup")
async def startup_db_connection ():
    Setting=get_settings()
    app.mongo_connect=AsyncIOMotorClient(Setting.MONGODB_URL)
    app.db_client = app.mongo_connect[Setting.MONGODB_DATABASE]
 
@app.on_event("shutdown")
async def shutdown_db_client():
    app.mongo_connect.close()




app.include_router(base.base_router)
app.include_router(data.data_router)