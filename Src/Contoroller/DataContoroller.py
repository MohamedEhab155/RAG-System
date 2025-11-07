from .BaseContoroller import BaseContoroller
from fastapi import UploadFile
from  Models import ResponseSignal
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




