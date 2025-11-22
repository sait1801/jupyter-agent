"""Configuration management for the application."""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""
    
    # API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    PORT = int(os.getenv("PORT", "8000"))
    HOST = os.getenv("HOST", "0.0.0.0")
    
    # CORS Configuration
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    # Jupyter Configuration
    KERNEL_TIMEOUT = 60  # seconds
    EXECUTION_TIMEOUT = 300  # seconds
    
    # AI Agent Configuration
    MAX_RETRY_ATTEMPTS = 3
    
    # Model-specific configurations
    # Reasoning models (o1-preview, o1-mini) use reasoning_effort instead of temperature
    REASONING_MODELS = ["o1-preview", "o1-mini", "o1","gpt-5","gpt-5-mini","gpt-5-nano"]
    
    # Non-reasoning models use temperature
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_REASONING_EFFORT = "medium"  # low, medium, high


config = Config()
