from pydantic import BaseModel ,Field
from typing import Optional
from bson import ObjectId

class ChunkData(BaseModel):

    id: Optional[ObjectId] = Field(None, alias="_id")

    chunk_text : str =Field(...,min_length=1)

    chunk_meta_data: dict
    chunk_order:int =Field(...,gt=0)
    chunk_project_id : ObjectId

    model_config = {
    "arbitrary_types_allowed": True
}
