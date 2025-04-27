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
from hashtagger import scrape_tweets
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

# Updated search route to scrape tweets and store them
@app.post("/search")
async def search(request: SearchRequest):
    print("Search endpoint accessed")
    # Log the request
    timestamp = datetime.now(timezone.utc)
    log_entry = {
        "timestamp": timestamp,
        "event": "Search endpoint accessed",
        "request_body": request.model_dump_json()  # Log the request payload
    }
    logs_collection.insert_one(log_entry)
    print("Request logged in logs_collection")

    results_data = []
    print("Initialized results_data")

    # Process each hashtag
    for hashtag in request.hashtags:
        print(f"Processing hashtag: {hashtag}")
        try:
            # Scrape tweets for the hashtag
            tweets = await scrape_tweets(hashtag)
            print(f"Scraped {len(tweets)} tweets for hashtag: {hashtag}")

            # Process each tweet
            for tweet in tweets:
                print(f"Processing tweet: {tweet.get('id', 'unknown')}")
                # Extract tweet text
                tweet_text = tweet.get("text", "")
                if not tweet_text:
                    print("Tweet text is empty, skipping")
                    continue

                # Analyze the tweet text
                analysis = analyze_feedback(tweet_text)
                print(f"Analysis result: {analysis}")

                # Create document for MongoDB insertion
                tweet_doc = {
                    "keywords": tweet.get("tagged_hashtags", []),
                    "sentiment": analysis["sentiment"],
                    "urgency": analysis["urgency"],
                    "urgency_reason": analysis["urgency_reason"],
                    "topic": analysis["topic"],
                    "topic_scores": [
                        {"name": topic, "score": score}
                        for topic, score in analysis["topic_scores"].items()
                    ] if isinstance(analysis["topic_scores"], dict) else analysis["topic_scores"],
                    "priority_score": analysis["priority_score"],
                    "timestamp": datetime.strptime(tweet.get("created_at", timestamp.isoformat()),
                                                   "%a %b %d %H:%M:%S %z %Y")
                    if "created_at" in tweet else timestamp,
                    "tweet_id": tweet.get("id", ""),
                    "text": tweet_text  # Store the original tweet text
                }
                print(f"Prepared tweet_doc: {tweet_doc}")

                # Insert into MongoDB
                result = tweets_collection.insert_one(tweet_doc)
                print(f"Inserted tweet into tweets_collection with ID: {result.inserted_id}")

                # Add to results if it meets the priority threshold
                if tweet_doc["priority_score"] >= request.priority_threshold:
                    tweet_doc["_id"] = str(result.inserted_id)
                    results_data.append(tweet_doc)
                    print(f"Tweet added to results_data: {tweet_doc}")

        except Exception as e:
            print(f"Error processing hashtag {hashtag}: {str(e)}")
            # Log the error
            error_log = {
                "timestamp": datetime.now(timezone.utc),
                "event": "Search error",
                "hashtag": hashtag,
                "error": str(e)
            }
            logs_collection.insert_one(error_log)
            print(f"Error logged in logs_collection: {error_log}")

    print("Search completed, returning results")
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

