# Deployment Instructions

## Quick Deploy to Render (Recommended - Free Tier)

1. Go to https://render.com and sign up (free)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository (or use the manual deploy option)
4. Configure:
   - **Name**: fdi-news-tracker
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
5. Click "Create Web Service"
6. Your app will be live at: `https://fdi-news-tracker.onrender.com` (or similar)

## Alternative: Deploy to Railway

1. Go to https://railway.app and sign up
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your repository
4. Railway will auto-detect and deploy
5. Your app will be live automatically

## Local Testing with Public URL

If you want to test locally with a public URL:

1. Make sure your Flask app is running: `python3 app.py`
2. In another terminal, run: `ssh -R 80:localhost:5000 serveo.net`
3. You'll get a public URL like: `https://xxxxx.serveo.net`

## Notes

- The app uses in-memory storage (news is lost on restart)
- For production, consider adding a database (SQLite/PostgreSQL)
- Add environment variables for API keys if needed
- Enable HTTPS in production settings

