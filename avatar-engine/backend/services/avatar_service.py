import os
import uuid
import shutil
import json
import asyncio
from typing import List, Optional
from datetime import datetime
from pathlib import Path
from PIL import Image
import cv2
import numpy as np

from config import settings
from models import Avatar, AvatarStatus, database

class AvatarService:
    def __init__(self):
        self.storage_path = Path(settings.AVATARS_PATH)
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    async def create_avatar(self, name: str, description: Optional[str], images: List) -> Avatar:
        """Create a new avatar from uploaded images"""
        # Generate unique token
        token = f"avtr_{uuid.uuid4().hex[:8]}"
        
        # Create avatar directory structure
        avatar_dir = self.storage_path / token
        images_dir = avatar_dir / "images"
        processed_dir = avatar_dir / "processed"
        model_dir = avatar_dir / "model"
        
        for dir_path in [avatar_dir, images_dir, processed_dir, model_dir]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        # Save uploaded images
        saved_images = []
        for i, image_file in enumerate(images):
            # Validate image type
            if image_file.content_type not in settings.ALLOWED_IMAGE_TYPES:
                raise ValueError(f"Invalid image type: {image_file.content_type}")
            
            # Save original image
            image_path = images_dir / f"image_{i:03d}.jpg"
            with open(image_path, "wb") as f:
                content = await image_file.read()
                f.write(content)
            
            saved_images.append(str(image_path))
        
        # Preprocess images
        processed_images = await self._preprocess_images(saved_images, processed_dir)
        
        # Create avatar record in database
        avatar_data = {
            "token": token,
            "name": name,
            "description": description,
            "status": AvatarStatus.PREPROCESSING,
            "training_images_count": len(processed_images),
            "created_at": datetime.utcnow()
        }
        
        # Insert into database
        query = """
        INSERT INTO avatars (token, name, description, status, training_images_count, created_at)
        VALUES (:token, :name, :description, :status, :training_images_count, :created_at)
        """
        await database.execute(query=query, values=avatar_data)
        
        # Save metadata
        metadata = {
            "token": token,
            "name": name,
            "description": description,
            "created_at": avatar_data["created_at"].isoformat(),
            "original_images": saved_images,
            "processed_images": processed_images,
            "status": AvatarStatus.PREPROCESSING
        }
        
        metadata_path = avatar_dir / "metadata.json"
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2, default=str)
        
        # Update status to created
        await self.update_avatar_status(token, AvatarStatus.CREATED)
        
        return await self.get_avatar(token)
    
    async def _preprocess_images(self, image_paths: List[str], output_dir: Path) -> List[str]:
        """Preprocess images for training"""
        processed_images = []
        
        for i, image_path in enumerate(image_paths):
            try:
                # Load image
                img = cv2.imread(image_path)
                if img is None:
                    continue
                
                # Resize to 512x512
                img_resized = cv2.resize(img, (512, 512), interpolation=cv2.INTER_LANCZOS4)
                
                # Optional: Face detection and alignment could be added here
                # For now, we'll just do basic preprocessing
                
                # Save processed image
                output_path = output_dir / f"processed_{i:03d}.jpg"
                cv2.imwrite(str(output_path), img_resized, [cv2.IMWRITE_JPEG_QUALITY, 95])
                processed_images.append(str(output_path))
                
            except Exception as e:
                print(f"Error processing image {image_path}: {e}")
                continue
        
        return processed_images
    
    async def get_avatar(self, token: str) -> Optional[Avatar]:
        """Get avatar by token"""
        query = "SELECT * FROM avatars WHERE token = :token"
        result = await database.fetch_one(query=query, values={"token": token})
        
        if result:
            return Avatar(**dict(result))
        return None
    
    async def update_avatar_status(self, token: str, status: AvatarStatus):
        """Update avatar status"""
        query = """
        UPDATE avatars 
        SET status = :status, updated_at = :updated_at
        WHERE token = :token
        """
        await database.execute(
            query=query, 
            values={
                "token": token, 
                "status": status, 
                "updated_at": datetime.utcnow()
            }
        )
        
        # Update metadata file
        avatar_dir = self.storage_path / token
        metadata_path = avatar_dir / "metadata.json"
        
        if metadata_path.exists():
            with open(metadata_path, "r") as f:
                metadata = json.load(f)
            
            metadata["status"] = status
            metadata["updated_at"] = datetime.utcnow().isoformat()
            
            with open(metadata_path, "w") as f:
                json.dump(metadata, f, indent=2, default=str)
    
    async def delete_avatar(self, token: str) -> bool:
        """Delete avatar and all associated data"""
        # Check if avatar exists
        avatar = await self.get_avatar(token)
        if not avatar:
            return False
        
        # Delete from database
        query = "DELETE FROM avatars WHERE token = :token"
        await database.execute(query=query, values={"token": token})
        
        # Delete files
        avatar_dir = self.storage_path / token
        if avatar_dir.exists():
            shutil.rmtree(avatar_dir)
        
        return True
    
    async def list_avatars(self) -> List[dict]:
        """List all avatars"""
        query = """
        SELECT token, name, description, status, created_at, training_images_count
        FROM avatars 
        ORDER BY created_at DESC
        """
        results = await database.fetch_all(query=query)
        
        return [dict(result) for result in results]
    
    async def get_avatar_images(self, token: str) -> List[str]:
        """Get list of avatar image paths"""
        avatar_dir = self.storage_path / token
        images_dir = avatar_dir / "images"
        
        if not images_dir.exists():
            return []
        
        return [str(path) for path in images_dir.glob("*.jpg")]
    
    async def get_statistics(self) -> dict:
        """Get system statistics"""
        # Avatar counts by status
        query = """
        SELECT status, COUNT(*) as count
        FROM avatars
        GROUP BY status
        """
        status_counts = await database.fetch_all(query=query)
        
        # Total generation jobs
        query = "SELECT COUNT(*) as count FROM generation_jobs"
        total_generations = await database.fetch_one(query=query)
        
        # Recent activity
        query = """
        SELECT COUNT(*) as count
        FROM generation_jobs
        WHERE started_at > datetime('now', '-24 hours')
        """
        recent_generations = await database.fetch_one(query=query)
        
        return {
            "avatar_counts": {row["status"]: row["count"] for row in status_counts},
            "total_generations": total_generations["count"],
            "recent_generations": recent_generations["count"],
            "storage_used": await self._calculate_storage_usage()
        }
    
    async def _calculate_storage_usage(self) -> dict:
        """Calculate storage usage"""
        def get_dir_size(path):
            total = 0
            if os.path.exists(path):
                for dirpath, dirnames, filenames in os.walk(path):
                    for filename in filenames:
                        filepath = os.path.join(dirpath, filename)
                        total += os.path.getsize(filepath)
            return total
        
        return {
            "avatars_mb": get_dir_size(settings.AVATARS_PATH) / (1024 * 1024),
            "models_mb": get_dir_size(settings.MODELS_PATH) / (1024 * 1024),
            "outputs_mb": get_dir_size(settings.OUTPUTS_PATH) / (1024 * 1024)
        }