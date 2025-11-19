from flask import Flask, render_template, jsonify, request, send_file
from news_scraper import search_fdi_news, search_fdi_news_by_date
from summarizer import summarize_article
from excel_export import export_to_excel
import os
from datetime import datetime
from typing import List

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

# Store collected news
collected_news = []


def _prepare_news_items(news_items: List[dict]):
    """Attach AI summaries and timestamps to news items."""
    prepared = []
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    for item in news_items:
        summary = item.get('summary')
        if not summary:
            summary = summarize_article(item.get('url', ''), item.get('content'))

        enriched_item = {**item}
        enriched_item['summary'] = summary
        enriched_item['collected_at'] = now
        prepared.append(enriched_item)
    return prepared


def _merge_news_items(news_items: List[dict]):
    """Merge unique news items into the in-memory collection."""
    global collected_news
    existing_urls = {item['url']: index for index, item in enumerate(collected_news)}
    fresh_items = []

    for item in news_items:
        url = item.get('url')
        if not url:
            continue
        if url in existing_urls:
            # Update metadata for existing entries (summary, relevance, etc.)
            collected_news[existing_urls[url]].update(item)
        else:
            fresh_items.append(item)

    if fresh_items:
        collected_news = fresh_items + collected_news

    return fresh_items

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/search', methods=['POST'])
def search_news():
    """Search for FDI news in Latin America"""
    try:
        data = request.json
        query = data.get('query', 'FDI projects Latin America')
        num_results = data.get('num_results', 20)  # Default to 20 for pagination
        
        # Search for news
        news_items = search_fdi_news(query, num_results)
        news_items = _prepare_news_items(news_items)
        news_items.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        _merge_news_items(news_items)
        
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
    """Get all collected news with pagination"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Calculate pagination
    total = len(collected_news)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_news = collected_news[start:end]
    
    return jsonify({
        'success': True,
        'news': paginated_news,
        'count': len(paginated_news),
        'total': total,
        'page': page,
        'per_page': per_page,
        'total_pages': (total + per_page - 1) // per_page
    })

@app.route('/api/news/latest', methods=['GET'])
def get_latest_news():
    """Automatically fetch latest FDI news"""
    try:
        # Search for latest news (last 7 days)
        news_items = search_fdi_news("FDI foreign direct investment Latin America", 20)
        news_items = _prepare_news_items(news_items)
        news_items.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        _merge_news_items(news_items)
        
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
        news_items = _prepare_news_items(news_items)
        for item in news_items:
            item['search_date'] = search_date
        news_items.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        _merge_news_items(news_items)
        
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

