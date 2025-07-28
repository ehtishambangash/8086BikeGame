# Uncensored DreamBooth Avatar Engine

A backend system that allows users to upload facial images to train personalized avatar models using DreamBooth and generate images/videos via ComfyUI integration.

## 🚀 Features

- **Avatar Training**: Upload 5-20 facial images to train personalized DreamBooth/LoRA models
- **Unique Tokens**: Each avatar gets a unique token (e.g., `avtr_mia`)
- **ComfyUI Integration**: Headless image and video generation pipeline
- **NSFW Support**: Optional uncensored content generation with toggle controls
- **Video Generation**: AnimateDiff/Deforum integration for video creation
- **Midjourney-style UI**: Clean, modern frontend interface
- **Privacy-First**: Local deployment, no telemetry, no prompt filtering

## 🏗️ Architecture

```
avatar-engine/
├── backend/           # FastAPI server and core logic
├── frontend/          # React/Vue.js web interface  
├── models/           # Model management and training
├── storage/          # File storage system
├── scripts/          # Utility scripts
└── tests/           # Test suite
```

## 📦 Tech Stack

- **Backend**: Python, FastAPI, PyTorch, Transformers
- **Training**: DreamBooth, LoRA, Textual Inversion
- **Generation**: ComfyUI, Stable Diffusion, AnimateDiff
- **Frontend**: React, TailwindCSS, DaisyUI
- **Jobs**: Celery + Redis for background processing
- **Storage**: Local filesystem + SQLite/PostgreSQL
- **Deployment**: Local server or RunPod/Vast.ai

## 🚦 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+ (for frontend)
- CUDA-compatible GPU (16GB+ VRAM recommended)
- Redis server

### Installation

1. **Backend Setup**:
```bash
cd backend
pip install -r requirements.txt
python main.py
```

2. **Frontend Setup**:
```bash
cd frontend
npm install
npm run dev
```

3. **ComfyUI Setup**:
```bash
cd models
git clone https://github.com/comfyanonymous/ComfyUI.git
cd ComfyUI
pip install -r requirements.txt
```

## 🔄 User Workflow

### 1. Avatar Creation
1. Upload 5-20 facial images
2. System preprocesses and assigns unique token
3. DreamBooth training starts (90 mins on 16GB GPU)
4. Avatar stored with metadata

### 2. Image Generation
1. Enter structured prompt or use form
2. Select avatar token and settings
3. Toggle NSFW if desired
4. Generate via ComfyUI pipeline

### 3. Video Generation
1. Provide prompt/storyboard
2. Select avatar and animation style
3. Generate using AnimateDiff/Deforum

## 🔧 Configuration

### Environment Variables
```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
DEBUG=true

# Storage Paths
STORAGE_PATH=./storage
MODELS_PATH=./storage/models
AVATARS_PATH=./storage/avatars

# Training Configuration
RUNPOD_API_KEY=your_key_here
DEFAULT_TRAINING_STEPS=1000
BATCH_SIZE=1

# ComfyUI Configuration
COMFYUI_PATH=./models/ComfyUI
COMFYUI_API_URL=http://localhost:8188

# Database
DATABASE_URL=sqlite:///./avatar_engine.db

# Redis (for background jobs)
REDIS_URL=redis://localhost:6379

# NSFW Settings
ENABLE_NSFW=true
CONTENT_FILTERING=false
```

## 📁 Directory Structure

```
storage/
├── avatars/           # User avatars
│   └── avtr_token/
│       ├── images/    # Original uploaded images
│       ├── processed/ # Preprocessed training data
│       ├── model/     # Trained LoRA weights
│       └── metadata.json
├── models/           # Base models and LoRA weights
│   ├── base/        # SD 1.5, SDXL checkpoints
│   ├── lora/        # User-trained LoRA files
│   └── ComfyUI/     # ComfyUI installation
└── outputs/         # Generated content
    ├── images/      # Generated images
    └── videos/      # Generated videos
```

## 🔐 Privacy & Security

- **Local Deployment**: Run entirely on your hardware
- **No Telemetry**: No data collection or external reporting
- **Uncensored**: No prompt filtering or content restrictions
- **Private**: All training and generation happens locally

## 📊 API Endpoints

### Avatar Management
- `POST /api/avatars/create` - Create new avatar
- `GET /api/avatars/{token}` - Get avatar details
- `DELETE /api/avatars/{token}` - Delete avatar

### Generation
- `POST /api/generate/image` - Generate image
- `POST /api/generate/video` - Generate video
- `GET /api/generate/status/{job_id}` - Check job status

### Training
- `POST /api/training/start` - Start avatar training
- `GET /api/training/status/{job_id}` - Check training progress

## 🧪 Development

### Running Tests
```bash
cd tests
python -m pytest
```

### Code Quality
```bash
black backend/
flake8 backend/
mypy backend/
```

## 📄 License

This project is for educational and research purposes. Please ensure compliance with local laws and platform terms of service when using AI-generated content.

## ⚠️ Disclaimer

This system supports uncensored content generation. Users are responsible for ensuring appropriate use and compliance with applicable laws and regulations.