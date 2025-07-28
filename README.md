# 8086BikeGame Repository

This repository contains two projects:

## 1. Classic Motorcycle Game (Assembly)
- **File**: `MotorcycleGame_ASCII_FULL_FINAL.asm`
- **Description**: A classic motorcycle game written in x86 Assembly language
- **Controls**: Use W/S to move, ESC to quit

## 2. Uncensored DreamBooth Avatar Engine
- **Directory**: `avatar-engine/`
- **Description**: A backend system for training personalized avatars using DreamBooth and generating images/videos via ComfyUI
- **Tech Stack**: Python, FastAPI, PyTorch, ComfyUI, React frontend

### Avatar Engine Features
- Upload 5-20 facial images to train personalized avatar models
- DreamBooth/LoRA training with unique tokens
- ComfyUI integration for image and video generation
- Midjourney-style frontend interface
- NSFW content support with toggle controls
- Local/RunPod compatible deployment
- Background job processing for training and generation

## Getting Started

### Assembly Game
Compile and run the assembly file using an x86 assembler like MASM or NASM.

### Avatar Engine
```bash
cd avatar-engine
pip install -r requirements.txt
python main.py
```

See `avatar-engine/README.md` for detailed setup instructions.