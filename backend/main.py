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
client = MongoClient(f"mongodb+srv://admin:{os.getenv('PASSWORD')}@civicpulse.cwyk8qt.mongodb.net/?retryWrites=true&w=majority&appName=civicpulse") # Replace with your MongoDB connection string if needed
db = client["sample_mflix"] # Database name - TODO: Consider renaming db if not using sample_mflix
tweets_collection = db["tweets"] # Collection name - TODO: Ensure this collection exists and has tweet data
logs_collection = db["logs"] # Collection name for logs
analysis_collection = db["analysis"] # Collection for analysis results

# Define the request body model
class SearchRequest(BaseModel):
    hashtags: List[str]
    priority_threshold: int
        
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
        
        # Query the analysis collection for documents where the 'keywords' array contains the clean_tag
        analysis_results = list(analysis_collection.find({"keywords": clean_tag}))

        print(analysis_results) # Debugging line to check the analysis results
    # Process each found analysis document
        for analysis_item in analysis_results:
            # Check if priority score meets the threshold
            if analysis_item.get('priority_score', 0) >= request.priority_threshold:
            # Ensure timestamp is timezone-aware and format it
                analysis_timestamp = analysis_item.get('timestamp', datetime.now(timezone.utc))
                if isinstance(analysis_timestamp, datetime):
                    if analysis_timestamp.tzinfo is None:
                        analysis_timestamp = analysis_timestamp.replace(tzinfo=timezone.utc)
                timestamp_str = analysis_timestamp.isoformat()
            else:
                # Handle cases where timestamp might not be a datetime object (fallback)
                timestamp_str = datetime.now(timezone.utc).isoformat()

            # Format result for response
            result_item = {
                "id": f"{clean_tag}-{result_counter}", # Use counter for unique ID in response
                "hashtag": query_tag,
                "sentiment": analysis_item.get('sentiment'),
                "urgency": analysis_item.get('urgency'),
                "urgency_reason": analysis_item.get('urgency_reason'),
                "topic": analysis_item.get('topic'),
                "topic_scores": analysis_item.get('topic_scores', []), # Use existing scores
                "priority_score": analysis_item.get('priority_score', 0),
                "timestamp": timestamp_str
            # "tweet_id": analysis_item.get('tweet_id') # Optionally include tweet_id if needed
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
    # Use string "main:app" and add reload=True for auto-reloading on code changes
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)

