from .BaseContoroller import BaseContoroller
from fastapi import UploadFile
from  Models import ResponseSignal
from .ProjectContoroller import ProjectContoroller
import re
import os 
class DataContoroller (BaseContoroller): 
    def __init__(self):
        super().__init__()
        self.size_scale = 1048576 # convert MB to bytes
    


    def vaildate(self,file:UploadFile): 

        if file.content_type not in self.app_settings.FILE_ALLOWED_TYPES : 
            return False , ResponseSignal.FILE_TYPE_NOT_SUPPORTED.value
        
        if file.size  > self.size_scale : 
            return False , ResponseSignal.FILE_SIZE_EXCEEDED
        
        return True , ResponseSignal.FILE_UPLOAD_SUCCESS



    def generate_unique_filepath(self, orig_file_name: str, project_id: str):

        random_key = self.generate_random_string()
        project_path = ProjectContoroller().get_project_path(project_id=project_id)

        cleaned_file_name = self.get_clean_file_name(
            orig_file_name=orig_file_name
        )

        new_file_path = os.path.join(
            project_path,
            random_key + "_" + cleaned_file_name
        )

        while os.path.exists(new_file_path):
            random_key = self.generate_random_string()
            new_file_path = os.path.join(
                project_path,
                random_key + "_" + cleaned_file_name
            )

        return new_file_path, random_key + "_" + cleaned_file_name

    def get_clean_file_name(self, orig_file_name: str):

        # remove any special characters, except underscore and .
        cleaned_file_name = re.sub(r'[^\w.]', '', orig_file_name.strip())

        # replace spaces with underscore
        cleaned_file_name = cleaned_file_name.replace(" ", "_")

        return cleaned_file_name 
