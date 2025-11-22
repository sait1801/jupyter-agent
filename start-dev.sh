#!/bin/bash
# Jupyter Agent - Development Server Launcher for Mac/Linux

echo "🚀 Starting Jupyter Agent Development Servers..."
echo ""

# Check if .env exists
if [ ! -f "backend/.env" ]; then
    echo "❌ Error: backend/.env not found!"
    echo "Please run setup.sh first and configure your API key."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: Virtual environment not found!"
    echo "Please run setup.sh first."
    exit 1
fi

echo "📋 Starting Backend Server..."
echo "   - API will be available at: http://localhost:8000"
echo ""

# Start backend in background
cd backend
source ../.venv/bin/activate
python main.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 2

echo "📋 Starting Frontend Server..."
echo "   - App will be available at: http://localhost:5173"
echo ""

# Start frontend in background
cd frontend
python3 -m http.server 5173 &
FRONTEND_PID=$!
cd ..

# Wait for frontend to start
sleep 2

echo "✅ Both servers are running!"
echo ""
echo "🌐 Open your browser and navigate to:"
echo "   http://localhost:5173"
echo ""
echo "📚 Useful URLs:"
echo "   - Frontend:  http://localhost:5173"
echo "   - Backend:   http://localhost:8000"
echo "   - API Docs:  http://localhost:8000/docs"
echo ""
echo "💡 Press Ctrl+C to stop both servers"
echo ""
echo "🎉 Happy coding!"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ Servers stopped"
    exit 0
}

# Trap Ctrl+C
trap cleanup INT TERM

# Wait for user interrupt
wait
