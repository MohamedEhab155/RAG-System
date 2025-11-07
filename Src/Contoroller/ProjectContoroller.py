from .BaseContoroller import BaseContoroller
import os 
class ProjectContoroller(BaseContoroller): 
    def __init__(self):
        super().__init__() 

    
    def get_project_path(self,project_id): 
        project_dire = os.path.join(self.file_dirs , project_id)

        if not os.path.exists(project_dire):
            os.makedirs(project_dire)
        return project_dire