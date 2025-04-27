from pymongo import MongoClient
from dotenv import load_dotenv
import os
load_dotenv()

if __name__ == "__main__":
    # Replace with your MongoDB connection details
    MONGO_URI = f"mongodb+srv://admin:{os.getenv('PASSWORD')}@civicpulse.cwyk8qt.mongodb.net/?retryWrites=true&w=majority&appName=civicpulse"
    client = MongoClient(MONGO_URI)
    db = client["sample_mflix"]  # Replace with your database name
    