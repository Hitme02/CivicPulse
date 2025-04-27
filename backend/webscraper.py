import json
import logging
import os
from ntscraper import Nitter

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
# It's highly recommended to use environment variables or a secure config file
# for credentials instead of hardcoding them.
TWITTER_EMAIL = os.environ.get("TWITTER_EMAIL", "your_email@example.com")
TWITTER_USERNAME = os.environ.get("TWITTER_USERNAME", "your_username")
TWITTER_PASSWORD = os.environ.get("TWITTER_PASSWORD", "your_password")
# Cookie file to store session information (ntscraper handles this internally after login)
# While ntscraper manages the session, explicitly defining a cookie file path
# isn't part of its standard login flow. Login establishes the session.
# COOKIE_FILE = "twitter_session.json" # ntscraper doesn't directly use this file path for login persistence across runs.

SEARCH_TERMS = ["#python", "webscraping", "AI"]
MAX_TWEETS_PER_TERM = 50
OUTPUT_FILE = "scraped_tweets.json"

# --- Main Scraping Logic ---
def scrape_tweets(scraper, terms, max_tweets):
    """Scrapes tweets for given terms using the logged-in scraper."""
    all_tweets = {}
    for term in terms:
        logger.info(f"Scraping tweets for term: {term}")
        try:
            # Scrape tweets using search function
            result = scraper.get_tweets(term, mode='term', number=max_tweets)
            if result and 'tweets' in result:
                 # Filter out potential None values if any tweet fetching failed partially
                valid_tweets = [tweet for tweet in result['tweets'] if tweet]
                all_tweets[term] = valid_tweets
                logger.info(f"Found {len(valid_tweets)} tweets for '{term}'.")
            else:
                logger.warning(f"No tweets found or error fetching for term: {term}. Result: {result}")
                all_tweets[term] = []

        except Exception as e:
            logger.error(f"Error scraping term '{term}': {e}", exc_info=True)
            all_tweets[term] = []
    return all_tweets

def save_tweets(tweets, filename):
    """Saves the scraped tweets to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tweets, f, ensure_ascii=False, indent=4)
        logger.info(f"Successfully saved tweets to {filename}")
    except IOError as e:
        logger.error(f"Error saving tweets to {filename}: {e}")

def main():
    """Main function to handle login and scraping."""
    scraper = Nitter()

    # Login to Twitter - ntscraper handles the session internally
    # It uses the provided credentials to establish a session for scraping.
    # This session is typically maintained for the lifetime of the scraper object.
    # Persisting the session *between script runs* without re-login might
    # require more complex browser automation (like Selenium) if ntscraper
    # doesn't support loading session state from a file directly.
    try:
        logger.info("Attempting to log in...")
        # Note: ntscraper's login might be fragile due to Twitter changes.
        # Ensure you have the latest version of ntscraper.
        # As of recent versions, login might require email, username, AND password.
        login_success = scraper.login(email=TWITTER_EMAIL, username=TWITTER_USERNAME, password=TWITTER_PASSWORD)
        if not login_success:
             logger.error("Login failed. Please check credentials and ensure 2FA is handled if enabled.")
             # Depending on ntscraper's implementation, it might still allow
             # scraping without login, but results could be limited/different.
             # You might want to exit if login is strictly required.
             # return # Optional: exit if login fails
        else:
            logger.info("Login successful.")

    except Exception as e:
        logger.error(f"An error occurred during login: {e}", exc_info=True)
        # Decide if you want to proceed without login or exit
        # return # Optional: exit if login fails

    # Scrape tweets
    scraped_data = scrape_tweets(scraper, SEARCH_TERMS, MAX_TWEETS_PER_TERM)

    # Save results
    if scraped_data:
        save_tweets(scraped_data, OUTPUT_FILE)
    else:
        logger.info("No data was scraped.")

if __name__ == "__main__":
    # Basic check for placeholder credentials
    if "your_email@example.com" in TWITTER_EMAIL or \
       "your_username" in TWITTER_USERNAME or \
       "your_password" in TWITTER_PASSWORD:
        logger.warning("Using placeholder credentials. Please update configuration.")

    main()