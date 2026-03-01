from fastapi import APIRouter , Response,Request ,status
from models.ProjectModel import ProjectModel
from models.ChunkModel import ChunkModel
import logging 
from Contoroller import NLPContoroller
from fastapi.responses import JSONResponse
from models.Enums import ResponseEnums
from .Schema.nlp import PushRequest,SearchRequest
from tqdm.auto import tqdm
logger=logging.getLogger("uvicorn_error")

nlp_router=APIRouter(prefix="/app/v2/nlp")

@nlp_router.post("/index/push/{project_id}")
async def index_project (project_id:int , request: Request,PushRequest:PushRequest):
    project_model=await ProjectModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_create_one(
    project_id=project_id ) 
    
    page_no = 1
    has_records = True
    idx=0
    inserted_items_count = 0

    chunk_model=await ChunkModel.create_instance(request.app.db_client)
    
    if not project:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "signal": ResponseEnums.ResponseSignal.PROJECT_NOT_FOUND_ERROR.value
            }
        )
    
    nlp_controller = NLPContoroller(
            vectordb_client=request.app.vectordb_client,
            generation_client=request.app.generation_client,
            embedding_client=request.app.embedding_client,
            TempleteParser=request.app.template_parser
        )

    chunk_count=await chunk_model.count_project_chunks(project_id=project.project_id)
    pbar=tqdm(total=chunk_count,desc=f"Indexing Project ID:{project.project_id} into Vector DB",position=0)
    while has_records:
            page_chunks = await chunk_model.get_project_chunks(project_id=project.project_id, page_no=page_no)
            if len(page_chunks):
                page_no += 1
            
            if not page_chunks or len(page_chunks) == 0:
                has_records = False
                break

            chunks_ids =  [ c.chunk_id for c in page_chunks ]
            idx += len(page_chunks)
            
            is_inserted = await nlp_controller.index_into_vector_db(
                project=project,
                chunks=page_chunks,
                chunks_ids=chunks_ids
            )

            if not is_inserted:
                return JSONResponse(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    content={
                        "signal": ResponseEnums.ResponseSignal.INSERT_INTO_VECTORDB_ERROR.value
                    }
                )

            pbar.update(len(page_chunks))
            inserted_items_count += len(page_chunks)
            
    return JSONResponse(
            content={
                "signal": ResponseEnums.ResponseSignal.INSERT_INTO_VECTORDB_SUCCESS.value,
                "inserted_items_count": inserted_items_count
            }
        )




@nlp_router.get("/index/info/{project_id}")
async def get_project_index_info(project_id:int , request: Request):
    project_model=await ProjectModel.create_instance(request.app.db_client)
    project = await project_model.get_project_or_create_one(
    project_id=project_id ) 


    
     
    nlp_controller = NLPContoroller(
            vectordb_client=request.app.vectordb_client,
            generation_client=request.app.generation_client,
            embedding_client=request.app.embedding_client,
            TempleteParser=request.app.template_parser
        )

    collection_info = await nlp_controller.get_vector_db_collection_info(project=project)
    
    return JSONResponse(
        content={
            "signal": ResponseEnums.ResponseSignal.VECTORDB_COLLECTION_RETRIEVED.value,
            "collection_info": collection_info
        }
    )

   
    

@nlp_router.post("/index/search/{project_id}")
async def search_index(project_id:int , request: Request, search_request: SearchRequest):
    
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
            TempleteParser=request.app.template_parser
        )

    results = await nlp_controller.search_vector_db_collection(
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
    })  



@nlp_router.post("/index/answer/{project_id}")
async def answer_rag(request: Request, project_id: int, search_request: SearchRequest):

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
            TempleteParser=request.app.template_parser
        )


    answer, full_prompt, chat_history = await nlp_controller.answer_rag_question(
        project=project,
        query=search_request.text,
        limit=search_request.limit,
    )

    if not answer:
        return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={
                    "signal": ResponseEnums.ResponseSignal.RAG_ANSWER_ERROR.value
                }
        )
    
    return JSONResponse(
        content={
            "signal": ResponseEnums.ResponseSignal.RAG_ANSWER_SUCCESS.value,
            "answer": answer,
            "full_prompt": full_prompt,
            "chat_history": chat_history
        }
    )

