from __future__ import annotations

import re
import time
from datetime import datetime
from typing import Dict, List

import feedparser
from googlesearch import search
from newspaper import Article

LATAM_COUNTRIES = [
    'Argentina', 'Bolivia', 'Brazil', 'Chile', 'Colombia', 'Costa Rica', 'Cuba',
    'Dominican Republic', 'Ecuador', 'El Salvador', 'Guatemala', 'Honduras',
    'Mexico', 'Nicaragua', 'Panama', 'Paraguay', 'Peru', 'Uruguay', 'Venezuela'
]

SECTOR_KEYWORDS = {
    'Energy': ['energy', 'renewable', 'solar', 'wind', 'hydro'],
    'Manufacturing': ['plant', 'factory', 'manufacturing', 'assembly'],
    'Technology': ['technology', 'software', 'data center', 'ai', 'cloud'],
    'Infrastructure': ['port', 'rail', 'infrastructure', 'airport'],
    'Finance': ['bank', 'financial', 'fintech', 'investment fund'],
    'Mining': ['mining', 'copper', 'lithium', 'extractive'],
}

FDI_CORE_KEYWORDS = [
    'fdi', 'foreign direct investment', 'inversión extranjera',
    'greenfield', 'capital expenditure', 'capex', 'investment project',
    'manufacturing investment', 'plant expansion', 'factory expansion'
]

DEAL_TERMS = [
    'investment', 'invests', 'investirá', 'announce', 'project', 'facility',
    'expansion', 'build', 'construct', 'develop', 'partnership'
]

EXCLUDE_KEYWORDS = [
    'middle east', 'africa', 'asia', 'europe', 'australia', 'new zealand'
]

MIN_RELEVANCE_SCORE = 6


def clean_text(value: str) -> str:
    return ' '.join(value.split()) if value else ''


def score_article_relevance(title: str, summary: str, text: str) -> int:
    combined = f"{title} {summary} {text}".lower()
    score = 0

    score += sum(3 for kw in FDI_CORE_KEYWORDS if kw in combined)
    score += sum(2 for kw in DEAL_TERMS if kw in combined)
    score += sum(2 for country in LATAM_COUNTRIES if country.lower() in combined)

    if any(word in combined for word in EXCLUDE_KEYWORDS):
        score -= 4

    return score


def is_fdi_latin_america_related(title: str, summary: str, text: str) -> bool:
    return score_article_relevance(title, summary, text) >= MIN_RELEVANCE_SCORE


def extract_fdi_details(text: str) -> Dict[str, List[str]]:
    text = text or ''
    lower_text = text.lower()

    countries = [c for c in LATAM_COUNTRIES if c.lower() in lower_text]

    sectors = []
    for sector, keywords in SECTOR_KEYWORDS.items():
        if any(keyword in lower_text for keyword in keywords):
            sectors.append(sector)

    amount_pattern = r'(?:US\$|\$|USD\s?)?[\d,.]+\s?(?:million|billion|m|bn|b)?'
    amounts = re.findall(amount_pattern, text, flags=re.IGNORECASE)

    company_pattern = r'([A-Z][A-Za-z0-9&\- ]{2,})(?:\s+(?:Corp|Corporation|S\.A\.|SA|Inc|LLC|Group|Holdings|S\.A\. de C\.V\.))'
    companies = [match.strip() for match in re.findall(company_pattern, text)]

    return {
        'countries': sorted(set(countries)),
        'sectors': sorted(set(sectors)),
        'amount': amounts[0] if amounts else '',
        'company': companies[0] if companies else '',
    }


def build_news_item(title: str, url: str, summary: str, published: str, source: str, text: str, origin: str = 'rss') -> Dict:
    clean_summary = clean_text(summary)[:700]
    clean_text_content = clean_text(text)
    details = extract_fdi_details(clean_text_content or clean_summary)
    relevance = score_article_relevance(title, summary, clean_text_content)

    return {
        'title': title,
        'url': url,
        'summary': clean_summary,
        'published': published,
        'source': source,
        'content': clean_text_content,
        'relevance_score': relevance,
        'countries': details['countries'],
        'country': details['countries'][0] if details['countries'] else '',
        'sectors': details['sectors'],
        'sector': details['sectors'][0] if details['sectors'] else '',
        'amount': details['amount'],
        'company': details['company'],
        'origin': origin,
    }


def parse_article(url: str) -> Article:
    article = Article(url)
    article.download()
    article.parse()
    return article


def search_fdi_news(query: str = "FDI projects Latin America", num_results: int = 20):
    news_items = []
    urls_found = set()

    search_query = (
        "FDI foreign direct investment Latin America Argentina Brazil Chile Colombia "
        "Mexico Peru AND project"
    )
    google_news_url = (
        f"https://news.google.com/rss/search?q={search_query.replace(' ', '+')}+when:10d&hl=en&gl=US&ceid=US:en"
    )

    try:
        feed = feedparser.parse(google_news_url)
        for entry in feed.entries[:num_results * 3]:
            if entry.link in urls_found:
                continue

            entry_title = entry.title or ''
            entry_summary = entry.get('summary', '') or ''

            try:
                article = parse_article(entry.link)
                article_text = article.text or ''
            except Exception:
                article = None
                article_text = ''

            if not is_fdi_latin_america_related(entry_title, entry_summary, article_text):
                continue

            news_items.append(
                build_news_item(
                    title=entry_title,
                    url=entry.link,
                    summary=article_text[:600] if article_text else entry_summary,
                    published=entry.get('published', ''),
                    source=entry.get('source', {}).get('title', 'Google News'),
                    text=article_text,
                )
            )
            urls_found.add(entry.link)
            if len(news_items) >= num_results:
                break
            time.sleep(0.5)
    except Exception as exc:
        print(f"Error fetching Google News: {exc}")

    if len(news_items) < num_results:
        try:
            fallback_query = (
                "(FDI OR 'foreign direct investment') Latin America site:reuters.com OR site:bloomberg.com "
                "OR site:bloomberglinea.com OR site:bnamericas.com"
            )
            for url in search(fallback_query, num=min(25, num_results * 3), stop=25):
                if url in urls_found:
                    continue

                try:
                    article = parse_article(url)
                except Exception:
                    continue

                if not is_fdi_latin_america_related(article.title or '', article.text[:300], article.text):
                    continue

                news_items.append(
                    build_news_item(
                        title=article.title or 'No title',
                        url=url,
                        summary=article.text[:600],
                        published=article.publish_date.strftime('%Y-%m-%d') if article.publish_date else '',
                        source=url.split('/')[2] if '/' in url else 'Unknown',
                        text=article.text,
                        origin='web',
                    )
                )
                urls_found.add(url)
                if len(news_items) >= num_results:
                    break
                time.sleep(0.5)
        except Exception as exc:
            print(f"Error in web search: {exc}")

    return news_items[:num_results]


def search_fdi_news_by_date(search_date: str, num_results: int = 10):
    news_items = []
    urls_found = set()

    try:
        target_date = datetime.strptime(search_date, '%Y-%m-%d')
    except ValueError:
        return []

    base_query = "FDI foreign direct investment Latin America"
    query_encoded = base_query.replace(' ', '+')
    google_news_url = f"https://news.google.com/rss/search?q={query_encoded}&hl=en&gl=US&ceid=US:en"

    try:
        feed = feedparser.parse(google_news_url)
        for entry in feed.entries[:num_results * 4]:
            if entry.link in urls_found:
                continue

            entry_date_str = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                entry_date = datetime(*entry.published_parsed[:6])
                entry_date_str = entry_date.strftime('%Y-%m-%d')

            if entry_date_str and entry_date_str != search_date:
                continue

            try:
                article = parse_article(entry.link)
                article_text = article.text or ''
            except Exception:
                article = None
                article_text = ''

            if not is_fdi_latin_america_related(entry.title or '', entry.get('summary', ''), article_text):
                continue

            news_items.append(
                build_news_item(
                    title=entry.title,
                    url=entry.link,
                    summary=article_text[:600] if article_text else entry.get('summary', ''),
                    published=entry.get('published', ''),
                    source=entry.get('source', {}).get('title', 'Google News'),
                    text=article_text,
                )
            )
            news_items[-1]['date'] = search_date
            urls_found.add(entry.link)
            if len(news_items) >= num_results:
                break
            time.sleep(0.5)
    except Exception as exc:
        print(f"Error fetching Google News by date: {exc}")

    if len(news_items) < num_results:
        try:
            date_query = f"{base_query} {search_date}"
            fallback_query = (
                f"{date_query} site:reuters.com OR site:bloomberg.com OR site:ft.com OR site:bloomberglinea.com"
            )
            for url in search(fallback_query, num=min(20, num_results * 3), stop=20):
                if url in urls_found:
                    continue

                try:
                    article = parse_article(url)
                except Exception:
                    continue

                if not is_fdi_latin_america_related(article.title or '', article.text[:300], article.text):
                    continue

                news_items.append(
                    build_news_item(
                        title=article.title or 'No title',
                        url=url,
                        summary=article.text[:600],
                        published=article.publish_date.strftime('%Y-%m-%d') if article.publish_date else search_date,
                        source=url.split('/')[2] if '/' in url else 'Unknown',
                        text=article.text,
                        origin='web',
                    )
                )
                news_items[-1]['date'] = search_date
                urls_found.add(url)
                if len(news_items) >= num_results:
                    break
                time.sleep(0.5)
        except Exception as exc:
            print(f"Error in date-specific web search: {exc}")

    return news_items[:num_results]
