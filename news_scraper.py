import requests
from bs4 import BeautifulSoup
from googlesearch import search
import feedparser
from newspaper import Article
import time
from datetime import datetime, timedelta

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

def search_fdi_news_by_date(search_date, num_results=10):
    """
    Search for FDI news in Latin America for a specific date
    search_date format: YYYY-MM-DD
    """
    news_items = []
    urls_found = set()
    
    # Parse the date
    try:
        target_date = datetime.strptime(search_date, '%Y-%m-%d')
        date_str = target_date.strftime('%Y-%m-%d')
        # Format for Google News: YYYYMMDD
        google_date = target_date.strftime('%Y%m%d')
    except ValueError:
        print(f"Invalid date format: {search_date}")
        return []
    
    # Base query for FDI in Latin America
    base_query = "FDI foreign direct investment Latin America"
    
    # Search Google News for specific date
    try:
        # Google News RSS with date filter
        # Note: Google News RSS date filtering is limited, so we'll search and filter
        query_encoded = base_query.replace(' ', '+')
        google_news_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=en&gl=US&ceid=US:en"
        feed = feedparser.parse(google_news_url)
        
        for entry in feed.entries[:num_results * 2]:  # Get more to filter by date
            if entry.link not in urls_found:
                # Check if article date matches
                entry_date_str = None
                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                    try:
                        entry_date = datetime(*entry.published_parsed[:6])
                        entry_date_str = entry_date.strftime('%Y-%m-%d')
                    except:
                        pass
                
                # If date matches or we can't determine date, include it
                if entry_date_str == date_str or entry_date_str is None:
                    try:
                        article = Article(entry.link)
                        article.download()
                        article.parse()
                        
                        # Double-check date from article
                        article_date_str = None
                        if article.publish_date:
                            article_date_str = article.publish_date.strftime('%Y-%m-%d')
                        
                        # Only include if date matches
                        if article_date_str == date_str or (entry_date_str == date_str and article_date_str is None):
                            news_items.append({
                                'title': entry.title,
                                'url': entry.link,
                                'summary': article.text[:500] if article.text else entry.get('summary', ''),
                                'published': entry.get('published', ''),
                                'source': entry.get('source', {}).get('title', 'Unknown'),
                                'date': article_date_str or entry_date_str or date_str
                            })
                            urls_found.add(entry.link)
                            if len(news_items) >= num_results:
                                break
                        time.sleep(1)
                    except:
                        # Fallback: include if date from RSS matches
                        if entry_date_str == date_str:
                            news_items.append({
                                'title': entry.title,
                                'url': entry.link,
                                'summary': entry.get('summary', '')[:500],
                                'published': entry.get('published', ''),
                                'source': entry.get('source', {}).get('title', 'Unknown'),
                                'date': entry_date_str or date_str
                            })
                            urls_found.add(entry.link)
                            if len(news_items) >= num_results:
                                break
    except Exception as e:
        print(f"Error fetching Google News by date: {e}")
    
    # Additional search with date in query
    if len(news_items) < num_results:
        try:
            # Search with date-specific query
            date_query = f"{base_query} {date_str} OR {target_date.strftime('%B %d, %Y')}"
            search_query = f"{date_query} site:reuters.com OR site:bloomberg.com OR site:ft.com OR site:wsj.com OR site:bloomberglinea.com"
            
            for url in search(search_query, num=min(15, (num_results - len(news_items)) * 2), stop=15):
                if url not in urls_found and len(news_items) < num_results:
                    try:
                        article = Article(url)
                        article.download()
                        article.parse()
                        
                        # Check if article date matches
                        article_date_str = None
                        if article.publish_date:
                            article_date_str = article.publish_date.strftime('%Y-%m-%d')
                        
                        # Include if date matches or if we can't determine (might be relevant)
                        if article_date_str == date_str or article_date_str is None:
                            news_items.append({
                                'title': article.title or 'No title',
                                'url': url,
                                'summary': article.text[:500] if article.text else '',
                                'published': article.publish_date.strftime('%Y-%m-%d') if article.publish_date else date_str,
                                'source': url.split('/')[2] if '/' in url else 'Unknown',
                                'date': article_date_str or date_str
                            })
                            urls_found.add(url)
                            time.sleep(1)
                    except:
                        pass
        except Exception as e:
            print(f"Error in date-specific web search: {e}")
    
    return news_items[:num_results]

