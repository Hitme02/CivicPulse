import json
import os
from datetime import datetime, timezone
from pymongo import MongoClient
from dotenv import load_dotenv
from sentiment_module import analyze_feedback

# Load environment variables
load_dotenv()
password = os.getenv("PASSWORD")

# Connect to MongoDB
client = MongoClient(f"mongodb+srv://admin:{os.getenv('PASSWORD')}@civicpulse.cwyk8qt.mongodb.net/?retryWrites=true&w=majority&appName=civicpulse")
db = client["sample_mflix"]
tweets_collection = db["tweets"]
analysis_collection = db["analysis"]
logs_collection = db["logs"]

# Helper function to parse Twitter timestamp
def parse_twitter_timestamp(timestamp_str):
    try:
        # Parse Twitter's timestamp format
        dt = datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %z %Y")
        return dt
    except Exception as e:
        print(f"Error parsing timestamp: {e}")
        return datetime.now(timezone.utc)

def main():
    # Log start of upload process
    start_time = datetime.now(timezone.utc)
    log_entry = {
        "timestamp": start_time,
        "event": "Starting upload of all_social_issue_tweets.json to MongoDB"
    }
    logs_collection.insert_one(log_entry)
    
    # Read the JSON file
    try:
        with open('/home/shogun/hack/RVU/backend/all_social_issue_tweets.json', 'r') as file:
            tweets = json.load(file)
            print(f"Successfully loaded {len(tweets)} tweets from file")
    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return
    
    # Process each tweet
    tweets_processed = 0
    tweets_stored = 0
    analyses_stored = 0
    
    for tweet in tweets:
        tweets_processed += 1
        
        # Skip if tweet doesn't have required fields
        if not all(key in tweet for key in ['text', 'created_at', 'id', 'tagged_hashtags']):
            print(f"Skipping tweet {tweets_processed} - missing required fields")
            continue
        
        # Extract hashtags
        hashtags = tweet.get('tagged_hashtags', [])
        if not hashtags:
            # If no hashtags, create a generic one based on content
            hashtags = ['general']
        
        # Parse timestamp
        tweet_timestamp = parse_twitter_timestamp(tweet['created_at'])
        
        # Process for each hashtag
        for hashtag in hashtags:
            clean_tag = hashtag.strip('#').lower()
            
            # Store tweet in tweets collection
            tweet_doc = {
                "keyword": clean_tag,
                "tweets": {
                    "timestamp": tweet_timestamp,
                    "text": tweet["text"],
                    "favourite_count": tweet.get("favorite_count", 0),
                    "id": tweet["id"],
                    "retweet_count": tweet.get("retweet_count", 0),
                    "follower_count": tweet.get("user", {}).get("followers_count", 0),
                    "verified": tweet.get("user", {}).get("verified", False)
                }
            }
            
            # Insert tweet
            tweet_result = tweets_collection.insert_one(tweet_doc)
            tweets_stored += 1
            
            # Analyze the tweet
            analysis = analyze_feedback(tweet["text"])
            
            # Format topic scores
            formatted_topic_scores = [
                {"name": topic, "score": round(score * 100)}
                for topic, score in analysis.get('topic_scores', {}).items()
            ]
            
            # Sort topic scores descending
            formatted_topic_scores.sort(key=lambda x: x['score'], reverse=True)
            
            # Store analysis in analysis collection
            analysis_doc = {
                "keyword": clean_tag,
                "sentiment": analysis['sentiment'],
                "urgency": analysis['urgency'],
                "urgency_reason": analysis['urgency_reason'],
                "topic": analysis['topic'],
                "topic_scores": formatted_topic_scores,
                "priority_score": analysis['priority_score'],
                "timestamp": tweet_timestamp,
                "tweet_id": tweet["id"]
            }
            
            analysis_result = analysis_collection.insert_one(analysis_doc)
            analyses_stored += 1
        
        # Print progress every 10 tweets
        if tweets_processed % 10 == 0:
            print(f"Processed {tweets_processed} tweets")
    
    # Log completion
    end_time = datetime.now(timezone.utc)
    duration = (end_time - start_time).total_seconds()
    
    log_entry = {
        "timestamp": end_time,
        "event": "Completed upload of all_social_issue_tweets.json",
        "metrics": {
            "tweets_processed": tweets_processed,
            "tweets_stored": tweets_stored,
            "analyses_stored": analyses_stored,
            "duration_seconds": duration
        }
    }
    logs_collection.insert_one(log_entry)
    
    print(f"Upload complete! Processed {tweets_processed} tweets, stored {tweets_stored} tweet documents and {analyses_stored} analysis documents in {duration:.2f} seconds")

if __name__ == "__main__":
    main()


