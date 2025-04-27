from nltk.sentiment.vader import SentimentIntensityAnalyzer
from transformers import pipeline, MarianMTModel, MarianTokenizer
import torch
import re
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

# Load VADER sentiment analyzer
vader = SentimentIntensityAnalyzer()

# Load zero-shot classification pipeline (optimized with device map)
try:
    topic_classifier = pipeline(
        "zero-shot-classification",
        model="facebook/bart-large-mnli",
        device=0 if torch.cuda.is_available() else -1
    )
except Exception as e:
    logging.warning(f"Failed to load topic classifier: {e}")
    topic_classifier = None  # fallback will be used

# Load transformer-based sentiment analyzer
try:
    transformer_sentiment = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
except Exception as e:
    logging.warning(f"Failed to load transformer sentiment analyzer: {e}")
    transformer_sentiment = None

# Translation enabled for multilingual support
USE_TRANSLATION = True
if USE_TRANSLATION:
    translation_model_name = "Helsinki-NLP/opus-mt-mul-en"
    translator_model = MarianMTModel.from_pretrained(translation_model_name)
    translator_tokenizer = MarianTokenizer.from_pretrained(translation_model_name)

# Topics
CIVIC_TOPICS = [
    "infrastructure", "water supply", "electricity", "sanitation",
    "public safety", "health", "transport", "garbage collection",
    "road maintenance", "education", "pollution", "government services"
]

# Urgent keywords (in English only, rely on translation for others)
URGENT_KEYWORDS = [
    "urgent", "immediately", "emergency", "accident", "fire", "flood", "collapsed",
    "danger", "ambulance", "police", "dead", "injured", "asap", "violence", "attack"
]

# Topic keyword fallback map
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
        logging.error(f"Translation failed: {e}")
        return text  # Fallback to original text

# Sentiment classification
def get_sentiment(text):
    if transformer_sentiment:
        result = transformer_sentiment(text)[0]
        return result['label'].capitalize()  # Returns "Positive" or "Negative"
    else:
        scores = vader.polarity_scores(text)
        compound = scores['compound']
        if compound >= 0.05:
            return "Positive"
        elif compound <= -0.05:
            return "Negative"
        else:
            return "Neutral"

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
            return get_topic_keyword(text)  # Fallback to keyword-based
    else:
        return get_topic_keyword(text)

# Keyword-based fallback
def get_topic_keyword(text):
    text_lower = text.lower()
    matches = {topic: sum(kw in text_lower for kw in kws)
               for topic, kws in TOPIC_KEYWORDS.items()}
    best = max(matches, key=matches.get)
    return best, matches

# Priority scoring
def get_priority_score(sentiment, urgency):
    sentiment_score = {"Negative": 50, "Neutral": 30, "Positive": 10}
    urgency_score = {"Urgent": 50, "Not Urgent": 0}
    return sentiment_score[sentiment] + urgency_score[urgency]

# Main function
def analyze_feedback(text):
    logging.info(f"Analyzing feedback: {text}")
    original = text

    try:
        english = translate_to_english(text) if USE_TRANSLATION else text
    except Exception as e:
        logging.error(f"Translation failed: {e}")
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
    logging.info(f"Analysis result: {result}")
    return result

# Sample test
if __name__ == "__main__":
    test_inputs = [
        "पानी की सप्लाई पिछले 3 दिनों से बंद है। कृपया तुरंत ध्यान दें।",
        "There was a fire near the bus stand. Immediate help needed.",
        "The new footpath construction is amazing!",
        "The garbage collection in our area has been consistent. Thanks!",
        "हमारे मोहल्ले में बहुत गंदगी है और मच्छर फैल रहे हैं।",
        "Il y a eu une fuite de gaz près de l'école. Veuillez agir immédiatement.",
        "È scoppiato un incendio in via Roma. È urgente intervenire!",
        "सड़क पर गड्ढे हैं जिससे दुर्घटना हो सकती है।",
        "Luz não está funcionando no meu bairro há dois dias."
    ]
    for i, txt in enumerate(test_inputs, 1):
        print(f"\nFeedback {i}:")
        result = analyze_feedback(txt)
        for k, v in result.items():
            print(f"{k}: {v}")