import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Application configuration class."""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
    
    # Azure Document Intelligence Configuration
    AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT')
    AZURE_DOCUMENT_INTELLIGENCE_KEY = os.getenv('AZURE_DOCUMENT_INTELLIGENCE_KEY')
    
    # Azure Language Service Configuration
    AZURE_LANGUAGE_ENDPOINT = os.getenv('AZURE_LANGUAGE_ENDPOINT')
    AZURE_LANGUAGE_KEY = os.getenv('AZURE_LANGUAGE_KEY')
    
    # OpenAI Configuration (Optional)
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    
    # File Upload Configuration
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB max file size
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'bmp', 'gif', 'tiff'}
    
    @staticmethod
    def validate():
        """Validate required configuration values."""
        required_configs = [
            ('AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT', Config.AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT),
            ('AZURE_DOCUMENT_INTELLIGENCE_KEY', Config.AZURE_DOCUMENT_INTELLIGENCE_KEY),
            ('AZURE_LANGUAGE_ENDPOINT', Config.AZURE_LANGUAGE_ENDPOINT),
            ('AZURE_LANGUAGE_KEY', Config.AZURE_LANGUAGE_KEY),
        ]
        
        missing = [name for name, value in required_configs if not value]
        
        if missing:
            raise ValueError(
                f"Missing required configuration: {', '.join(missing)}. "
                f"Please check your .env file."
            )
