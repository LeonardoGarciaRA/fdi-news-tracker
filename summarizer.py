from newspaper import Article
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
import re

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt', quiet=True)

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords', quiet=True)

def summarize_article(url, max_sentences=3):
    """
    Summarize an article from URL
    """
    try:
        article = Article(url)
        article.download()
        article.parse()
        
        if not article.text:
            return "Unable to extract content from article."
        
        # Simple extractive summarization
        sentences = sent_tokenize(article.text)
        
        if len(sentences) == 0:
            return "Unable to extract content from article."
        
        # Score sentences based on word frequency
        words = word_tokenize(article.text.lower())
        try:
            stop_words = set(stopwords.words('english') + stopwords.words('spanish'))
        except:
            stop_words = set(stopwords.words('english'))
        
        words = [w for w in words if w.isalnum() and w not in stop_words]
        
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Score sentences
        sentence_scores = {}
        for sentence in sentences:
            sentence_words = word_tokenize(sentence.lower())
            score = sum([word_freq.get(word, 0) for word in sentence_words if word.isalnum()])
            sentence_scores[sentence] = score
        
        # Get top sentences
        sorted_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)
        summary = ' '.join([s[0] for s in sorted_sentences[:max_sentences]])
        
        return summary[:500]  # Limit length
        
    except Exception as e:
        return f"Summary unavailable. Error: {str(e)[:100]}"

def extract_fdi_keywords(text):
    """
    Extract FDI-related keywords and information
    """
    keywords = {
        'investment_amount': '',
        'country': '',
        'sector': '',
        'company': ''
    }
    
    # Extract amounts (USD, millions, billions)
    amount_pattern = r'\$[\d,]+(?:\s*(?:million|billion|M|B))?'
    amounts = re.findall(amount_pattern, text, re.IGNORECASE)
    if amounts:
        keywords['investment_amount'] = amounts[0]
    
    # Extract countries
    countries = ['Argentina', 'Brazil', 'Chile', 'Colombia', 'Mexico', 'Peru']
    for country in countries:
        if country.lower() in text.lower():
            keywords['country'] = country
            break
    
    return keywords

