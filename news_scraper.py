import requests
from bs4 import BeautifulSoup
from googlesearch import search
import feedparser
from newspaper import Article
import time

def search_fdi_news(query="FDI projects Latin America", num_results=10):
    """
    Search for FDI news using multiple sources
    """
    news_items = []
    
    # Search terms for Latin America FDI
    search_terms = [
        f"{query} investment",
        f"{query} foreign direct investment",
        "FDI Latin America projects",
        "foreign investment Latin America",
        "inversión extranjera América Latina"
    ]
    
    # Use Google News RSS feeds and web search
    urls_found = set()
    
    # Search Google News
    try:
        google_news_url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}+when:7d&hl=en&gl=US&ceid=US:en"
        feed = feedparser.parse(google_news_url)
        
        for entry in feed.entries[:num_results]:
            if entry.link not in urls_found:
                try:
                    article = Article(entry.link)
                    article.download()
                    article.parse()
                    
                    news_items.append({
                        'title': entry.title,
                        'url': entry.link,
                        'summary': article.text[:500] if article.text else entry.get('summary', ''),
                        'published': entry.get('published', ''),
                        'source': entry.get('source', {}).get('title', 'Unknown')
                    })
                    urls_found.add(entry.link)
                    time.sleep(1)  # Be respectful with requests
                except:
                    # Fallback to RSS data
                    news_items.append({
                        'title': entry.title,
                        'url': entry.link,
                        'summary': entry.get('summary', '')[:500],
                        'published': entry.get('published', ''),
                        'source': entry.get('source', {}).get('title', 'Unknown')
                    })
                    urls_found.add(entry.link)
    except Exception as e:
        print(f"Error fetching Google News: {e}")
    
    # Additional web search as fallback
    if len(news_items) < num_results:
        try:
            search_query = f"{query} site:reuters.com OR site:bloomberg.com OR site:ft.com OR site:wsj.com"
            for url in search(search_query, num=min(10, num_results - len(news_items)), stop=10):
                if url not in urls_found:
                    try:
                        article = Article(url)
                        article.download()
                        article.parse()
                        
                        news_items.append({
                            'title': article.title or 'No title',
                            'url': url,
                            'summary': article.text[:500] if article.text else '',
                            'published': article.publish_date.strftime('%Y-%m-%d') if article.publish_date else '',
                            'source': url.split('/')[2] if '/' in url else 'Unknown'
                        })
                        urls_found.add(url)
                        time.sleep(1)
                    except:
                        pass
        except Exception as e:
            print(f"Error in web search: {e}")
    
    return news_items[:num_results]

def extract_fdi_details(text):
    """
    Extract FDI project details from text
    """
    details = {
        'country': '',
        'sector': '',
        'amount': '',
        'company': ''
    }
    
    # Simple keyword extraction (can be enhanced with NLP)
    latin_american_countries = [
        'Argentina', 'Brazil', 'Chile', 'Colombia', 'Mexico', 'Peru',
        'Ecuador', 'Uruguay', 'Paraguay', 'Bolivia', 'Venezuela',
        'Costa Rica', 'Panama', 'Guatemala', 'Honduras', 'Nicaragua'
    ]
    
    for country in latin_american_countries:
        if country.lower() in text.lower():
            details['country'] = country
            break
    
    return details

