from __future__ import annotations

from typing import List, Optional

import re

from newspaper import Article
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from transformers import pipeline

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

_AI_SUMMARIZER = None
_SUMMARIZER_MODEL = "sshleifer/distilbart-cnn-12-6"


def _get_ai_summarizer():
    """Lazy-load the transformer summarization pipeline."""
    global _AI_SUMMARIZER
    if _AI_SUMMARIZER is None:
        _AI_SUMMARIZER = pipeline("summarization", model=_SUMMARIZER_MODEL)
    return _AI_SUMMARIZER


def _chunk_text(text: str, max_chars: int = 1800) -> List[str]:
    """Split long articles into smaller chunks to respect token limits."""
    cleaned = text.replace("\r", " ").replace("  ", " ").strip()
    if not cleaned:
        return []

    chunks = []
    current = []
    current_len = 0
    for sentence in sent_tokenize(cleaned):
        if current_len + len(sentence) > max_chars and current:
            chunks.append(" ".join(current))
            current = []
            current_len = 0
        current.append(sentence)
        current_len += len(sentence)

    if current:
        chunks.append(" ".join(current))

    return chunks or [cleaned[:max_chars]]


def generate_ai_summary(text: str) -> Optional[str]:
    """Generate an abstractive summary using a transformer pipeline."""
    if not text or len(text.split()) < 40:
        return None

    try:
        summarizer = _get_ai_summarizer()
        chunks = _chunk_text(text)
        summaries = []
        for chunk in chunks:
            summary = summarizer(
                chunk,
                max_length=180,
                min_length=60,
                do_sample=False,
            )[0]["summary_text"].strip()
            summaries.append(summary)
        return " ".join(summaries)[:800]
    except Exception as exc:
        # Fall back to extractive summary when the transformer cannot run
        print(f"AI summarizer unavailable: {exc}")
        return None


def _extractive_summary(text: str, max_sentences: int = 3) -> str:
    """Simple frequency-based extractive summary as a fallback."""
    sentences = sent_tokenize(text)
    if not sentences:
        return "Unable to extract content from article."

    words = word_tokenize(text.lower())
    try:
        stop_words = set(stopwords.words('english') + stopwords.words('spanish'))
    except LookupError:
        stop_words = set(stopwords.words('english'))

    words = [w for w in words if w.isalnum() and w not in stop_words]
    word_freq = {}
    for word in words:
        word_freq[word] = word_freq.get(word, 0) + 1

    sentence_scores = {}
    for sentence in sentences:
        sentence_words = word_tokenize(sentence.lower())
        score = sum([word_freq.get(word, 0) for word in sentence_words if word.isalnum()])
        sentence_scores[sentence] = score

    sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
    summary = ' '.join([s[0] for s in sorted_sentences[:max_sentences]])
    return summary[:500]


def _get_article_text(url: str) -> str:
    article = Article(url)
    article.download()
    article.parse()
    return article.text or ""


def summarize_article(url: str, article_text: Optional[str] = None, max_sentences: int = 3) -> str:
    """Summarize an article prioritizing an AI model with extractive fallback."""
    try:
        text = article_text or _get_article_text(url)
        if not text:
            return "Unable to extract content from article."

        ai_summary = generate_ai_summary(text)
        if ai_summary:
            return ai_summary

        return _extractive_summary(text, max_sentences=max_sentences)
    except Exception as exc:
        return f"Summary unavailable. Error: {str(exc)[:100]}"


def extract_fdi_keywords(text: str):
    """
    Extract FDI-related keywords and information
    """
    keywords = {
        'investment_amount': '',
        'country': '',
        'sector': '',
        'company': ''
    }

    if not text:
        return keywords

    amount_pattern = r'\$[\d,]+(?:\s*(?:million|billion|M|B))?'
    amounts = re.findall(amount_pattern, text, re.IGNORECASE)
    if amounts:
        keywords['investment_amount'] = amounts[0]

    countries = ['Argentina', 'Brazil', 'Chile', 'Colombia', 'Mexico', 'Peru']
    for country in countries:
        if country.lower() in text.lower():
            keywords['country'] = country
            break

    return keywords
