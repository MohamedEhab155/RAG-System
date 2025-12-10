from fastapi import APIRouter , Response,Request ,status
from Models.ProjectModel import ProjectModel
from Models.ChunkModel import ChunkModel
import logging 
from Contoroller import NLPContoroller
from fastapi.responses import JSONResponse
from Models.Enums import ResponseEnums
from .Schema.nlp import PushRequest,SearchRequest
logger=logging.getLogger("uvicorn_error")

nlp_router=APIRouter(prefix="/app/v2/nlp")

@nlp_router.post("/index/push/{project_id}")
async def index_project (project_id:str , request: Request,PushRequest:PushRequest):
    project_model=await ProjectModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_create_one(
    project_id=project_id ) 


    chunk_model=await ChunkModel.create_instance(request.app.db_client)
    
    nlp_controller = NLPContoroller(
            vectordb_client=request.app.vectordb_client,
            generation_client=request.app.generation_client,
            embedding_client=request.app.embedding_client,
        )
    if not project:
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseEnums.ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
                }
            )
    
    
    has_records=True
    page_no=1
    idx=0
    inserted_items_count=0
    while has_records :
        page_chunks=await chunk_model.get_poject_chunks(project_id=project.id,page_no=page_no)   

        if len(page_chunks):
            page_no += 1
        
        if not page_chunks or len(page_chunks) == 0:
            has_records = False
            break
        

        chunk_idx=list(range(idx,idx+len(page_chunks)))
        idx+=len(page_chunks)      

        is_inserted=nlp_controller.index_into_vector_db(project=project,chunks=page_chunks,chunks_ids=chunk_idx,do_reset=PushRequest.do_reset)

        if is_inserted==False:

            return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST
                                ,content={
                                    "single":ResponseEnums.ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
                                })
        inserted_items_count += len(page_chunks)
    
    return JSONResponse(content={

        "single":ResponseEnums.ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
        "inserted_items_count":inserted_items_count
    })



@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(project_id:str , request: Request):
    project_model=await ProjectModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_create_one(
    project_id=project_id ) 


    
    nlp_controller = NLPContoroller(
            vectordb_client=request.app.vectordb_client,
            generation_client=request.app.generation_client,
            embedding_client=request.app.embedding_client,
        )

    collection_info = nlp_controller.get_vector_db_collection_info(project=project)
    
    return JSONResponse(
        content={
            "signal": ResponseEnums.ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )

   
    

@nlp_router.post("/index/search/{project_id}")
async def search_index(project_id:str , request: Request, search_request: SearchRequest):
    
    project_model = await ProjectModel.create_instance(
        db_client=request.app.db_client
    )

    project = await project_model.get_project_or_create_one(
        project_id=project_id
    )

    
    nlp_controller = NLPContoroller(
            vectordb_client=request.app.vectordb_client,
            generation_client=request.app.generation_client,
            embedding_client=request.app.embedding_client,
        )

    results = nlp_controller.search_vector_db_collection(
        project=project, text=search_request.text, limit=search_request.limit
    )

    if not results:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseEnums.ResponseSignal.VECTORDB_SEARCH_ERROR.value
                }
            )
    
    return JSONResponse(
    content={
        "signal": ResponseEnums.ResponseSignal.VECTORDB_SEARCH_SUCCESS.value,
         "results" : results 
          
           }
    )  