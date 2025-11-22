# Jupyter Agent - Development Server Launcher
# This script starts both backend and frontend servers

Write-Host "🚀 Starting Jupyter Agent Development Servers..." -ForegroundColor Cyan
Write-Host ""

# Check if .env exists
if (-not (Test-Path "backend\.env")) {
    Write-Host "❌ Error: backend\.env not found!" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first and configure your API key." -ForegroundColor Yellow
    exit 1
}

# Check if virtual environment exists
if (-not (Test-Path ".venv")) {
    Write-Host "❌ Error: Virtual environment not found!" -ForegroundColor Red
    Write-Host "Please run setup.ps1 first." -ForegroundColor Yellow
    exit 1
}

Write-Host "📋 Starting Backend Server..." -ForegroundColor Yellow
Write-Host "   - API will be available at: http://localhost:8000" -ForegroundColor Gray
Write-Host ""

# Start backend in a new window
$backendScript = @"
Set-Location '$PWD\backend'
& '$PWD\.venv\Scripts\Activate.ps1'
Write-Host '🐍 Backend Server Running' -ForegroundColor Green
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow
python main.py
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendScript

# Wait a bit for backend to start
Start-Sleep -Seconds 2

Write-Host "📋 Starting Frontend Server..." -ForegroundColor Yellow
Write-Host "   - App will be available at: http://localhost:5173" -ForegroundColor Gray
Write-Host ""

# Start frontend in a new window
$frontendScript = @"
Set-Location '$PWD\frontend'
Write-Host '🎨 Frontend Server Running' -ForegroundColor Green
Write-Host 'Press Ctrl+C to stop' -ForegroundColor Yellow
python -m http.server 5173
"@

Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendScript

# Wait a bit for frontend to start
Start-Sleep -Seconds 2

Write-Host "✅ Both servers are starting!" -ForegroundColor Green
Write-Host ""
Write-Host "🌐 Open your browser and navigate to:" -ForegroundColor Cyan
Write-Host "   http://localhost:5173" -ForegroundColor White
Write-Host ""
Write-Host "📚 Useful URLs:" -ForegroundColor Cyan
Write-Host "   - Frontend:  http://localhost:5173" -ForegroundColor White
Write-Host "   - Backend:   http://localhost:8000" -ForegroundColor White
Write-Host "   - API Docs:  http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tip: Check the new PowerShell windows for server logs" -ForegroundColor Yellow
Write-Host ""
Write-Host "🎉 Happy coding!" -ForegroundColor Cyan
