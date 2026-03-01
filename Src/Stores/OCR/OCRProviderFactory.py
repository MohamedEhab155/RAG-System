from  .OCREnums import OCRTypes
from .Providers.GemenaiProvidrs import GeminiProvider
from .Providers.MistralProviders import MistralProvider
from Helper.config import get_settings

settings = get_settings()

class OCRProviderFactory:

    @staticmethod
    def create_provider(provider_name):

        if provider_name == OCRTypes.GEMENAI:
            return GeminiProvider(api_key=settings.GEMENAI_API_KEY)

        elif provider_name == OCRTypes.MISTRAL:
            return MistralProvider(api_key=settings.MISTRAL_API_KEY)

        else:
            raise ValueError(f"Unsupported OCR provider: {provider_name}")