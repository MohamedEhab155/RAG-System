from Stores.LLM.LLmsInterface import LLmsInterface 
import cohere

import logging
from ..LLMSEnums import CoHereEnums,DocumentTypeEnum
class CoHereProvider(LLmsInterface): 

    def __init__(self, api_key: str,
                       default_input_max_characters: int=1000,
                       default_generation_max_output_tokens: int=1000,
                       default_generation_temperature: float=0.1):
        
        self.api_key = api_key

        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature

        self.generation_model_id = None

        self.embedding_model_id = None
        self.embedding_size = None
        self.enums = CoHereEnums

        self.client=cohere.Client(
            api_key=self.api_key 
        )

        self.logger=logging.getLogger(__name__)
    
 
    def set_generation_model(self, model_id: str):
        self.generation_model_id=model_id


    def set_embedding_model(self, model_id: str, embedding_size: int=None):
        self.embedding_model_id=model_id 
        self.embedding_size=embedding_size

    def process_text(self, text):
        if isinstance(text, list):
            text = "\n".join(
                item["data"]["text"] for item in text if "data" in item
            )

        return text[:self.default_input_max_characters].strip()


    def generate_text(self, prompt: str, system_message: str = None, max_output_tokens: int = None,
                  temperature: float = None, documents: list = None):
        """
        Generate text using Cohere's Chat API with RAG capabilities for SDK version 5.20.0.
        
        Args:
            prompt: The user's query or prompt
            system_message: Optional system message to guide the model
            max_output_tokens: Maximum number of tokens to generate
            temperature: Temperature parameter for generation
            documents: List of documents for RAG
            
        Returns:
            Generated text response or None if an error occurs
        """
        if not self.client:
            self.logger.error("CoHere client was not set")
            return None

        if not self.generation_model_id:
            self.logger.error("Generation model for CoHere was not set")
            return None
        
        max_output_tokens = max_output_tokens if max_output_tokens else self.default_generation_max_output_tokens
        temperature = temperature if temperature else self.default_generation_temperature

        try:
            message = f"System: {system_message}\n\nUser: {prompt}"
            # Make the API call with proper parameters for version 5.20.0
            response = self.client.chat(
                model=self.generation_model_id,
                message=message,  # Note: In 5.20.0, it's 'message' not 'messages'
                temperature=temperature,
                max_tokens=max_output_tokens,
                documents=documents
            )
            
            # Extract the response text
            if response and hasattr(response, 'text'):
                return response.text
            else:
                self.logger.error("Invalid response format from Cohere API")
                return None
                
        except Exception as e:
            self.logger.error(f"Error while generating text with CoHere: {str(e)}")
            return None


  
    def embed_text(self, text: str, document_type: str = None):
        if not self.client : 
            self.logger.error("Cohere client was not set")
            return None 
            self.logger.error("Embedding model for Cohere was not set")
            return None
        
        model=self.embedding_model_id 

        input_type=CoHereEnums.DOCUMENT.value 
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type=CoHereEnums.QUERY.value

        res = self.client.embed(
        texts=[self.process_text(text)],
        model=model,
        input_type=input_type,
        embedding_types=["float"],
    )
        if not res or not res.embeddings or not res.embeddings.float :
            self.logger.error("Error while embedding text with Cohere")
            return None
        return res.embeddings.float[0]


    def construct_prompt(self, prompt: str, role: str):
        return { 

            "role":role,
            "content": self.process_text(prompt)
        }
    