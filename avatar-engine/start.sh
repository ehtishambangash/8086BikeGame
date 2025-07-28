#!/bin/bash

# Avatar Engine Startup Script

echo "🚀 Starting Avatar Engine..."

# Check if running in development or production
if [ "$NODE_ENV" = "production" ]; then
    echo "📦 Running in production mode"
else
    echo "🔧 Running in development mode"
fi

# Create necessary directories
echo "📁 Creating storage directories..."
mkdir -p storage/{avatars,models,outputs,temp}

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

# Check if Node.js is available for frontend
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed"
    exit 1
fi

# Setup backend
echo "🐍 Setting up backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🔧 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
pip install -r requirements.txt

# Copy environment file if it doesn't exist
if [ ! -f "../.env" ]; then
    echo "📝 Creating environment file..."
    cp ../.env.example ../.env
    echo "⚠️  Please configure your .env file before running the application"
fi

# Start backend server
echo "🚀 Starting FastAPI backend server..."
python main.py &
BACKEND_PID=$!

# Setup frontend
echo "⚛️  Setting up frontend..."
cd ../frontend

# Install frontend dependencies
if [ ! -d "node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    npm install
fi

# Start frontend development server
echo "🚀 Starting React frontend server..."
npm start &
FRONTEND_PID=$!

# Function to cleanup on exit
cleanup() {
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Setup trap for cleanup
trap cleanup SIGINT SIGTERM

echo "✅ Avatar Engine is running!"
echo "🌐 Backend: http://localhost:8000"
echo "🌐 Frontend: http://localhost:3000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for processes
wait