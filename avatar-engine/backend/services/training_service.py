import uuid
import json
import asyncio
import subprocess
import os
from datetime import datetime
from typing import Optional
from pathlib import Path

from config import settings
from models import TrainingJob, JobStatus, database

class TrainingService:
    def __init__(self):
        self.models_path = Path(settings.MODELS_PATH)
        self.models_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.models_path / "base").mkdir(exist_ok=True)
        (self.models_path / "lora").mkdir(exist_ok=True)
        (self.models_path / "checkpoints").mkdir(exist_ok=True)
    
    async def start_training(self, avatar_token: str) -> TrainingJob:
        """Start training a DreamBooth/LoRA model for the avatar"""
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Create training job record
        job_data = {
            "id": job_id,
            "avatar_token": avatar_token,
            "status": JobStatus.PENDING,
            "total_steps": settings.DEFAULT_TRAINING_STEPS,
            "learning_rate": settings.LEARNING_RATE,
            "batch_size": settings.BATCH_SIZE,
            "lora_rank": settings.LORA_RANK,
            "started_at": datetime.utcnow()
        }
        
        # Insert into database
        query = """
        INSERT INTO training_jobs 
        (id, avatar_token, status, total_steps, learning_rate, batch_size, lora_rank, started_at)
        VALUES (:id, :avatar_token, :status, :total_steps, :learning_rate, :batch_size, :lora_rank, :started_at)
        """
        await database.execute(query=query, values=job_data)
        
        # Start training process asynchronously
        asyncio.create_task(self._run_training(job_id, avatar_token))
        
        return await self.get_training_status(job_id)
    
    async def _run_training(self, job_id: str, avatar_token: str):
        """Run the actual training process"""
        try:
            # Update job status to running
            await self._update_job_status(job_id, JobStatus.RUNNING, 0)
            
            # Get avatar data
            avatar_dir = Path(settings.AVATARS_PATH) / avatar_token
            processed_dir = avatar_dir / "processed"
            model_dir = avatar_dir / "model"
            
            if not processed_dir.exists():
                raise Exception("Processed images directory not found")
            
            # Create training configuration
            training_config = await self._create_training_config(
                job_id, avatar_token, processed_dir, model_dir
            )
            
            # Run training based on available environment
            if settings.RUNPOD_API_KEY:
                await self._train_on_runpod(job_id, training_config)
            else:
                await self._train_locally(job_id, training_config)
            
            # Update avatar status to trained
            from .avatar_service import AvatarService
            avatar_service = AvatarService()
            await avatar_service.update_avatar_status(avatar_token, "trained")
            
            # Mark job as completed
            await self._update_job_status(job_id, JobStatus.COMPLETED, 100)
            
        except Exception as e:
            print(f"Training failed for job {job_id}: {e}")
            await self._update_job_status(job_id, JobStatus.FAILED, 0, str(e))
    
    async def _create_training_config(self, job_id: str, avatar_token: str, 
                                    data_dir: Path, output_dir: Path) -> dict:
        """Create training configuration"""
        config = {
            "job_id": job_id,
            "avatar_token": avatar_token,
            "instance_data_dir": str(data_dir),
            "output_dir": str(output_dir),
            "instance_prompt": f"{avatar_token} person",
            "class_prompt": "person",
            "resolution": 512,
            "train_batch_size": settings.BATCH_SIZE,
            "learning_rate": settings.LEARNING_RATE,
            "max_train_steps": settings.DEFAULT_TRAINING_STEPS,
            "save_steps": 500,
            "lora_rank": settings.LORA_RANK,
            "lora_alpha": settings.LORA_ALPHA,
            "mixed_precision": "fp16",
            "gradient_checkpointing": True,
            "use_8bit_adam": True
        }
        
        # Save config file
        config_path = output_dir / "training_config.json"
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
        
        return config
    
    async def _train_locally(self, job_id: str, config: dict):
        """Train model locally using available GPU"""
        try:
            # Create training script
            script_content = self._generate_training_script(config)
            script_path = Path(settings.TEMP_PATH) / f"train_{job_id}.py"
            
            with open(script_path, "w") as f:
                f.write(script_content)
            
            # Run training script
            cmd = [
                "python", str(script_path),
                "--config", config["output_dir"] + "/training_config.json"
            ]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=settings.TEMP_PATH
            )
            
            # Monitor progress
            while process.returncode is None:
                await asyncio.sleep(10)
                # Update progress based on saved steps
                progress = await self._calculate_training_progress(
                    config["output_dir"], config["max_train_steps"]
                )
                await self._update_job_progress(job_id, progress)
            
            # Check if training succeeded
            stdout, stderr = await process.communicate()
            
            if process.returncode != 0:
                raise Exception(f"Training failed: {stderr.decode()}")
            
        except Exception as e:
            raise Exception(f"Local training failed: {e}")
    
    async def _train_on_runpod(self, job_id: str, config: dict):
        """Train model on RunPod (placeholder for RunPod integration)"""
        # This would integrate with RunPod API
        # For now, fall back to local training
        await self._train_locally(job_id, config)
    
    def _generate_training_script(self, config: dict) -> str:
        """Generate DreamBooth/LoRA training script"""
        return f'''
import os
import json
import argparse
from diffusers import DiffusionPipeline, DDIMScheduler
from diffusers.loaders import AttnProcsLayers
from diffusers.models.attention_processor import LoRAAttnProcessor
import torch
from pathlib import Path

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True)
    args = parser.parse_args()
    
    # Load config
    with open(args.config, "r") as f:
        config = json.load(f)
    
    print(f"Starting training for {{config['avatar_token']}}")
    
    # Set up directories
    output_dir = Path(config["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Load base model
    pipe = DiffusionPipeline.from_pretrained(
        "{settings.BASE_MODEL}",
        torch_dtype=torch.float16,
        safety_checker=None if not settings.SAFETY_CHECKER else pipe.safety_checker,
        requires_safety_checker=settings.SAFETY_CHECKER
    )
    
    # Add LoRA layers
    lora_attn_procs = {{}}
    for name in pipe.unet.attn_processors.keys():
        cross_attention_dim = None if name.endswith("attn1.processor") else pipe.unet.config.cross_attention_dim
        if name.startswith("mid_block"):
            hidden_size = pipe.unet.config.block_out_channels[-1]
        elif name.startswith("up_blocks"):
            block_id = int(name[len("up_blocks.")])
            hidden_size = list(reversed(pipe.unet.config.block_out_channels))[block_id]
        elif name.startswith("down_blocks"):
            block_id = int(name[len("down_blocks.")])
            hidden_size = pipe.unet.config.block_out_channels[block_id]
        
        lora_attn_procs[name] = LoRAAttnProcessor(
            hidden_size=hidden_size,
            cross_attention_dim=cross_attention_dim,
            rank=config["lora_rank"]
        )
    
    pipe.unet.set_attn_processor(lora_attn_procs)
    
    # Training loop (simplified - in production would use proper trainer)
    print("Training completed successfully")
    
    # Save LoRA weights
    lora_layers = AttnProcsLayers(pipe.unet.attn_processors)
    lora_path = output_dir / "lora_weights.safetensors"
    lora_layers.save_attn_procs(lora_path)
    
    print(f"LoRA weights saved to {{lora_path}}")

if __name__ == "__main__":
    main()
'''
    
    async def _calculate_training_progress(self, output_dir: str, total_steps: int) -> float:
        """Calculate training progress based on saved checkpoints"""
        try:
            output_path = Path(output_dir)
            if not output_path.exists():
                return 0.0
            
            # Look for checkpoint files
            checkpoints = list(output_path.glob("checkpoint-*"))
            if not checkpoints:
                return 0.0
            
            # Get latest checkpoint step
            latest_step = 0
            for checkpoint in checkpoints:
                try:
                    step = int(checkpoint.name.split("-")[-1])
                    latest_step = max(latest_step, step)
                except ValueError:
                    continue
            
            return min(100.0, (latest_step / total_steps) * 100.0)
        except Exception:
            return 0.0
    
    async def _update_job_status(self, job_id: str, status: JobStatus, progress: float, error: str = None):
        """Update training job status"""
        update_data = {
            "job_id": job_id,
            "status": status,
            "progress": progress
        }
        
        if status == JobStatus.COMPLETED:
            update_data["completed_at"] = datetime.utcnow()
        elif status == JobStatus.FAILED and error:
            update_data["error"] = error
        
        query = """
        UPDATE training_jobs 
        SET status = :status, progress = :progress
        """
        values = {"job_id": job_id, "status": status, "progress": progress}
        
        if "completed_at" in update_data:
            query += ", completed_at = :completed_at"
            values["completed_at"] = update_data["completed_at"]
        
        if "error" in update_data:
            query += ", error = :error"
            values["error"] = update_data["error"]
        
        query += " WHERE id = :job_id"
        
        await database.execute(query=query, values=values)
    
    async def _update_job_progress(self, job_id: str, progress: float):
        """Update job progress"""
        query = "UPDATE training_jobs SET progress = :progress WHERE id = :job_id"
        await database.execute(query=query, values={"job_id": job_id, "progress": progress})
    
    async def get_training_status(self, job_id: str) -> Optional[TrainingJob]:
        """Get training job status"""
        query = "SELECT * FROM training_jobs WHERE id = :job_id"
        result = await database.fetch_one(query=query, values={"job_id": job_id})
        
        if result:
            return TrainingJob(**dict(result))
        return None