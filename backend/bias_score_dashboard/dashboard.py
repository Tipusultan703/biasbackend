import sys
from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from difflib import ndiff

# Ensure UTF-8 encoding for output
sys.stdout.reconfigure(encoding='utf-8')

# ✅ Load RoBERTa model with custom label mapping
model_name = "roberta-base"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSequenceClassification.from_pretrained(model_name, num_labels=5)

# ✅ Define label-to-ID mapping (Fixes 'entailment' error)
label2id = {
    "Neutral": 0,
    "Left Bias": 1,
    "Right Bias": 2,
    "Sensational": 3,
    "Opinion": 4
}

# ✅ Use RoBERTa for bias detection (Fixes Label ID Error)
bias_classifier = pipeline(
    "zero-shot-classification",
    model=model,
    tokenizer=tokenizer,
    framework="pt",
    device=0  # Change to -1 if using CPU
)

# ✅ Use small & fast models for summarization & rewriting (with PyTorch)
summarizer = pipeline(
    "summarization", 
    model="sshleifer/distilbart-cnn-6-6",
    framework="pt",
    device=0
)  

rewriter = pipeline(
    "text2text-generation", 
    model="t5-small",
    framework="pt",
    device=0
)  

def detect_bias_advanced(text):
    """Detect bias using RoBERTa."""
    try:
        categories = ["Neutral", "Left Bias", "Right Bias", "Sensational", "Opinion"]
        result = bias_classifier(text, candidate_labels=categories, return_all_scores=True)
        return result
    except Exception as e:
        print(f"❌ Error in AI Bias Detection: {str(e)}")
        return {"labels": ["Neutral"], "scores": [1.0]}  

def summarize_text(text):
    """Summarize the article using a small BART model."""
    try:
        summary = summarizer(text, max_length=200, min_length=50, do_sample=False)
        return summary[0]['summary_text']
    except Exception as e:
        print(f"❌ Error in Summarization: {str(e)}")
        return text 

def rewrite_article(text):
    """Rewrite the article using T5-small without repetition."""
    try:
        rewritten = rewriter(text, max_length=200, min_length=50, do_sample=False)
        rewritten_text = rewritten[0]['generated_text']
        
        # ✅ Remove duplicate sentences
        unique_sentences = list(dict.fromkeys(rewritten_text.split(". ")))  # Remove duplicates
        return ". ".join(unique_sentences) + "."  # Join sentences properly
    except Exception as e:
        print(f"❌ Error in Rewriting: {str(e)}")
        return text


def highlight_changes(original, rewritten):
    """Compare original and rewritten text to highlight changes."""
    try:
        changes = []
        for diff in ndiff(original.split(), rewritten.split()):
            if diff.startswith("+ "):
                changes.append(f"✅ Added: {diff[2:]}")
            elif diff.startswith("- "):
                changes.append(f"❌ Removed: {diff[2:]}")
        
        return changes if changes else ["No significant changes."]
    except Exception as e:
        print(f"❌ Error in Highlighting Changes: {str(e)}")
        return ["Error detecting changes."]







