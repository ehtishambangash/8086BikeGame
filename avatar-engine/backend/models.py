import databases
import sqlalchemy
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from config import settings

# Database setup
database = databases.Database(settings.DATABASE_URL)
metadata = sqlalchemy.MetaData()
Base = declarative_base()

class AvatarStatus(str, enum.Enum):
    CREATED = "created"
    PREPROCESSING = "preprocessing"
    TRAINING = "training"
    TRAINED = "trained"
    FAILED = "failed"

class JobStatus(str, enum.Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"

class Avatar(Base):
    __tablename__ = "avatars"
    
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default=AvatarStatus.CREATED)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Model paths
    model_path = Column(String, nullable=True)
    config_path = Column(String, nullable=True)
    
    # Training metadata
    training_steps = Column(Integer, default=1000)
    training_images_count = Column(Integer, default=0)
    
    # Relationships
    training_jobs = relationship("TrainingJob", back_populates="avatar")
    generation_jobs = relationship("GenerationJob", back_populates="avatar")

class TrainingJob(Base):
    __tablename__ = "training_jobs"
    
    id = Column(String, primary_key=True, index=True)
    avatar_token = Column(String, ForeignKey("avatars.token"), nullable=False)
    status = Column(String, default=JobStatus.PENDING)
    progress = Column(Float, default=0.0)
    current_step = Column(Integer, default=0)
    total_steps = Column(Integer, default=1000)
    
    # Job metadata
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    
    # Training configuration
    learning_rate = Column(Float, default=1e-4)
    batch_size = Column(Integer, default=1)
    lora_rank = Column(Integer, default=64)
    
    # RunPod/Remote execution
    runpod_job_id = Column(String, nullable=True)
    remote_endpoint = Column(String, nullable=True)
    
    # Relationships
    avatar = relationship("Avatar", back_populates="training_jobs")

class GenerationJob(Base):
    __tablename__ = "generation_jobs"
    
    id = Column(String, primary_key=True, index=True)
    avatar_token = Column(String, ForeignKey("avatars.token"), nullable=False)
    job_type = Column(String, nullable=False)  # "image" or "video"
    status = Column(String, default=JobStatus.PENDING)
    progress = Column(Float, default=0.0)
    
    # Generation parameters
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text, nullable=True)
    steps = Column(Integer, default=20)
    cfg_scale = Column(Float, default=7.0)
    width = Column(Integer, default=512)
    height = Column(Integer, default=512)
    seed = Column(Integer, nullable=True)
    nsfw = Column(Boolean, default=False)
    
    # Video-specific parameters
    frames = Column(Integer, nullable=True)
    fps = Column(Integer, nullable=True)
    
    # Output
    output_url = Column(String, nullable=True)
    output_path = Column(String, nullable=True)
    thumbnail_url = Column(String, nullable=True)
    
    # Job metadata
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)
    
    # ComfyUI workflow
    comfyui_workflow_id = Column(String, nullable=True)
    comfyui_node_id = Column(String, nullable=True)
    
    # Relationships
    avatar = relationship("Avatar", back_populates="generation_jobs")

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # User preferences
    nsfw_enabled = Column(Boolean, default=False)
    default_steps = Column(Integer, default=20)
    default_cfg_scale = Column(Float, default=7.0)

class ModelConfig(Base):
    __tablename__ = "model_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    type = Column(String, nullable=False)  # "base", "lora", "checkpoint"
    path = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    nsfw_compatible = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

# Create all tables
engine = sqlalchemy.create_engine(settings.DATABASE_URL, connect_args={"check_same_thread": False})
Base.metadata.create_all(bind=engine)