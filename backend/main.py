from fastapi import FastAPI
# Import CORSMiddleware
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
# Import pymongo and datetime
from pymongo import MongoClient
from datetime import datetime
from dotenv import load_dotenv
import os
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
db = client["sample_mflix"] # Database name
tweets_collection = db["tweets"] # Collection name
logs_collection = db["logs"] # Collection name for logs

# Add dummy search route
@app.post("/search")
def search():
    # Log the timestamp
    timestamp = datetime.now(datetime.timezone.utc)
    log_entry = {"timestamp": timestamp, "event": "Search endpoint accessed"}
    logs_collection.insert_one(log_entry)

    return {"message": "This is the search page.", "timestamp_logged": str(timestamp)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8080)

