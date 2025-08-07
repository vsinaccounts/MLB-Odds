#!/bin/bash

# MLB Odds Feed Web Server Startup Script
# This script starts the Flask web server that serves your MLB odds feed

echo "🏈 Starting MLB Odds Feed Web Server..."
echo "📍 Location: $(pwd)"
echo "🔑 Using Unabated API Key: ${UNABATED_API_KEY:0:8}..."
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run setup.py first."
    exit 1
fi

# Check if requirements are installed
if ! python -c "import flask" 2>/dev/null; then
    echo "📥 Installing requirements..."
    pip install -r requirements.txt
fi

# Start the server
echo "🚀 Starting web server..."
echo ""
echo "🌐 Your MLB Odds Feed URLs:"
echo "   📊 Feed: http://localhost:5000/feed"
echo "   📈 Status: http://localhost:5000/status"
echo "   🏠 Home: http://localhost:5000/"
echo ""
echo "💡 Tips:"
echo "   - Add ?pretty=true for formatted JSON"
echo "   - Feed updates every 5 minutes"
echo "   - Press Ctrl+C to stop the server"
echo ""

python web_server.py