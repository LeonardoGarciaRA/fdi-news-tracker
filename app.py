from flask import Flask, render_template, jsonify, request, send_file
from news_scraper import search_fdi_news, search_fdi_news_by_date
from summarizer import summarize_article
from excel_export import export_to_excel
import os
from datetime import datetime

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Store collected news
collected_news = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_news():
    """Search for FDI news in Latin America"""
    try:
        data = request.json
        query = data.get('query', 'FDI projects Latin America')
        num_results = data.get('num_results', 10)
        
        # Search for news
        news_items = search_fdi_news(query, num_results)
        
        # Summarize each article
        for item in news_items:
            if 'summary' not in item or not item['summary']:
                item['summary'] = summarize_article(item.get('url', ''))
        
        # Add timestamp
        for item in news_items:
            item['collected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Store in memory (in production, use a database)
        collected_news.extend(news_items)
        
        return jsonify({
            'success': True,
            'news': news_items,
            'count': len(news_items)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/news', methods=['GET'])
def get_news():
    """Get all collected news"""
    return jsonify({
        'success': True,
        'news': collected_news,
        'count': len(collected_news)
    })

@app.route('/api/export', methods=['GET'])
def export_excel():
    """Export collected news to Excel"""
    try:
        filename = export_to_excel(collected_news)
        return send_file(
            filename,
            as_attachment=True,
            download_name=f'fdi_projects_{datetime.now().strftime("%Y%m%d_%H%M%S")}.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/search/date', methods=['POST'])
def search_news_by_date():
    """Search for FDI news in Latin America for a specific date"""
    try:
        data = request.json
        search_date = data.get('date', None)  # Format: YYYY-MM-DD
        num_results = data.get('num_results', 10)
        
        if not search_date:
            return jsonify({
                'success': False,
                'error': 'Date is required'
            }), 400
        
        # Search for news on specific date
        news_items = search_fdi_news_by_date(search_date, num_results)
        
        # Summarize each article
        for item in news_items:
            if 'summary' not in item or not item['summary']:
                item['summary'] = summarize_article(item.get('url', ''))
        
        # Add timestamp
        for item in news_items:
            item['collected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            item['search_date'] = search_date
        
        # Store in memory
        collected_news.extend(news_items)
        
        return jsonify({
            'success': True,
            'news': news_items,
            'count': len(news_items),
            'search_date': search_date
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/clear', methods=['POST'])
def clear_news():
    """Clear collected news"""
    global collected_news
    collected_news = []
    return jsonify({'success': True, 'message': 'News cleared'})

if __name__ == '__main__':
    # Create data directory if it doesn't exist
    os.makedirs('data', exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=True, host='0.0.0.0', port=port)

