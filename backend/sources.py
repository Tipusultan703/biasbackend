# backend/sources.py
from urllib.parse import urlparse

TRUSTED_SOURCES = {
    "bbc.com": "High",
    "nytimes.com": "High",
    "foxnews.com": "Medium",
    "indianexpress.com": "High",
    "reuters.com": "High",
    "theguardian.com": "High",
    "breitbart.com": "Low",
    "oann.com": "Low"
}

def extract_domain(url):
    """Extracts domain name from URL correctly."""
    parsed_url = urlparse(url)
    domain = parsed_url.netloc.replace("www.", "").split('/')[0]
    return domain

def get_source_rating(url):
    """Check if the domain is a trusted news source."""
    domain = extract_domain(url)
    return TRUSTED_SOURCES.get(domain, "Unknown")


