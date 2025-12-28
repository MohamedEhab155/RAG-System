from minirag_base import SQLAlchemyBase 
from sqlalchemy import Column , Integer,DateTime ,func
from sqlalchemy.dialects.postgresql import UUID
import uuid

class Project(SQLAlchemyBase):
    __tablename__ = "projects"

    Project_id=Column(Integer,primary_key=True,autoincrement=True)
    uuid=Column(UUID,default=uuid.uuid4,unique=True,nullable=False)

    created_at=Column(DateTime(timezone=True),server_default=func.now,nullable=False)
    updated_at=Column(DateTime(timezone=True),onupdatess=func.now,nullable=False)

