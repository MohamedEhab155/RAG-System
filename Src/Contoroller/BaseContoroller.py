from Helper.config import Settings,get_settings 
import os 
import random
import string
class BaseContoroller: 
    def __init__(self):
        self.app_settings=get_settings()

        self.base_dir= os.path.dirname(os.path.dirname(__file__))
        self.file_dirs=os.path.join (self.base_dir,'assets/Files')

    def generate_random_string(self, length: int=12):
             return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))