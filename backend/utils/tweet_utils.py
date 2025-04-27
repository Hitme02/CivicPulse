from datetime import datetime, timezone
import re

def parse_twitter_timestamp(timestamp_str):
    """
    Parse Twitter's timestamp format into a datetime object
    Args:
        timestamp_str: String timestamp in Twitter format (e.g. "Sun Apr 27 02:30:12 +0000 2025")
    Returns:
        datetime object with UTC timezone
    """
    try:
        dt = datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %z %Y")
        return dt
    except Exception as e:
        print(f"Error parsing timestamp: {e}")
        return datetime.now(timezone.utc)

def extract_hashtags(tweet_text):
    """
    Extract hashtags from tweet text
    Args:
        tweet_text: The text of the tweet
    Returns:
        List of hashtags found in the tweet
    """
    # Find all words starting with # character
    hashtags = re.findall(r'#(\w+)', tweet_text)
    return hashtags

def calculate_priority_score(sentiment, urgency):
    """
    Calculate priority score based on sentiment and urgency
    Args:
        sentiment: String sentiment (Positive, Negative, Neutral)
        urgency: String urgency (Urgent, Not Urgent)
    Returns:
        Integer priority score
    """
    sentiment_score = {"Negative": 50, "Neutral": 30, "Positive": 10}
    urgency_score = {"Urgent": 50, "Not Urgent": 0}
    
    return sentiment_score.get(sentiment, 30) + urgency_score.get(urgency, 0)
