import uuid
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Optional
from pathlib import Path

from config import settings
from models import GenerationJob, JobStatus, database

class GenerationService:
    def __init__(self):
        self.outputs_path = Path(settings.OUTPUTS_PATH)
        self.outputs_path.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        (self.outputs_path / "images").mkdir(exist_ok=True)
        (self.outputs_path / "videos").mkdir(exist_ok=True)
        (self.outputs_path / "thumbnails").mkdir(exist_ok=True)
    
    async def generate_image(self, request) -> GenerationJob:
        """Generate an image using ComfyUI"""
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Create generation job record
        job_data = {
            "id": job_id,
            "avatar_token": request.avatar_token,
            "job_type": "image",
            "status": JobStatus.PENDING,
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "steps": request.steps,
            "cfg_scale": request.cfg_scale,
            "width": request.width,
            "height": request.height,
            "seed": request.seed,
            "nsfw": request.nsfw,
            "started_at": datetime.utcnow()
        }
        
        # Insert into database
        query = """
        INSERT INTO generation_jobs 
        (id, avatar_token, job_type, status, prompt, negative_prompt, steps, cfg_scale, 
         width, height, seed, nsfw, started_at)
        VALUES (:id, :avatar_token, :job_type, :status, :prompt, :negative_prompt, 
                :steps, :cfg_scale, :width, :height, :seed, :nsfw, :started_at)
        """
        await database.execute(query=query, values=job_data)
        
        # Start generation process
        asyncio.create_task(self._run_image_generation(job_id))
        
        return await self.get_job_status(job_id)
    
    async def generate_video(self, request) -> GenerationJob:
        """Generate a video using ComfyUI with AnimateDiff"""
        # Generate job ID
        job_id = str(uuid.uuid4())
        
        # Create generation job record
        job_data = {
            "id": job_id,
            "avatar_token": request.avatar_token,
            "job_type": "video",
            "status": JobStatus.PENDING,
            "prompt": request.prompt,
            "negative_prompt": request.negative_prompt,
            "steps": request.steps,
            "cfg_scale": request.cfg_scale,
            "seed": request.seed,
            "nsfw": request.nsfw,
            "frames": request.frames,
            "fps": request.fps,
            "started_at": datetime.utcnow()
        }
        
        # Insert into database
        query = """
        INSERT INTO generation_jobs 
        (id, avatar_token, job_type, status, prompt, negative_prompt, steps, cfg_scale, 
         seed, nsfw, frames, fps, started_at)
        VALUES (:id, :avatar_token, :job_type, :status, :prompt, :negative_prompt, 
                :steps, :cfg_scale, :seed, :nsfw, :frames, :fps, :started_at)
        """
        await database.execute(query=query, values=job_data)
        
        # Start generation process
        asyncio.create_task(self._run_video_generation(job_id))
        
        return await self.get_job_status(job_id)
    
    async def _run_image_generation(self, job_id: str):
        """Run image generation using ComfyUI"""
        try:
            # Update job status
            await self._update_job_status(job_id, JobStatus.RUNNING, 10)
            
            # Get job details
            job = await self.get_job_status(job_id)
            if not job:
                raise Exception("Job not found")
            
            # Create ComfyUI workflow
            workflow = await self._create_image_workflow(job)
            
            # Submit to ComfyUI
            result = await self._submit_to_comfyui(workflow)
            
            # Update progress
            await self._update_job_progress(job_id, 50)
            
            # Wait for completion and get result
            output_path = await self._wait_for_comfyui_completion(
                result["prompt_id"], job_id, "image"
            )
            
            # Update job with output
            await self._complete_job(job_id, output_path)
            
        except Exception as e:
            print(f"Image generation failed for job {job_id}: {e}")
            await self._update_job_status(job_id, JobStatus.FAILED, 0, str(e))
    
    async def _run_video_generation(self, job_id: str):
        """Run video generation using ComfyUI with AnimateDiff"""
        try:
            # Update job status
            await self._update_job_status(job_id, JobStatus.RUNNING, 10)
            
            # Get job details
            job = await self.get_job_status(job_id)
            if not job:
                raise Exception("Job not found")
            
            # Create ComfyUI workflow for video
            workflow = await self._create_video_workflow(job)
            
            # Submit to ComfyUI
            result = await self._submit_to_comfyui(workflow)
            
            # Update progress
            await self._update_job_progress(job_id, 30)
            
            # Wait for completion and get result
            output_path = await self._wait_for_comfyui_completion(
                result["prompt_id"], job_id, "video"
            )
            
            # Update job with output
            await self._complete_job(job_id, output_path)
            
        except Exception as e:
            print(f"Video generation failed for job {job_id}: {e}")
            await self._update_job_status(job_id, JobStatus.FAILED, 0, str(e))
    
    async def _create_image_workflow(self, job: GenerationJob) -> dict:
        """Create ComfyUI workflow for image generation"""
        # Get avatar LoRA path
        avatar_dir = Path(settings.AVATARS_PATH) / job.avatar_token
        lora_path = avatar_dir / "model" / "lora_weights.safetensors"
        
        # Base model to use
        base_model = settings.NSFW_MODEL if job.nsfw else settings.BASE_MODEL
        
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": base_model,
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                    "lora_name": str(lora_path),
                    "strength_model": 1.0,
                    "strength_clip": 1.0,
                    "model": ["1", 0],
                    "clip": ["1", 1]
                },
                "class_type": "LoraLoader"
            },
            "3": {
                "inputs": {
                    "text": job.prompt,
                    "clip": ["2", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "4": {
                "inputs": {
                    "text": job.negative_prompt or "",
                    "clip": ["2", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "5": {
                "inputs": {
                    "seed": job.seed or -1,
                    "steps": job.steps,
                    "cfg": job.cfg_scale,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["2", 0],
                    "positive": ["3", 0],
                    "negative": ["4", 0],
                    "latent_image": ["6", 0]
                },
                "class_type": "KSampler"
            },
            "6": {
                "inputs": {
                    "width": job.width,
                    "height": job.height,
                    "batch_size": 1
                },
                "class_type": "EmptyLatentImage"
            },
            "7": {
                "inputs": {
                    "samples": ["5", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode"
            },
            "8": {
                "inputs": {
                    "filename_prefix": f"avatar_{job.avatar_token}_{job.id}",
                    "images": ["7", 0]
                },
                "class_type": "SaveImage"
            }
        }
        
        return workflow
    
    async def _create_video_workflow(self, job: GenerationJob) -> dict:
        """Create ComfyUI workflow for video generation with AnimateDiff"""
        # Get avatar LoRA path
        avatar_dir = Path(settings.AVATARS_PATH) / job.avatar_token
        lora_path = avatar_dir / "model" / "lora_weights.safetensors"
        
        # Base model to use
        base_model = settings.NSFW_MODEL if job.nsfw else settings.BASE_MODEL
        
        workflow = {
            "1": {
                "inputs": {
                    "ckpt_name": base_model,
                },
                "class_type": "CheckpointLoaderSimple"
            },
            "2": {
                "inputs": {
                    "lora_name": str(lora_path),
                    "strength_model": 1.0,
                    "strength_clip": 1.0,
                    "model": ["1", 0],
                    "clip": ["1", 1]
                },
                "class_type": "LoraLoader"
            },
            "3": {
                "inputs": {
                    "model_name": "mm_sd_v15_v2.ckpt",  # AnimateDiff model
                    "model": ["2", 0]
                },
                "class_type": "ADE_AnimateDiffLoaderWithContext"
            },
            "4": {
                "inputs": {
                    "text": job.prompt,
                    "clip": ["2", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "5": {
                "inputs": {
                    "text": job.negative_prompt or "",
                    "clip": ["2", 1]
                },
                "class_type": "CLIPTextEncode"
            },
            "6": {
                "inputs": {
                    "seed": job.seed or -1,
                    "steps": job.steps,
                    "cfg": job.cfg_scale,
                    "sampler_name": "euler",
                    "scheduler": "normal",
                    "denoise": 1.0,
                    "model": ["3", 0],
                    "positive": ["4", 0],
                    "negative": ["5", 0],
                    "latent_image": ["7", 0]
                },
                "class_type": "KSampler"
            },
            "7": {
                "inputs": {
                    "width": 512,
                    "height": 512,
                    "length": job.frames,
                    "batch_size": 1
                },
                "class_type": "ADE_EmptyLatentImageLarge"
            },
            "8": {
                "inputs": {
                    "samples": ["6", 0],
                    "vae": ["1", 2]
                },
                "class_type": "VAEDecode"
            },
            "9": {
                "inputs": {
                    "filename_prefix": f"avatar_{job.avatar_token}_{job.id}",
                    "fps": job.fps,
                    "images": ["8", 0]
                },
                "class_type": "VHS_VideoCombine"
            }
        }
        
        return workflow
    
    async def _submit_to_comfyui(self, workflow: dict) -> dict:
        """Submit workflow to ComfyUI API"""
        async with aiohttp.ClientSession() as session:
            url = f"{settings.COMFYUI_API_URL}/prompt"
            payload = {"prompt": workflow}
            
            async with session.post(url, json=payload) as response:
                if response.status != 200:
                    raise Exception(f"ComfyUI API error: {response.status}")
                
                return await response.json()
    
    async def _wait_for_comfyui_completion(self, prompt_id: str, job_id: str, job_type: str) -> str:
        """Wait for ComfyUI to complete and return output path"""
        max_wait_time = 600  # 10 minutes max
        check_interval = 5
        elapsed_time = 0
        
        async with aiohttp.ClientSession() as session:
            while elapsed_time < max_wait_time:
                # Check job status
                url = f"{settings.COMFYUI_API_URL}/history/{prompt_id}"
                async with session.get(url) as response:
                    if response.status == 200:
                        history = await response.json()
                        
                        if prompt_id in history:
                            job_history = history[prompt_id]
                            
                            if job_history.get("status", {}).get("completed", False):
                                # Job completed, get output
                                outputs = job_history.get("outputs", {})
                                
                                # Find the output file
                                for node_id, output in outputs.items():
                                    if job_type == "image" and "images" in output:
                                        image_info = output["images"][0]
                                        return await self._download_comfyui_output(
                                            image_info, job_id, job_type
                                        )
                                    elif job_type == "video" and "gifs" in output:
                                        video_info = output["gifs"][0]
                                        return await self._download_comfyui_output(
                                            video_info, job_id, job_type
                                        )
                
                # Update progress
                progress = min(90, 50 + (elapsed_time / max_wait_time) * 40)
                await self._update_job_progress(job_id, progress)
                
                await asyncio.sleep(check_interval)
                elapsed_time += check_interval
        
        raise Exception("ComfyUI job timed out")
    
    async def _download_comfyui_output(self, file_info: dict, job_id: str, job_type: str) -> str:
        """Download output file from ComfyUI"""
        filename = file_info["filename"]
        subfolder = file_info.get("subfolder", "")
        file_type = file_info.get("type", "output")
        
        # Download URL
        url = f"{settings.COMFYUI_API_URL}/view"
        params = {
            "filename": filename,
            "type": file_type
        }
        if subfolder:
            params["subfolder"] = subfolder
        
        # Determine output path
        if job_type == "image":
            output_dir = self.outputs_path / "images"
            file_ext = ".png"
        else:
            output_dir = self.outputs_path / "videos"
            file_ext = ".gif"
        
        output_path = output_dir / f"{job_id}{file_ext}"
        
        # Download file
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    with open(output_path, "wb") as f:
                        async for chunk in response.content.iter_chunked(8192):
                            f.write(chunk)
                else:
                    raise Exception(f"Failed to download output: {response.status}")
        
        return str(output_path)
    
    async def _update_job_status(self, job_id: str, status: JobStatus, progress: float, error: str = None):
        """Update generation job status"""
        update_data = {
            "job_id": job_id,
            "status": status,
            "progress": progress
        }
        
        query = "UPDATE generation_jobs SET status = :status, progress = :progress"
        values = {"job_id": job_id, "status": status, "progress": progress}
        
        if status == JobStatus.COMPLETED:
            query += ", completed_at = :completed_at"
            values["completed_at"] = datetime.utcnow()
        elif status == JobStatus.FAILED and error:
            query += ", error = :error"
            values["error"] = error
        
        query += " WHERE id = :job_id"
        
        await database.execute(query=query, values=values)
    
    async def _update_job_progress(self, job_id: str, progress: float):
        """Update job progress"""
        query = "UPDATE generation_jobs SET progress = :progress WHERE id = :job_id"
        await database.execute(query=query, values={"job_id": job_id, "progress": progress})
    
    async def _complete_job(self, job_id: str, output_path: str):
        """Complete generation job with output"""
        # Generate public URL for output
        output_url = f"/static/outputs/{Path(output_path).name}"
        
        query = """
        UPDATE generation_jobs 
        SET status = :status, progress = 100, output_path = :output_path, 
            output_url = :output_url, completed_at = :completed_at
        WHERE id = :job_id
        """
        
        await database.execute(query=query, values={
            "job_id": job_id,
            "status": JobStatus.COMPLETED,
            "output_path": output_path,
            "output_url": output_url,
            "completed_at": datetime.utcnow()
        })
    
    async def get_job_status(self, job_id: str) -> Optional[GenerationJob]:
        """Get generation job status"""
        query = "SELECT * FROM generation_jobs WHERE id = :job_id"
        result = await database.fetch_one(query=query, values={"job_id": job_id})
        
        if result:
            return GenerationJob(**dict(result))
        return None