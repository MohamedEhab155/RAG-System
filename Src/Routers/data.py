from fastapi import APIRouter, UploadFile, Depends
from Helper.config import get_settings, Settings
from Contoroller.DataContoroller import DataContoroller
from Contoroller import ProjectContoroller 
import os 
from fastapi import UploadFile , status , Request
from fastapi.responses import JSONResponse 
import aiofiles
from Models import ResponseSignal
from Helper.config import get_settings, Settings
from Routers.Schema.data import ProcessRequest
from Contoroller.ProcessContoroller import processContoroller
import logging
logger=logging.getLogger("uvicorn_error")
from Models.ProjectModel import ProjectModel
from Models.ChunkModel import ChunkModel 
from  Models.db_Schema.ChunkDtata import ChunkData
from Models.db_Schema.Assets import  Asset
from Models.Assets
data_controller = DataContoroller()

data_router = APIRouter(prefix="/app/v2/data")
@data_router.post("/upload/{project_id}")
async def upload_data(request: Request,project_id: str, file: UploadFile, app_setting: Settings = Depends(get_settings)):
    data_controller = DataContoroller()

    project_model=await ProjectModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_create_one(
        project_id=project_id ) 

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
                "file_id":file_id,
                
                "project_id":str(project.id)
                  
                  } 
                  )

@data_router.post("/process/{project_id}")
async def process(project_id,process_request:ProcessRequest,request:Request):
     
    chunk_size=process_request.chunk_size
    overlap_size=process_request.overlap_size
    file_id=process_request.file_id
    do_reset=process_request.do_reset


    project_model=await ProjectModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_create_one(
    project_id=project_id ) 
    

    processing_file=processContoroller(project_id=project_id)

    file_content=processing_file.get_file_content(file_id=process_request.file_id)

    file_chunks =processing_file.process_file_content(file_content,chunk_size,overlap_size,file_id) 

    if file_chunks is None or len(file_chunks) == 0:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseSignal.PROCESSING_FAILED.value
            }
        )
    

    file_chunks_records = [
        ChunkData(
            chunk_text=chunk.page_content,
            chunk_meta_data=chunk.metadata,
            chunk_order=i+1,
            chunk_project_id=project.id,
        )
        for i, chunk in enumerate(file_chunks)
    ]

    chunk_model=await ChunkModel.create_instance(request.app.db_client)
    if do_reset == 1:
        _ = await chunk_model.delete_chunks_by_project_id(
            project_id=project.id
        )

    no_records = await chunk_model.insert_many_chunks(chunks=file_chunks_records)

    return JSONResponse(
        content={
            "signal": ResponseSignal.PROCESSING_SUCCESS.value,
            "inserted_chunks": no_records
        }
    )