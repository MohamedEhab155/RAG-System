from Helper.config import Settings,get_settings 
import os 

class BaseContoroller: 
    def __init__(self):
        self.app_settings=get_settings()

        self.base_dir= os.path.dirname(os.path.dirname(__file__))
        self.file_dirs=os.path.join (self.base_dir,'assets/Files')