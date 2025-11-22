#!/bin/bash
# Jupyter Agent - Setup Script for Mac/Linux

echo "🚀 Setting up Jupyter Agent..."

# Check Python version
echo ""
echo "📋 Checking Python version..."
python3 --version

# Create virtual environment
if [ ! -d ".venv" ]; then
    echo ""
    echo "🔧 Creating virtual environment..."
    python3 -m venv .venv
    echo "✅ Virtual environment created"
else
    echo ""
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo ""
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..
echo "✅ Backend dependencies installed"

# Create .env file
if [ ! -f "backend/.env" ]; then
    echo ""
    echo "📝 Creating .env file..."
    cp backend/.env.example backend/.env
    echo "⚠️  Please edit backend/.env and add your GEMINI_API_KEY"
else
    echo ""
    echo "✅ .env file already exists"
fi

# Create notebooks directory
if [ ! -d "backend/notebooks" ]; then
    echo ""
    echo "📁 Creating notebooks directory..."
    mkdir -p backend/notebooks
    echo "✅ Notebooks directory created"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit backend/.env and add your GEMINI_API_KEY"
echo "2. Run: cd backend && python main.py"
echo "3. In another terminal: cd frontend && python -m http.server 5173"
echo "4. Open http://localhost:5173 in your browser"
echo ""
echo "🎉 Happy coding!"
