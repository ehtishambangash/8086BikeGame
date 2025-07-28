import asyncio
import aiohttp
import subprocess
import os
import time
from pathlib import Path
from typing import Optional

from config import settings

class ComfyUIService:
    def __init__(self):
        self.comfyui_path = Path(settings.COMFYUI_PATH)
        self.api_url = settings.COMFYUI_API_URL
        self.process = None
        
    async def initialize(self):
        """Initialize ComfyUI service"""
        if settings.COMFYUI_AUTO_START:
            await self.start()
    
    async def start(self):
        """Start ComfyUI server"""
        try:
            if not self.comfyui_path.exists():
                print(f"ComfyUI not found at {self.comfyui_path}")
                return False
            
            # Check if already running
            if await self._is_running():
                print("ComfyUI is already running")
                return True
            
            # Start ComfyUI process
            cmd = [
                "python", "main.py",
                "--listen", "0.0.0.0",
                "--port", "8188",
                "--dont-print-server"
            ]
            
            self.process = subprocess.Popen(
                cmd,
                cwd=str(self.comfyui_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=os.environ.copy()
            )
            
            # Wait for startup
            max_wait = 60  # 60 seconds
            start_time = time.time()
            
            while time.time() - start_time < max_wait:
                if await self._is_running():
                    print("ComfyUI started successfully")
                    return True
                await asyncio.sleep(2)
            
            print("ComfyUI failed to start within timeout")
            return False
            
        except Exception as e:
            print(f"Error starting ComfyUI: {e}")
            return False
    
    async def stop(self):
        """Stop ComfyUI server"""
        if self.process:
            self.process.terminate()
            self.process.wait()
            self.process = None
    
    async def restart(self):
        """Restart ComfyUI server"""
        await self.stop()
        await asyncio.sleep(2)
        return await self.start()
    
    async def _is_running(self) -> bool:
        """Check if ComfyUI is running"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/system_stats", timeout=5) as response:
                    return response.status == 200
        except Exception:
            return False
    
    async def get_status(self) -> dict:
        """Get ComfyUI status"""
        try:
            if await self._is_running():
                async with aiohttp.ClientSession() as session:
                    # Get system stats
                    async with session.get(f"{self.api_url}/system_stats") as response:
                        if response.status == 200:
                            stats = await response.json()
                            return {
                                "status": "running",
                                "system_stats": stats
                            }
            
            return {"status": "stopped"}
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def get_models(self) -> dict:
        """Get available models"""
        try:
            if not await self._is_running():
                return {"error": "ComfyUI not running"}
            
            async with aiohttp.ClientSession() as session:
                # Get checkpoints
                async with session.get(f"{self.api_url}/object_info/CheckpointLoaderSimple") as response:
                    if response.status == 200:
                        info = await response.json()
                        checkpoints = info.get("CheckpointLoaderSimple", {}).get("input", {}).get("required", {}).get("ckpt_name", [])
                        
                        return {
                            "checkpoints": checkpoints[0] if checkpoints else [],
                            "status": "success"
                        }
            
            return {"error": "Failed to get models"}
        except Exception as e:
            return {"error": str(e)}
    
    async def queue_prompt(self, workflow: dict) -> dict:
        """Queue a prompt for generation"""
        try:
            if not await self._is_running():
                raise Exception("ComfyUI not running")
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.api_url}/prompt", 
                    json={"prompt": workflow}
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        raise Exception(f"API error: {response.status}")
        except Exception as e:
            raise Exception(f"Failed to queue prompt: {e}")
    
    async def get_queue(self) -> dict:
        """Get current queue status"""
        try:
            if not await self._is_running():
                return {"error": "ComfyUI not running"}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.api_url}/queue") as response:
                    if response.status == 200:
                        return await response.json()
            
            return {"error": "Failed to get queue"}
        except Exception as e:
            return {"error": str(e)}
    
    async def get_history(self, prompt_id: Optional[str] = None) -> dict:
        """Get generation history"""
        try:
            if not await self._is_running():
                return {"error": "ComfyUI not running"}
            
            url = f"{self.api_url}/history"
            if prompt_id:
                url += f"/{prompt_id}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        return await response.json()
            
            return {"error": "Failed to get history"}
        except Exception as e:
            return {"error": str(e)}
    
    async def cancel_all(self) -> dict:
        """Cancel all queued prompts"""
        try:
            if not await self._is_running():
                return {"error": "ComfyUI not running"}
            
            async with aiohttp.ClientSession() as session:
                async with session.post(f"{self.api_url}/queue", json={"clear": True}) as response:
                    if response.status == 200:
                        return {"success": True}
            
            return {"error": "Failed to cancel queue"}
        except Exception as e:
            return {"error": str(e)}