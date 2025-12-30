from .BaseDataModel import BaseDataModel
from .db_Schema import Project
from sqlalchemy import select
from .Enums.DataBaseEnum import DataBaseEnum
from sqlalchemy import func
class ProjectModel(BaseDataModel): 
     def __init__(self, db_client):
        super().__init__(db_client)

        self.db_client=db_client
    
     @classmethod
     async def create_instance(cls, db_client: object):
        instance = cls(db_client)
        return instance 
 

                     
     async def  creat_project(self,project):
         
         async with self.db_client() as session:
             async with session.begin():
                session.add(project)
             session.commit()
             session.refresh(project)

     
     async def get_project_or_create_one(self, project_id: int):
          async with self.db_client() as session:
             async with session.begin():
                 quary=select(Project).where(Project.project_id==project_id)
                 result=await session.execute(quary)

                 project=result.scalar_one_or_none()

                 if project is None : 
                
                     project_rec=Project(project_id=project_id)
                     project= await self.creat_project(project=project_rec)

                 return project
        
        
     async def get_all_projects(self, page: int=1, page_size: int=10):
         
         async with self.db_client() as session:
             async with session.begin():
                 total_documents_quary=await session.execute(select(
                     
                     func.count(Project.project_id)
                 ))

                 total_documents=total_documents_quary.scalalr_one()

                 total_pages = total_documents // page_size
                 if total_documents % page_size > 0:
                    total_pages += 1

                 query = select(Project).offset((page - 1) * page_size ).limit(page_size)
                 projects = await session.execute(query).scalars().all()

                 return projects, total_pages




         

         

    
