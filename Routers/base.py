from fastapi import APIRouter 
import os 
base_router =APIRouter(prefix='/base/v1',
                       tags=['base1'])


@base_router.get("/")         # cheak healthy 
async def welcome():
    app_name=os.getenv('APP_NAME')
    app_version =os.getenv('APP_VERSION')

    return {
        "app_name": app_name,
        "app_version": app_version
    }