# backend/feedback.py
import json
import os
from datetime import datetime

BIAS_SCORE_HISTORY = "bias_scores.json"

def save_bias_score(article_text, score):
    """Save bias scores for tracking."""
    if not article_text.strip():
        return "❌ Error: Cannot save empty text."

    try:
        if os.path.exists(BIAS_SCORE_HISTORY):
            with open(BIAS_SCORE_HISTORY, "r") as f:
                data = json.load(f)
        else:
            data = []

    except json.JSONDecodeError:
        data = []

    # Store timestamped score
    data.append({
        "text": article_text[:50], 
        "bias_score": score,
        "timestamp": datetime.now().isoformat()
    })

    with open(BIAS_SCORE_HISTORY, "w") as f:
        json.dump(data, f, indent=4)

    return "✅ Bias score saved successfully!"

def get_bias_score_history():
    """Retrieve stored bias scores."""
    try:
        if os.path.exists(BIAS_SCORE_HISTORY):
            with open(BIAS_SCORE_HISTORY, "r") as f:
                return json.load(f)
        return []
    except json.JSONDecodeError:
        return []




