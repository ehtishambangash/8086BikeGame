from pydantic_settings import BaseSettings
from pathlib import Path
import os

class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    
    # Storage Paths
    STORAGE_PATH: str = "./storage"
    MODELS_PATH: str = "./storage/models"
    AVATARS_PATH: str = "./storage/avatars"
    OUTPUTS_PATH: str = "./storage/outputs"
    TEMP_PATH: str = "./storage/temp"
    
    # Training Configuration
    RUNPOD_API_KEY: str = ""
    DEFAULT_TRAINING_STEPS: int = 1000
    BATCH_SIZE: int = 1
    LEARNING_RATE: float = 1e-4
    
    # ComfyUI Configuration
    COMFYUI_PATH: str = "./models/ComfyUI"
    COMFYUI_API_URL: str = "http://localhost:8188"
    COMFYUI_AUTO_START: bool = True
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./avatar_engine.db"
    
    # Redis Configuration (for background jobs)
    REDIS_URL: str = "redis://localhost:6379"
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"
    
    # NSFW Settings
    ENABLE_NSFW: bool = True
    CONTENT_FILTERING: bool = False
    SAFETY_CHECKER: bool = False
    
    # Model Configuration
    BASE_MODEL: str = "runwayml/stable-diffusion-v1-5"
    NSFW_MODEL: str = "ChilloutMix"  # Alternative NSFW-friendly model
    LORA_RANK: int = 64
    LORA_ALPHA: int = 64
    
    # Generation Settings
    DEFAULT_STEPS: int = 20
    DEFAULT_CFG_SCALE: float = 7.0
    DEFAULT_WIDTH: int = 512
    DEFAULT_HEIGHT: int = 512
    MAX_BATCH_SIZE: int = 4
    
    # Video Settings
    DEFAULT_FRAMES: int = 16
    DEFAULT_FPS: int = 8
    MAX_FRAMES: int = 64
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # File Upload Settings
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_IMAGE_TYPES: list = ["image/jpeg", "image/png", "image/webp"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Ensure absolute paths
        base_dir = Path(__file__).parent.parent.parent
        
        if not os.path.isabs(self.STORAGE_PATH):
            self.STORAGE_PATH = str(base_dir / self.STORAGE_PATH)
        if not os.path.isabs(self.MODELS_PATH):
            self.MODELS_PATH = str(base_dir / self.MODELS_PATH)
        if not os.path.isabs(self.AVATARS_PATH):
            self.AVATARS_PATH = str(base_dir / self.AVATARS_PATH)
        if not os.path.isabs(self.OUTPUTS_PATH):
            self.OUTPUTS_PATH = str(base_dir / self.OUTPUTS_PATH)
        if not os.path.isabs(self.TEMP_PATH):
            self.TEMP_PATH = str(base_dir / self.TEMP_PATH)
        if not os.path.isabs(self.COMFYUI_PATH):
            self.COMFYUI_PATH = str(base_dir / self.COMFYUI_PATH)

# Global settings instance
settings = Settings()