import os
import re
import logging
from urllib.parse import urlparse
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai
from datetime import datetime 
from newspaper import Article
from bs4 import BeautifulSoup
import feedparser  # ✅ Fast RSS Parsing
import requests
from dateutil import parser
import dateutil.parser as date_parser
import pytz
import json

# ✅ Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    logging.warning("⚠ Warning: OPENAI_API_KEY is missing. Some features may not work.")


# ✅ OpenAI API Client
openai_client = openai.OpenAI(api_key=api_key)

# ✅ Configure Flask App
app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

# ✅ Configure Logging
logging.basicConfig(level=logging.DEBUG)

# ✅ Trusted News Sources Database
# ✅ Trusted News Sources Database
TRUSTED_SOURCES = {
    "bbc.com": "High",
    "nytimes.com": "High",
    "foxnews.com": "Medium",
    "indianexpress.com": "High",
    "reuters.com": "High",
    "theguardian.com": "High",
    "breitbart.com": "Low",
    "oann.com": "Low",
    "wsj.com": "High",                  
    "washingtonpost.com": "High",       
    "latimes.com": "High",              
    "bostonglobe.com": "High"   
}


# ✅ Utility Functions
def extract_domain(url):
    try:
        parsed_url = urlparse(url)
        domain_parts = parsed_url.netloc.replace("www.", "").split('.')
        return ".".join(domain_parts[-2:])
    except Exception as e:
        logging.error(f"❌ Error extracting domain from URL: {str(e)}")
        return "Unknown"

def extract_number(text):
    try:
        match = re.search(r"\d+(?:\.\d+)?", text)
        return float(match.group()) if match else None
    except Exception as e:
        logging.error(f"❌ Error extracting number: {str(e)}")
        return None

def is_valid_url(url):
    """Check if a URL is properly formatted"""
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False

def get_raw_published_date(url):
    """Returns the exact datetime string as published (preserving original timezone)"""
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml',
        'Accept-Language': 'en-US,en;q=0.9'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # 1. Check JSON-LD (Schema.org) - preserves original format
        json_ld = soup.find('script', type='application/ld+json')
        if json_ld:
            try:
                data = json.loads(json_ld.string)
                if isinstance(data, list) and len(data) > 0:
                    data = data[0]
                if data.get('datePublished'):
                    return data['datePublished']  # Returns exactly as published
            except (json.JSONDecodeError, AttributeError):
                pass

        # 2. Check OpenGraph/Meta Tags - preserves original format
        for attr, value in [
            ('property', 'article:published_time'),
            ('property', 'og:published_time'),
            ('name', 'datePublished'),
            ('itemprop', 'datePublished')
        ]:
            meta = soup.find('meta', {attr: value})
            if meta and meta.get('content'):
                return meta['content']  # Returns exactly as published

        # 3. Check HTML5 <time> tag - preserves datetime attribute exactly
        time_tag = soup.find('time')
        if time_tag and time_tag.get('datetime'):
            return time_tag['datetime']  # Returns exactly as published

        # 4. Check for other common patterns
        for selector in [
            'meta[property="article:published"]',
            'meta[name="DC.date.issued"]',
            'meta[name="sailthru.date"]'
        ]:
            tag = soup.select_one(selector)
            if tag and tag.get('content'):
                return tag['content']

        return None  # No date found

    except requests.RequestException as e:
        logging.warning(f"Request failed for {url}: {str(e)}")
        return None
    except Exception as e:
        logging.error(f"Unexpected error processing {url}: {str(e)}")
        return None


def get_published_date(url):
    """Returns the original published date string exactly as shown on the site"""
    raw_date = get_raw_published_date(url)
    
    if raw_date:
        # Return the raw date exactly as extracted (with original timezone)
        return raw_date
    
    # Fallback methods that might convert timezones (only if raw date not found)
    try:
        article = Article(url)
        article.download()
        article.parse()
        if article.publish_date:
            return article.publish_date.isoformat()  # Note: This may convert timezone
    except Exception:
        pass

    return "Original publish time not available"

@app.route('/fetch-news', methods=['GET'])
def fetch_news():
    url = request.args.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            return jsonify({"content": response.text})
        else:
            logging.error(f"❌ Failed to fetch news. Status: {response.status_code}")
            return jsonify({"error": "Failed to fetch news"}), response.status_code
    except requests.RequestException as e:
        logging.error(f"❌ Error fetching news: {e}")
        return jsonify({"error": "Request failed"}), 500



def extract_news_content(news_url):
    """Extracts full news article text from a URL with robust error handling."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "text/html,application/xhtml+xml",
            "Accept-Language": "en-US,en;q=0.9"
        }

        # Attempt with Newspaper3k first
        try:
            article = Article(news_url, language='en')
            article.download()
            article.parse()
            
            # Validate we got content
            if article.text and len(article.text) > 50:
                return {
                    "title": article.title or "Unknown Title",
                    "text": article.text,
                    "published_date": article.publish_date.strftime("%Y-%m-%d %H:%M:%S") if article.publish_date else "Unknown"
                }
        except Exception as e:
            logging.warning(f"Newspaper3k extraction failed, trying fallback: {str(e)}")

        # Fallback to BeautifulSoup if Newspaper3k fails
        try:
            response = requests.get(news_url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove unwanted elements
            for element in soup(['script', 'style', 'nav', 'footer', 'iframe']):
                element.decompose()
                
            # Try to find main content
            main_content = soup.find('article') or soup.find('main') or soup.find(class_=re.compile('content|article|main'))
            text = main_content.get_text(separator='\n') if main_content else soup.get_text(separator='\n')
            
            # Clean up text
            text = '\n'.join([line.strip() for line in text.split('\n') if line.strip()])
            
            if len(text) > 50:
                return {
                    "title": soup.title.string if soup.title else "Unknown Title",
                    "text": text,
                    "published_date": "Unknown"
                }
        except Exception as e:
            logging.error(f"Fallback extraction failed: {str(e)}")

        return {"error": "Failed to extract meaningful content from URL"}

    except Exception as e:
        logging.error(f"Critical error in content extraction: {str(e)}")
        return {"error": "Technical failure during content extraction"}

def analyze_with_gpt4(text, instructions, temperature=0):
    try:
        messages = [
            {"role": "system", "content": instructions},
            {"role": "user", "content": text}
        ]

        response = openai_client.chat.completions.create(
            model="gpt-4-turbo",
            messages=messages,
            temperature=temperature
        )

        if not response or not response.choices or not response.choices[0].message.content:
            logging.error("❌ GPT-4 response is empty or invalid.")
            return "Error: Empty response from GPT-4."

        return response.choices[0].message.content.strip()

    except openai.error.OpenAIError as e:
        logging.error(f"❌ OpenAI API Error: {str(e)}")
        return "Error: OpenAI API is unavailable."

    except Exception as e:
        logging.error(f"❌ Unexpected GPT-4 Analysis Error: {str(e)}")
        return "Error: Unexpected issue occurred."


def parse_redlined_text(text):
    try:
        logging.debug(f"🔍 GPT-4 Redlining Response: {text}")

        biased_words = []
        neutral_alternatives = []

        # Improved regex for flexibility
        biased_match = re.findall(r"(?i)Biased words:\s*\[([^\]]*)\]", text)
        neutral_match = re.findall(r"(?i)Neutral alternatives:\s*\[([^\]]*)\]", text)

        if biased_match:
            biased_words = [word.strip() for word in biased_match[0].split(",")]
        if neutral_match:
            neutral_alternatives = [word.strip() for word in neutral_match[0].split(",")]

        return {
            "biased_words": biased_words if biased_words else ["None"],
            "neutral_alternatives": neutral_alternatives if neutral_alternatives else ["None"]
        }
    except Exception as e:
        logging.error(f"❌ Error parsing redlined text: {str(e)}")
        return {"biased_words": ["Error parsing"], "neutral_alternatives": ["Error parsing"]} 
        

@app.route('/api/analyze', methods=['POST'])
def analyze_news():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid request format. Expected JSON"}), 400

        data = request.get_json()
        text = data.get("text", "").strip()
        news_url = data.get("url", "").strip()

        # Add URL validation
        if news_url and not is_valid_url(news_url):
            return jsonify({"error": "Invalid URL format. Please include http:// or https://"}), 400

        if not text and not news_url:
            return jsonify({"error": "No text or URL provided"}), 400

        if news_url:
            article_data = extract_news_content(news_url)
            if "error" in article_data:
                return jsonify({
                    "error": "Content extraction failed",
                    "details": article_data["error"],
                    "suggestion": "Try another URL or paste the text directly"
                }), 400
            
            text = article_data["text"]
            news_title = article_data["title"]
            published_date = article_data["published_date"]
        else:
            news_title = "User Provided Text" 
            published_date = "Unknown"

        # Get Bias Score
        bias_result = analyze_with_gpt4(
            text,
            "Analyze the bias in this article and return ONLY a number between 0 and 100. A higher number means more bias.",
            temperature=0
        )
        bias_score = extract_number(bias_result)
        if bias_score is None:
            return jsonify({"error": "Bias score could not be determined."}), 400

        # Get Neutral Rewritten Text
        rewritten_text = analyze_with_gpt4(
            text,
            "Rewrite this article in a fully neutral way, removing any emotionally charged language or bias.",
            temperature=0
        )

        # Get Biased Words & Neutral Alternatives
        redlined_text = analyze_with_gpt4(
            text,
            "Identify biased words and suggest neutral alternatives. Only return data in this exact format: \nBiased words: [word1, word2]\nNeutral alternatives: [alt1, alt2]\n",
            temperature=0
        )

        redlined_result = parse_redlined_text(redlined_text)
        
        return jsonify({
            "title": news_title,
            "original_article": text, 
            "published_date": published_date,
            "bias_score": round(bias_score, 2),
            "rewritten": rewritten_text if rewritten_text else "⚠ No rewrite available.",
            "redlined_text": redlined_result,
            "timestamp": published_date 
        })

    except Exception as e:
        logging.error(f"❌ Error in /api/analyze: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route('/')
def home():
    return render_template('index.html')

     
@app.route('/api/source-check', methods=['POST'])
def check_source():
    """Check the credibility of a news source."""
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid request format. Expected JSON"}), 400

        data = request.get_json()
        url = data.get("url", "").strip()

        if not url:
            return jsonify({"error": "No URL provided"}), 400

        # Extract domain and check credibility
        domain = extract_domain(url)
        credibility = TRUSTED_SOURCES.get(domain, "Unknown")

        logging.info(f"✅ Source Checked: {domain}, Credibility: {credibility}")

        return jsonify({"source": domain, "credibility": credibility})

    except Exception as e:
        logging.error(f"❌ Error in /api/source-check: {str(e)}")
        return jsonify({"error": "Internal Server Error"}), 500


# ✅ Run Flask App
if __name__ == '__main__':
    debug_mode = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    app.run(debug=debug_mode, host="0.0.0.0", port=5000)  




























