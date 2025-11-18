# FDI News Tracker - Latin America

A web application that searches for and tracks Foreign Direct Investment (FDI) projects in Latin America, with automatic summarization and Excel export functionality.

## Features

- 🔍 Search for FDI news in Latin America
- 📝 Automatic article summarization
- 🔗 Direct links to original sources
- 📊 Export collected data to Excel
- 📱 Responsive, modern UI

## Quick Start

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Download NLTK data:
```bash
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

3. Run the application:
```bash
python3 app.py
```

4. Open your browser: http://localhost:5000

## Deployment

### Option 1: Render (Recommended - Free)

1. Sign up at https://render.com (free account)
2. Click "New +" → "Web Service"
3. Connect your GitHub repository or upload files
4. Configure:
   - **Name**: fdi-news-tracker
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt && python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"`
   - **Start Command**: `gunicorn app:app`
5. Click "Create Web Service"
6. Your app will be live in a few minutes!

### Option 2: Railway

1. Sign up at https://railway.app
2. Click "New Project" → "Deploy from GitHub repo"
3. Connect your repository
4. Railway auto-detects and deploys
5. Done!

### Option 3: PythonAnywhere

1. Sign up at https://www.pythonanywhere.com
2. Upload your files via the Files tab
3. Create a new web app (Flask)
4. Install dependencies in Bash console
5. Configure WSGI file
6. Reload web app

## Project Structure

```
fdi-news-tracker/
├── app.py              # Flask application
├── news_scraper.py     # News search logic
├── summarizer.py       # Article summarization
├── excel_export.py     # Excel export functionality
├── templates/          # HTML templates
├── static/             # CSS and JavaScript
└── requirements.txt    # Python dependencies
```

## Usage

1. Enter a search query (e.g., "FDI Brazil manufacturing")
2. Click "Search News" to find articles
3. View summaries and click links to read full articles
4. Click "Export to Excel" to download all collected data

## Notes

- News is stored in memory (cleared on restart)
- For production, consider adding a database
- Respect robots.txt and terms of service when scraping

## License

MIT

