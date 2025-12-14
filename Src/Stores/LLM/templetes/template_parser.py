import os 
class TempleteParser :
    def __init__(self,language:str, default_language='en'):

        self.language=language
        self.default_language=default_language 

        self.current_path=os.path.dirname(os.path.abspath(__name__))

    

    def set (self,language): 
        if not language:
            language=self.default_language

        language_path = os.path.join(self.current_path,"locales",language)

        if  os.path.exists(language_path)  :
            language=self.language 
        else : 
            language=self.default_language
        
    
    def get(self,group:str,key:str,variables:dict={}):

        if not group or not key :
            return None 
        
        group_path=os.path.join(self.current_path,"localles",self.language,f"{group}.py")
        targeted_language=self.language

        if not os.path.exists(group_path):
            group_path=os.path.join(self.current_path,"localles",self.default_language,f"{group}.py")
            targeted_language=self.default_language
        
        
        module=__import__(f"Stores.LLM.templetes.locales.{targeted_language}.{group}", fromlist=[group])

        key_attribute=getattr(module,key)
        return key_attribute.substitute(variables)


        