import os
import re
import logging
from urllib.parse import urlparse
from dotenv import load_dotenv
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import openai

# ✅ Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ Missing API key. Set the OPENAI_API_KEY environment variable.")

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

        if response and response.choices and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        else:
            logging.error("❌ GPT-4 response is empty or invalid.")
            return "Error: Empty response from GPT-4."

    except Exception as e:
        logging.error(f"❌ Error in GPT-4 Analysis: {str(e)}")
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

# ✅ API Routes
@app.route('/api/analyze', methods=['POST'])
def analyze_news():
    try:
        if not request.is_json:
            return jsonify({"error": "Invalid request format. Expected JSON"}), 400

        data = request.get_json()
        text = data.get("text", "").strip()
        if not text:
            return jsonify({"error": "No text provided"}), 400

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
            "bias_score": round(bias_score, 2),
            "rewritten": rewritten_text if rewritten_text else "⚠ No rewrite available.",
            "redlined_text": redlined_result
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




























