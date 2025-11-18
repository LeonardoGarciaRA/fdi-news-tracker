#!/bin/bash
# Deployment script for FDI News Tracker

echo "🚀 Starting deployment process..."

# Check if app is running
if ! curl -s http://localhost:5000 > /dev/null; then
    echo "Starting Flask app..."
    cd /Users/leogj/fdi-news-tracker
    source venv/bin/activate
    python3 app.py > /tmp/flask_app.log 2>&1 &
    sleep 3
fi

echo "✅ App is running on http://localhost:5000"
echo ""
echo "📡 Creating public tunnel..."
echo "Your public URL will appear below:"
echo ""

# Try localhost.run first (free, no signup)
ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -R 80:localhost:5000 ssh.localhost.run 2>&1 | tee /tmp/tunnel.log

