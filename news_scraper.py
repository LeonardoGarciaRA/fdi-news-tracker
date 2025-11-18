import requests
from bs4 import BeautifulSoup
from googlesearch import search
import feedparser
from newspaper import Article
import time
from datetime import datetime, timedelta

def is_fdi_latin_america_related(title, summary, text):
    """
    Check if article is related to FDI in Latin America
    """
    combined_text = f"{title} {summary} {text}".lower()
    
    # Must contain FDI-related terms
    fdi_keywords = [
        'fdi', 'foreign direct investment', 'inversión extranjera',
        'foreign investment', 'direct investment', 'investment project',
        'capital investment', 'multinational', 'cross-border investment'
    ]
    
    # Must contain Latin America country or region
    latin_america_keywords = [
        'latin america', 'américa latina', 'south america', 'américa del sur',
        'argentina', 'brazil', 'brasil', 'chile', 'colombia', 'mexico', 'méxico',
        'peru', 'perú', 'ecuador', 'uruguay', 'paraguay', 'bolivia', 'venezuela',
        'costa rica', 'panama', 'panamá', 'guatemala', 'honduras', 'nicaragua',
        'el salvador', 'dominican republic', 'republica dominicana'
    ]
    
    # Exclude non-Latin America regions
    exclude_keywords = [
        'mozambique', 'africa', 'asia', 'europe', 'middle east',
        'china', 'india', 'japan', 'korea', 'australia'
    ]
    
    has_fdi = any(keyword in combined_text for keyword in fdi_keywords)
    has_latin_america = any(keyword in combined_text for keyword in latin_america_keywords)
    has_exclude = any(keyword in combined_text for keyword in exclude_keywords)
    
    # Must have FDI term AND Latin America reference, AND not have exclude terms
    return has_fdi and has_latin_america and not has_exclude

def search_fdi_news(query="FDI projects Latin America", num_results=20):
    """
    Search for FDI news using multiple sources - focused on Latin America
    """
    news_items = []
    
    # More specific search query for Latin America FDI
    base_query = "(FDI OR 'foreign direct investment' OR 'inversión extranjera') AND ('Latin America' OR 'América Latina' OR Argentina OR Brazil OR Chile OR Colombia OR Mexico OR Peru)"
    
    # Use Google News RSS feeds and web search
    urls_found = set()
    
    # Search Google News with more specific query
    try:
        # Use a more targeted query
        search_query = "FDI foreign direct investment Latin America Argentina Brazil Chile Colombia Mexico Peru"
        google_news_url = f"https://news.google.com/rss/search?q={search_query.replace(' ', '+')}+when:7d&hl=en&gl=US&ceid=US:en"
        feed = feedparser.parse(google_news_url)
        
        for entry in feed.entries[:num_results * 2]:  # Get more to filter
            if entry.link not in urls_found:
                entry_title = entry.title or ''
                entry_summary = entry.get('summary', '') or ''
                
                # Quick filter before downloading article
                if not is_fdi_latin_america_related(entry_title, entry_summary, ''):
                    continue
                
                try:
                    article = Article(entry.link)
                    article.download()
                    article.parse()
                    
                    article_text = article.text or ''
                    full_text = f"{entry_title} {entry_summary} {article_text}"
                    
                    # Double-check with full article text
                    if is_fdi_latin_america_related(entry_title, entry_summary, article_text):
                        news_items.append({
                            'title': entry.title,
                            'url': entry.link,
                            'summary': article.text[:500] if article.text else entry.get('summary', ''),
                            'published': entry.get('published', ''),
                            'source': entry.get('source', {}).get('title', 'Unknown')
                        })
                        urls_found.add(entry.link)
                        if len(news_items) >= num_results:
                            break
                    time.sleep(1)  # Be respectful with requests
                except:
                    # Fallback: only include if RSS data passes filter
                    if is_fdi_latin_america_related(entry_title, entry_summary, ''):
                        news_items.append({
                            'title': entry.title,
                            'url': entry.link,
                            'summary': entry.get('summary', '')[:500],
                            'published': entry.get('published', ''),
                            'source': entry.get('source', {}).get('title', 'Unknown')
                        })
                        urls_found.add(entry.link)
                        if len(news_items) >= num_results:
                            break
    except Exception as e:
        print(f"Error fetching Google News: {e}")
    
    # Additional web search as fallback - more targeted
    if len(news_items) < num_results:
        try:
            # More specific search for Latin America FDI
            search_query = f"FDI foreign direct investment Latin America Argentina Brazil Chile Colombia Mexico Peru site:reuters.com OR site:bloomberg.com OR site:bloomberglinea.com OR site:ft.com"
            for url in search(search_query, num=min(20, (num_results - len(news_items)) * 2), stop=20):
                if url not in urls_found and len(news_items) < num_results:
                    try:
                        article = Article(url)
                        article.download()
                        article.parse()
                        
                        article_title = article.title or ''
                        article_text = article.text or ''
                        
                        # Filter to ensure it's FDI in Latin America
                        if is_fdi_latin_america_related(article_title, article_text[:200], article_text):
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

