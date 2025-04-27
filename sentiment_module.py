from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import pipeline, MarianMTModel, MarianTokenizer
from langdetect import detect
import torch
import re

# Debug toggle
DEBUG = True
def log(msg):
    if DEBUG:
        print(msg)

# Load VADER sentiment analyzer
vader = SentimentIntensityAnalyzer()

# Optional Zero-shot classifier
USE_ZERO_SHOT = False
if USE_ZERO_SHOT:
    topic_classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli", device=0 if torch.cuda.is_available() else -1)
else:
    topic_classifier = None

# Load transformer-based sentiment analyzer
transformer_sentiment = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")

# Translation model for multilingual support
USE_TRANSLATION = True
translation_model_name = "Helsinki-NLP/opus-mt-mul-en"
translator_model = MarianMTModel.from_pretrained(translation_model_name)
translator_tokenizer = MarianTokenizer.from_pretrained(translation_model_name)

# Topics & Urgent keywords
CIVIC_TOPICS = [
    "infrastructure", "water supply", "electricity", "sanitation",
    "public safety", "health", "transport", "garbage collection",
    "road maintenance", "education", "pollution", "government services"
]

URGENT_KEYWORDS = [
    "urgent", "immediately", "emergency", "accident", "fire", "flood", "collapsed",
    "danger", "ambulance", "police", "dead", "injured", "asap", "violence", "attack"
]

TOPIC_KEYWORDS = {
    "infrastructure": ["road", "footpath", "building", "bridge"],
    "water supply": ["water", "tap", "pipeline", "leak"],
    "electricity": ["electric", "light", "power", "wire"],
    "sanitation": ["toilet", "drain", "sewage", "cleaning"],
    "public safety": ["crime", "police", "violence", "unsafe"],
    "health": ["hospital", "clinic", "medicine", "doctor"],
    "transport": ["bus", "metro", "train", "transport"],
    "garbage collection": ["garbage", "trash", "waste", "bin"],
    "road maintenance": ["pothole", "road", "repair", "construction"],
    "education": ["school", "teacher", "education"],
    "pollution": ["pollution", "smoke", "air", "noise"],
    "government services": ["ration", "subsidy", "aadhar", "passport", "government"]
}

# Translation function
def translate_to_english(text):
    try:
        tokens = translator_tokenizer(text, return_tensors="pt", padding=True, truncation=True)
        translation = translator_model.generate(**tokens)
        translated = translator_tokenizer.batch_decode(translation, skip_special_tokens=True)[0]
        return translated
    except Exception as e:
        log(f"Translation failed: {e}")
        return text  # fallback

# Sentiment classification
def get_sentiment(text):
    result = transformer_sentiment(text)[0]
    return result['label'].capitalize()

# Urgency detection
def get_urgency(text):
    text_lower = text.lower()
    for word in URGENT_KEYWORDS:
        if re.search(rf'\b{word}\b', text_lower):
            return "Urgent", f"Detected keyword: '{word}'"
    return "Not Urgent", "No urgent keyword found"

# Topic classification
def get_topic(text):
    if topic_classifier:
        result = topic_classifier(text, CIVIC_TOPICS)
        filtered = {label: score for label, score in zip(result['labels'], result['scores']) if score > 0.2}
        if filtered:
            best_topic = max(filtered, key=filtered.get)
            return best_topic, filtered
        else:
            return get_topic_keyword(text)
    else:
        return get_topic_keyword(text)

# Keyword-based fallback
def get_topic_keyword(text):
    text_lower = text.lower()
    matches = {topic: sum(kw in text_lower for kw in kws) for topic, kws in TOPIC_KEYWORDS.items()}
    best = max(matches, key=matches.get)
    return best, matches

# Priority scoring
def get_priority_score(sentiment, urgency):
    sentiment_score = {"Negative": 50, "Neutral": 30, "Positive": 10}
    urgency_score = {"Urgent": 50, "Not Urgent": 0}
    return sentiment_score[sentiment] + urgency_score[urgency]

# Main analysis function
def analyze_feedback(text):
    log(f"\nAnalyzing feedback: {text}")
    original = text

    # Detect language and translate if needed
    try:
        if detect(text) != 'en' and USE_TRANSLATION:
            english = translate_to_english(text)
        else:
            english = text
    except Exception as e:
        log(f"Language detection failed: {e}")
        english = text

    sentiment = get_sentiment(english)
    urgency, urgency_reason = get_urgency(english)
    topic, topic_scores = get_topic(english)
    priority = get_priority_score(sentiment, urgency)

    result = {
        "original_text": original,
        "translated_text": english,
        "sentiment": sentiment,
        "urgency": urgency,
        "urgency_reason": urgency_reason,
        "topic": topic,
        "topic_scores": topic_scores,
        "priority_score": priority
    }
    log(f"Result: {result}")
    return result

# Batch processing
def analyze_feedback_batch(text_list):
    return [analyze_feedback(text) for text in text_list]

# Quick test
if __name__ == "__main__":
    test_inputs = [
        "पानी की सप्लाई पिछले 3 दिनों से बंद है। कृपया तुरंत ध्यान दें।",
        "There was a fire near the bus stand. Immediate help needed.",
        "The new footpath construction is amazing!"
    ]
    results = analyze_feedback_batch(test_inputs)
    for i, res in enumerate(results, 1):
        print(f"\nFeedback {i}:")
        for k, v in res.items():
            print(f"{k}: {v}")
