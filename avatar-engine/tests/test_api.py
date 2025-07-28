import pytest
import asyncio
from fastapi.testclient import TestClient
import sys
import os

# Add the backend directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

from backend.main import app
from backend.config import settings

client = TestClient(app)

def test_health_check():
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_root_endpoint():
    """Test the root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Avatar Engine" in response.json()["message"]

def test_avatars_list_empty():
    """Test listing avatars when none exist"""
    response = client.get("/api/avatars")
    assert response.status_code == 200
    assert "avatars" in response.json()

def test_comfyui_status():
    """Test ComfyUI status endpoint"""
    response = client.get("/api/comfyui/status")
    assert response.status_code == 200
    assert "comfyui_status" in response.json()

def test_stats_endpoint():
    """Test statistics endpoint"""
    response = client.get("/api/stats")
    assert response.status_code == 200
    
@pytest.mark.asyncio
async def test_avatar_creation_validation():
    """Test avatar creation with invalid data"""
    # Test with no images
    response = client.post("/api/avatars/create", data={"name": "Test"})
    assert response.status_code == 422  # Validation error

def test_generate_image_without_avatar():
    """Test image generation without avatar token"""
    response = client.post("/api/generate/image", json={
        "avatar_token": "nonexistent",
        "prompt": "test prompt"
    })
    assert response.status_code == 404  # Avatar not found

if __name__ == "__main__":
    pytest.main([__file__])