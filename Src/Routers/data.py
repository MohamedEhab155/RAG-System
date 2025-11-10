from fastapi import APIRouter, UploadFile, Depends
from Helper.config import get_settings, Settings
from Contoroller.DataContoroller import DataContoroller
from Contoroller import ProjectContoroller 
import os 
from fastapi import UploadFile , status 
from fastapi.responses import JSONResponse 
import aiofiles
from Models import ResponseSignal
from Helper.config import get_settings, Settings
import logging

logger=logging.getLogger("uvicorn_error")

data_controller = DataContoroller()

data_router = APIRouter(prefix="/app/v2/data")
@data_router.post("/upload/{project_id}")
async def upload_data(project_id: str, file: UploadFile, app_setting: Settings = Depends(get_settings)):
    data_controller = DataContoroller()

    vaildate , msg = data_controller.vaildate(file)

    if vaildate==False:
        return JSONResponse (
            status_code=status.HTTP_400_BAD_REQUEST ,
            content= {
                "msg":msg
            }
        )
    
    project_dire_path=ProjectContoroller().get_project_path(project_id=project_id)

    file_path, file_id = data_controller.generate_unique_filepath(
        orig_file_name=file.filename,
        project_id=project_id
    )

    try:
        async with aiofiles.open(file_path, "wb") as f:
                while chunk := await file.read(app_setting.FILE_DEFAULT_CHUNK_SIZE):
                    await f.write(chunk)
    
    except Exception as e:

        logger.error(f"Error while uploading file: {e}")

        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.FILE_UPLOAD_FAILED.value
            }
        )
    return JSONResponse(
            content={
                "signal": ResponseSignal.FILE_UPLOAD_SUCCESS.value
                ,
                "file_id":file_id} 
                  )