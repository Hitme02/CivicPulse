from fastapi import FastAPI
# Import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
# Import pymongo and datetime
from pymongo import MongoClient
from datetime import datetime, timezone # Import timezone
from dotenv import load_dotenv
import os
# Import Pydantic BaseModel and List for request body validation
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
# Import the analysis function
from sentiment_module import analyze_feedback
import re # Import re for regex matching
import json
import random

load_dotenv()

# Get the password from the environment variables
password = os.getenv("PASSWORD")
app = FastAPI()

# Add CORS middleware
origins = ["*"]  # Allow all origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

# MongoDB setup
client = MongoClient(f"mongodb+srv://admin:{password}@tweets.ahxnyu0.mongodb.net/?retryWrites=true&w=majority&appName=tweets") # Replace with your MongoDB connection string if needed
db = client["sample_mflix"] # Database name - TODO: Consider renaming db if not using sample_mflix
tweets_collection = db["tweets"] # Collection name - TODO: Ensure this collection exists and has tweet data
logs_collection = db["logs"] # Collection name for logs
analysis_collection = db["analysis"] # Collection for analysis results

# Define the request body model
class SearchRequest(BaseModel):
    hashtags: List[str]
    priority_threshold: int

# Helper function to parse Twitter timestamp
def parse_twitter_timestamp(timestamp_str):
    try:
        # Parse Twitter's timestamp format
        dt = datetime.strptime(timestamp_str, "%a %b %d %H:%M:%S %z %Y")
        return dt
    except Exception as e:
        print(f"Error parsing timestamp: {e}")
        return datetime.now(timezone.utc)
        
# Dummy function to "scrape" tweets
def scrape_tweets(hashtag):
    """
    Simulates scraping tweets for a given hashtag and saves them to scrape.json
    
    Args:
        hashtag: The hashtag to search for
        
    Returns:
        List of tweets matching the hashtag
    """
    # Sample tweet template
    tweet_template = {
        "created_at": "Sun Apr 27 02:30:12 +0000 2025",
        "attached_urls": [],
        "attached_media": None,
        "tagged_users": [],
        "tagged_hashtags": [],
        "favorite_count": 0,
        "reply_count": 1,
        "retweet_count": 0,
        "text": "",
        "language": "en",
        "user_id": "2280013318",
        "id": "",
        "conversation_id": "1916318890554232972",
        "views": str(random.randint(10, 1000)),
        "user": {
            "id": None,
            "name": "Twitter User",
            "screen_name": f"user{random.randint(1000, 9999)}",
            "description": "",
            "followers_count": random.randint(100, 5000),
            "friends_count": random.randint(100, 500),
            "statuses_count": random.randint(500, 10000),
            "verified": random.choice([True, False]),
            "profile_image_url": "https://pbs.twimg.com/profile_images/default_normal.jpeg"
        }
    }
    
    # Generate sample tweet texts
    sample_texts = [
        f"The issue with {hashtag.strip('#')} is getting worse every day. Someone needs to look into this urgently!",
        f"I'm really happy with the improvements in {hashtag.strip('#')} services recently. Great job!",
        f"Can anyone help with the {hashtag.strip('#')} situation in my neighborhood? It's been days and no resolution.",
        f"The local government needs to address {hashtag.strip('#')} issues immediately. This is unacceptable!",
        f"I've noticed some improvements in {hashtag.strip('#')}, but there's still a long way to go."
    ]
    
    # Generate 3-5 dummy tweets for the hashtag
    num_tweets = random.randint(3, 5)
    tweets = []
    
    for i in range(num_tweets):
        tweet = tweet_template.copy()
        tweet["user"] = tweet_template["user"].copy()  # Create a copy of the user dict
        
        # Set unique values
        tweet["id"] = f"{random.randint(1000000000000000000, 9999999999999999999)}"
        tweet["text"] = sample_texts[i % len(sample_texts)]
        tweet["tagged_hashtags"] = [hashtag.strip('#')]
        
        tweets.append(tweet)
    
    # Save all tweets to scrape.json (append to any existing ones)
    try:
        try:
            with open('scrape.json', 'r') as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []
            
        # Add new tweets
        existing_data.extend(tweets)
        
        # Write back to file
        with open('scrape.json', 'w') as f:
            json.dump(existing_data, f, indent=2)
    except Exception as e:
        print(f"Error saving to scrape.json: {e}")
    
    return tweets

# Updated search route to scrape tweets and store them
@app.post("/search")
def search(request: SearchRequest):
    # Log the request
    timestamp = datetime.now(timezone.utc)
    log_entry = {
        "timestamp": timestamp,
        "event": "Search endpoint accessed",
        "request_body": request.model_dump_json() # Log the request payload
    }
    logs_collection.insert_one(log_entry)

    results_data = []
    result_counter = 0 # Counter for unique IDs

    # Process each hashtag
    for hashtag in request.hashtags:
        # Ensure hashtag starts with # for query, remove if already present
        query_tag = hashtag if hashtag.startswith('#') else '#' + hashtag
        clean_tag = hashtag.strip('#').lower()
        
        # Scrape tweets for this hashtag
        scraped_tweets = scrape_tweets(query_tag)
        
        # Process and store each scraped tweet
        for tweet in scraped_tweets:
            # Parse the created_at timestamp
            tweet_timestamp = parse_twitter_timestamp(tweet["created_at"])
            
            # Store tweet in tweets collection
            tweet_doc = {
                "keyword": clean_tag,
                "tweets": {
                    "timestamp": tweet_timestamp,
                    "text": tweet["text"],
                    "favourite_count": tweet["favorite_count"],
                    "id": tweet["id"],
                    "retweet_count": tweet["retweet_count"],
                    "follower_count": tweet["user"]["followers_count"] if "followers_count" in tweet["user"] else 0,
                    "verified": tweet["user"]["verified"] if "verified" in tweet["user"] else False
                }
            }
            tweets_collection.insert_one(tweet_doc)
            
            # Analyze the tweet
            analysis = analyze_feedback(tweet["text"])
            
            # Format topic scores
            formatted_topic_scores = [
                {"name": topic, "score": round(score * 100)}
                for topic, score in analysis.get('topic_scores', {}).items()
            ]
            
            # Sort topic scores descending
            formatted_topic_scores.sort(key=lambda x: x['score'], reverse=True)
            
            # Store analysis
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
            analysis_collection.insert_one(analysis_doc)
            
            # Check if priority score meets the threshold
            if analysis['priority_score'] >= request.priority_threshold:
                # Format result for response
                result_item = {
                    "id": f"{clean_tag}-{result_counter}",
                    "hashtag": query_tag,
                    "sentiment": analysis['sentiment'],
                    "urgency": analysis['urgency'],
                    "urgency_reason": analysis['urgency_reason'],
                    "topic": analysis['topic'],
                    "topic_scores": formatted_topic_scores,
                    "priority_score": analysis['priority_score'],
                    "timestamp": tweet_timestamp.isoformat()
                }
                results_data.append(result_item)
                result_counter += 1
        
        # Also check for existing analysis in the database
        stored_analysis = list(analysis_collection.find({"keyword": clean_tag}))
        
        for analysis_item in stored_analysis:
            # Check if priority score meets the threshold and not already included
            if analysis_item.get('priority_score', 0) >= request.priority_threshold:
                # Check if we already included this tweet
                tweet_id = analysis_item.get('tweet_id')
                if not any(item['id'].endswith(str(tweet_id)) for item in results_data):
                    result_item = {
                        "id": f"{clean_tag}-stored-{result_counter}",
                        "hashtag": query_tag,
                        "sentiment": analysis_item.get('sentiment'),
                        "urgency": analysis_item.get('urgency'),
                        "urgency_reason": analysis_item.get('urgency_reason'),
                        "topic": analysis_item.get('topic'),
                        "topic_scores": analysis_item.get('topic_scores', []),
                        "priority_score": analysis_item.get('priority_score', 0),
                        "timestamp": analysis_item.get('timestamp', datetime.now(timezone.utc)).isoformat()
                    }
                    results_data.append(result_item)
                    result_counter += 1

    return {"success": True, "data": results_data}

# Route to filter tweets based on priority_threshold
@app.post("/filter")
def filter_tweets(payload: dict):
    priority_threshold = payload.get("priority_threshold")
    if priority_threshold is None:
        return {"success": False, "error": "priority_threshold is required"}

    # Query MongoDB for tweets with priority_score >= priority_threshold
    filtered_tweets = list(tweets_collection.find({"priority_score": {"$gte": priority_threshold}}))

    # Format the results
    results_data = []
    for tweet in filtered_tweets:
        # Assume tweet is a dictionary-like object with necessary fields
        tweet_text = tweet.get("text")
        if not tweet_text:
            continue  # Skip if no text

        # Get timestamp (prefer tweet's timestamp if available)
        tweet_timestamp = tweet.get("timestamp", datetime.now(timezone.utc))
        if isinstance(tweet_timestamp, datetime):
            if tweet_timestamp.tzinfo is None:
                tweet_timestamp = tweet_timestamp.replace(tzinfo=timezone.utc)
            timestamp_str = tweet_timestamp.isoformat()
        else:
            timestamp_str = datetime.now(timezone.utc).isoformat()

        # Format the result
        result_item = {
            "id": tweet.get("_id"),  # Use MongoDB's unique ID
            "text": tweet_text,
            "priority_score": tweet.get("priority_score"),
            "timestamp": timestamp_str,
        }
        results_data.append(result_item)

    return {"success": True, "data": results_data}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

