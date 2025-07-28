from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import os
import uuid
import json
from datetime import datetime
import asyncio
from pathlib import Path

from config import settings
from models import database, Avatar, GenerationJob, TrainingJob
from services.avatar_service import AvatarService
from services.training_service import TrainingService
from services.generation_service import GenerationService
from services.comfyui_service import ComfyUIService

# Initialize FastAPI app
app = FastAPI(
    title="Uncensored DreamBooth Avatar Engine",
    description="A backend system for training personalized avatars and generating content via ComfyUI",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
avatar_service = AvatarService()
training_service = TrainingService()
generation_service = GenerationService()
comfyui_service = ComfyUIService()

# Mount static files
app.mount("/static", StaticFiles(directory=settings.STORAGE_PATH), name="static")

# Pydantic models
class AvatarCreateRequest(BaseModel):
    name: str
    description: Optional[str] = None
    
class ImageGenerationRequest(BaseModel):
    avatar_token: str
    prompt: str
    negative_prompt: Optional[str] = None
    steps: int = 20
    cfg_scale: float = 7.0
    width: int = 512
    height: int = 512
    seed: Optional[int] = None
    nsfw: bool = False
    
class VideoGenerationRequest(BaseModel):
    avatar_token: str
    prompt: str
    negative_prompt: Optional[str] = None
    frames: int = 16
    fps: int = 8
    steps: int = 20
    cfg_scale: float = 7.0
    seed: Optional[int] = None
    nsfw: bool = False

# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup"""
    await database.connect()
    
    # Create storage directories
    os.makedirs(settings.AVATARS_PATH, exist_ok=True)
    os.makedirs(settings.MODELS_PATH, exist_ok=True)
    os.makedirs(settings.OUTPUTS_PATH, exist_ok=True)
    os.makedirs(os.path.join(settings.STORAGE_PATH, "temp"), exist_ok=True)
    
    # Initialize ComfyUI service
    await comfyui_service.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await database.disconnect()

# Health check
@app.get("/")
async def root():
    return {"message": "Uncensored DreamBooth Avatar Engine API", "status": "running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow()}

# Avatar endpoints
@app.post("/api/avatars/create")
async def create_avatar(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    images: List[UploadFile] = File(...)
):
    """Create a new avatar from uploaded images"""
    try:
        # Validate image count
        if len(images) < 5 or len(images) > 20:
            raise HTTPException(
                status_code=400, 
                detail="Must upload between 5 and 20 images"
            )
        
        # Create avatar
        avatar = await avatar_service.create_avatar(name, description, images)
        
        # Start training job
        training_job = await training_service.start_training(avatar.token)
        
        return {
            "avatar_token": avatar.token,
            "training_job_id": training_job.id,
            "status": "training_started",
            "estimated_completion": "~90 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/avatars/{token}")
async def get_avatar(token: str):
    """Get avatar details"""
    avatar = await avatar_service.get_avatar(token)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    return {
        "token": avatar.token,
        "name": avatar.name,
        "description": avatar.description,
        "status": avatar.status,
        "created_at": avatar.created_at,
        "image_count": len(await avatar_service.get_avatar_images(token))
    }

@app.delete("/api/avatars/{token}")
async def delete_avatar(token: str):
    """Delete an avatar and all associated data"""
    success = await avatar_service.delete_avatar(token)
    if not success:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    return {"message": "Avatar deleted successfully"}

@app.get("/api/avatars")
async def list_avatars():
    """List all avatars"""
    avatars = await avatar_service.list_avatars()
    return {"avatars": avatars}

# Generation endpoints
@app.post("/api/generate/image")
async def generate_image(request: ImageGenerationRequest):
    """Generate an image using the specified avatar"""
    try:
        # Validate avatar exists and is trained
        avatar = await avatar_service.get_avatar(request.avatar_token)
        if not avatar:
            raise HTTPException(status_code=404, detail="Avatar not found")
        
        if avatar.status != "trained":
            raise HTTPException(status_code=400, detail="Avatar is not yet trained")
        
        # Start generation job
        job = await generation_service.generate_image(request)
        
        return {
            "job_id": job.id,
            "status": "generating",
            "estimated_time": "1-3 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate/video")
async def generate_video(request: VideoGenerationRequest):
    """Generate a video using the specified avatar"""
    try:
        # Validate avatar exists and is trained
        avatar = await avatar_service.get_avatar(request.avatar_token)
        if not avatar:
            raise HTTPException(status_code=404, detail="Avatar not found")
        
        if avatar.status != "trained":
            raise HTTPException(status_code=400, detail="Avatar is not yet trained")
        
        # Start generation job
        job = await generation_service.generate_video(request)
        
        return {
            "job_id": job.id,
            "status": "generating",
            "estimated_time": "5-15 minutes"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/generate/status/{job_id}")
async def get_generation_status(job_id: str):
    """Get the status of a generation job"""
    job = await generation_service.get_job_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return {
        "job_id": job.id,
        "status": job.status,
        "progress": job.progress,
        "output_url": job.output_url if job.status == "completed" else None,
        "error": job.error if job.status == "failed" else None
    }

# Training endpoints
@app.get("/api/training/status/{job_id}")
async def get_training_status(job_id: str):
    """Get the status of a training job"""
    job = await training_service.get_training_status(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Training job not found")
    
    return {
        "job_id": job.id,
        "avatar_token": job.avatar_token,
        "status": job.status,
        "progress": job.progress,
        "current_step": job.current_step,
        "total_steps": job.total_steps,
        "error": job.error if job.status == "failed" else None
    }

@app.post("/api/training/restart/{token}")
async def restart_training(token: str):
    """Restart training for an avatar"""
    avatar = await avatar_service.get_avatar(token)
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    # Start new training job
    training_job = await training_service.start_training(token)
    
    return {
        "training_job_id": training_job.id,
        "status": "training_restarted"
    }

# ComfyUI endpoints
@app.get("/api/comfyui/status")
async def get_comfyui_status():
    """Get ComfyUI service status"""
    status = await comfyui_service.get_status()
    return {"comfyui_status": status}

@app.post("/api/comfyui/restart")
async def restart_comfyui():
    """Restart ComfyUI service"""
    success = await comfyui_service.restart()
    if success:
        return {"message": "ComfyUI restarted successfully"}
    else:
        raise HTTPException(status_code=500, detail="Failed to restart ComfyUI")

# Statistics endpoints
@app.get("/api/stats")
async def get_stats():
    """Get system statistics"""
    stats = await avatar_service.get_statistics()
    return stats

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)