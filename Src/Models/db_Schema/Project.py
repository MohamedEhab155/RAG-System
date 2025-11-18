from pydantic import BaseModel ,Field
from typing import Optional

from bson import ObjectId

class Project(BaseModel): 
    id: Optional[ObjectId] = Field(None, alias="_id")

    project_id :str =Field(...,min_length=1) 

    def vailidat_project_id (cls,value):

        if  not value.isalnum:
            raise ValueError ("should be alphanumircal")
        return value


    model_config = {
     "arbitrary_types_allowed": True
}

        