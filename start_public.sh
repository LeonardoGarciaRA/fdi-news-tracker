#!/bin/bash
# Start app with public URL using localhost.run

cd /Users/leogj/fdi-news-tracker
source venv/bin/activate

echo "🚀 Starting FDI News Tracker..."
echo ""

# Start Flask app in background
python3 app.py > /tmp/flask_app.log 2>&1 &
FLASK_PID=$!

echo "⏳ Waiting for app to start..."
sleep 5

# Check if app is running
if curl -s http://localhost:5000 > /dev/null; then
    echo "✅ App is running on http://localhost:5000"
    echo ""
    echo "📡 Creating public tunnel..."
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Your public URL will appear below:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    # Create tunnel using localhost.run
    ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -R 80:localhost:5000 ssh.localhost.run
    
    # Cleanup on exit
    kill $FLASK_PID 2>/dev/null
else
    echo "❌ Failed to start app. Check /tmp/flask_app.log for errors"
    kill $FLASK_PID 2>/dev/null
    exit 1
fi

