import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration"""
    
    # Student credentials
    STUDENT_SECRET = os.getenv("STUDENT_SECRET", "")
    
    # API keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
    GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")
    
    # API settings
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("PORT", "7860"))
    
    # Directories
    GENERATED_APPS_DIR = "generated_apps"
    TEMP_ATTACHMENTS_DIR = "temp_attachments"
    
    # Timeouts
    EVALUATION_TIMEOUT = 600  # 10 minutes
    RETRY_DELAYS = [1, 2, 4, 8, 16]  # exponential backoff in seconds
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        errors = []
        if not cls.STUDENT_SECRET:
            errors.append("STUDENT_SECRET not set")
        if not cls.OPENAI_API_KEY:
            errors.append("OPENAI_API_KEY not set")
        if not cls.GITHUB_TOKEN:
            errors.append("GITHUB_TOKEN not set")
        if not cls.GITHUB_USERNAME:
            errors.append("GITHUB_USERNAME not set")
        
        if errors:
            raise ValueError(f"Configuration errors: {', '.join(errors)}")


config = Config()
