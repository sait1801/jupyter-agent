# Jupyter Agent - Setup Script
# This script helps set up the project

Write-Host "🚀 Setting up Jupyter Agent..." -ForegroundColor Cyan

# Check Python version
Write-Host "`n📋 Checking Python version..." -ForegroundColor Yellow
$pythonVersion = python --version 2>&1
Write-Host $pythonVersion -ForegroundColor Green

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "`n🔧 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
    Write-Host "✅ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "`n✅ Virtual environment already exists" -ForegroundColor Green
}

# Activate virtual environment
Write-Host "`n🔌 Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Install backend dependencies
Write-Host "`n📦 Installing backend dependencies..." -ForegroundColor Yellow
Set-Location backend
pip install -r requirements.txt
Set-Location ..
Write-Host "✅ Backend dependencies installed" -ForegroundColor Green

# Create .env file if it doesn't exist
if (-not (Test-Path "backend\.env")) {
    Write-Host "`n📝 Creating .env file..." -ForegroundColor Yellow
    Copy-Item "backend\.env.example" -Destination "backend\.env"
    Write-Host "⚠️  Please edit backend\.env and add your GEMINI_API_KEY" -ForegroundColor Yellow
} else {
    Write-Host "`n✅ .env file already exists" -ForegroundColor Green
}

# Create notebooks directory
if (-not (Test-Path "backend\notebooks")) {
    Write-Host "`n📁 Creating notebooks directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path "backend\notebooks" | Out-Null
    Write-Host "✅ Notebooks directory created" -ForegroundColor Green
}

Write-Host "`n✨ Setup complete!" -ForegroundColor Cyan
Write-Host "`nNext steps:" -ForegroundColor White
Write-Host "1. Edit backend\.env and add your GEMINI_API_KEY" -ForegroundColor White
Write-Host "2. Run: cd backend && python main.py" -ForegroundColor White
Write-Host "3. In another terminal: cd frontend && python -m http.server 5173" -ForegroundColor White
Write-Host "4. Open http://localhost:5173 in your browser" -ForegroundColor White
Write-Host "`n🎉 Happy coding!" -ForegroundColor Cyan
