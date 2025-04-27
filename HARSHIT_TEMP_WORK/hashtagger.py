from playwright.sync_api import sync_playwright
from typing import Dict, List, Tuple
import jmespath
import time
import json
import random
import urllib.parse
import os


# Define multiple accounts
ACCOUNTS = [
    {"username": "HarshitrajCs23", "password": "HR05@xrvce"},
    {"username": "chaarpatti", "password": "chaarpattinallesaale"}
]

def login_to_twitter(page, account: Dict[str, str]) -> bool:
    """
    Automate login to Twitter using the provided account credentials.
    Returns True if login is successful, False otherwise.
    """
    try:
        print("Attempting to log in...")
        page.goto("https://twitter.com/login")
        page.wait_for_selector("input[name='text']", timeout=10000)
        
        # Enter username
        page.fill("input[name='text']", account["username"])
        page.click("div[data-testid='LoginForm_Login_Button']")
        page.wait_for_selector("input[name='password']", timeout=10000)
        
        # Enter password
        page.fill("input[name='password']", account["password"])
        page.click("div[data-testid='LoginForm_Login_Button']")
        
        # Wait for successful login (e.g., check for home page or profile icon)
        page.wait_for_selector("div[data-testid='SideNav_AccountSwitcher_Button']", timeout=15000)
        print("Login successful!")
        return True
    except Exception as e:
        print(f"Login failed: {e}")
        return False
    

def parse_user(user_data: Dict) -> Dict:
    """Parse user-related information from the JSON data."""
    if not user_data:
        return {}
    return {
        "id": user_data.get("id_str"),
        "name": user_data.get("name"),
        "screen_name": user_data.get("screen_name"),
        "description": user_data.get("description"),
        "followers_count": user_data.get("followers_count"),
        "friends_count": user_data.get("friends_count"),
        "statuses_count": user_data.get("statuses_count"),
        "verified": user_data.get("verified"),
        "profile_image_url": user_data.get("profile_image_url_https"),
    }

def parse_tweet(data: Dict) -> Dict:
    """Parse Twitter tweet JSON dataset for the most important fields"""
    if not data:
        return {}
        
    result = jmespath.search(
    """{
        created_at: legacy.created_at,
        attached_urls: legacy.entities.urls[].expanded_url,
        attached_media: legacy.entities.media[].media_url_https,
        tagged_users: legacy.entities.user_mentions[].screen_name,
        tagged_hashtags: legacy.entities.hashtags[].text,
        favorite_count: legacy.favorite_count,
        reply_count: legacy.reply_count,
        retweet_count: legacy.retweet_count,
        text: legacy.full_text,
        language: legacy.lang,
        user_id: legacy.user_id_str,
        id: legacy.id_str,
        conversation_id: legacy.conversation_id_str,
        views: views.count
    }""",
        data,
    )
    
    if not result:
        return {}
    
    user_data = jmespath.search("core.user_results.result.legacy", data)
    if user_data:
        result["user"] = parse_user(user_data)
    return result

def search_tweets_by_hashtag(hashtag: str, max_tweets: int = 100) -> List[Dict]:
    """
    Search Twitter for tweets containing specific hashtags related to social issues
    hashtag: Hashtag to search for (without the # symbol)
    max_tweets: Maximum number of tweets to collect
    """
    _xhr_calls = []
    collected_tweets = []
    
    # Encode the hashtag for URL
    encoded_hashtag = urllib.parse.quote(f"#{hashtag}")

    def intercept_response(response):
        """capture all background requests and save them"""
        if response.request.resource_type == "xhr":
            try:
                # Capture search and timeline XHR calls
                if "SearchTimeline" in response.url or "timeline" in response.url.lower():
                    _xhr_calls.append(response)
            except:
                pass
        return response

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        context = browser.new_context(
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = context.new_page()

        # Select a random account to log in
        random_account = random.choice(ACCOUNTS)
        if not login_to_twitter(page, random_account):
            print("Login attempt failed with the selected random account. Exiting...")
            return []

        # Enable background request intercepting
        page.on("response", intercept_response)
        
        # Use advanced search with hashtag
        search_url = f"https://twitter.com/search?q={encoded_hashtag}&src=typed_query&f=live"
        print(f"Searching for hashtag: {hashtag}")
        print(f"URL: {search_url}")
        
        page.goto(search_url)
        page.wait_for_load_state("networkidle", timeout=30000)
        
        # Check if tweets are available
        tweet_elements = page.query_selector_all("[data-testid='tweet']")
        print(f"Found {len(tweet_elements)} tweets on the initial page")
        
        if not tweet_elements:
            print("No tweets found. Checking for login wall...")
            if page.query_selector("text=Sign in to X") or page.query_selector("text=Log in"):
                print("Login wall detected. Trying to bypass...")
                try:
                    close_button = page.query_selector("text=Not now")
                    if close_button:
                        close_button.click()
                        time.sleep(2)
                except:
                    print("Couldn't bypass login wall")
        
        # Re-check tweets on the page after potential login wall handling
        tweet_elements = page.query_selector_all("[data-testid='tweet']")
        print(f"Now found {len(tweet_elements)} tweets on the page")
        
        # Scroll to load more tweets
        last_height = page.evaluate("document.body.scrollHeight")
        tweet_count = 0
        scroll_attempts = 0
        max_scroll_attempts = 20
        
        while tweet_count < max_tweets and scroll_attempts < max_scroll_attempts:
            # Scroll down
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(random.uniform(2, 4))  # Reasonable delay
            
            # Process collected XHR calls
            for xhr in _xhr_calls:
                try:
                    data = xhr.json()
                    
                    # Try different JSON paths to find tweet data
                    tweet_entries = jmespath.search("data.search_by_raw_query.search_timeline.timeline.instructions[].entries[]", data)
                    
                    if not tweet_entries:
                        # Try alternative paths
                        tweet_entries = jmespath.search("data.threaded_conversation_with_injections_v2.instructions[].entries[]", data)
                    
                    if not tweet_entries:
                        continue
                        
                    for entry in tweet_entries:
                        if not entry.get("entryId", ""):
                            continue
                            
                        if "tweet" in entry.get("entryId", ""):
                            tweet_data = jmespath.search("content.itemContent.tweet_results.result", entry)
                            if not tweet_data:
                                continue
                                
                            parsed_tweet = parse_tweet(tweet_data)
                            if parsed_tweet and "text" in parsed_tweet:
                                collected_tweets.append(parsed_tweet)
                                tweet_count += 1
                                print(f"Collected {tweet_count} tweets", end="\r")
                                
                                if tweet_count >= max_tweets:
                                    break
                except Exception as e:
                    print(f"Error processing XHR: {e}")
                    
            _xhr_calls = []  # Clear processed calls
            
            # Check if we've reached the bottom of the page
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                print("\nNo more scrolling possible")
                scroll_attempts += 1
            else:
                scroll_attempts = 0  # Reset if we actually scrolled
                
            last_height = new_height
                
        browser.close()
    
    # If we didn't collect any tweets from XHR, try extracting directly from the page
    if not collected_tweets:
        print("No tweets collected from XHR. Consider a different approach.")
        
    # Remove duplicates based on tweet ID
    unique_tweets = {tweet.get("id"): tweet for tweet in collected_tweets if tweet.get("id")}
    return list(unique_tweets.values())

if __name__ == "__main__":
    # Define social issue hashtags to search for
    # social_hashtags = [
    #     "PublicService",
    #     "GovFeedback",
    #     "PublicTransport",
    #     "HealthcareReform",
    #     "EducationSystem",
    #     "SocialSecurity",
    #     "CommunityServices",
    #     "Infrastructure",
    #     "PublicPolicy",
    #     "CitizenRights",
    #     "GovServices",
    #     "CivicEngagement"
    # ]

    social_hashtags = [
        "pahalgam",
        "indiangovernment"
    ]
    
    all_tweets_by_hashtag = {}

    # Search for each hashtag separately
    for hashtag in social_hashtags:
        try:
            print(f"\nSearching for hashtag: {hashtag}")
            tweets = search_tweets_by_hashtag(hashtag, max_tweets=30)
            
            print(f"Found {len(tweets)} tweets for #{hashtag}")
            
            if tweets:
                # Store tweets in the dictionary under the hashtag key
                all_tweets_by_hashtag[hashtag] = tweets
            
            # Wait between searches to avoid rate limiting
            delay = random.uniform(5, 10)
            print(f"Waiting {delay:.1f} seconds before next search...")
            time.sleep(delay)
            
        except Exception as e:
            print(f"Error processing hashtag {hashtag}: {e}")
    
    # Save all tweets grouped by hashtags to a single JSON file
    if all_tweets_by_hashtag:
        with open("all_social_issue_tweets.json", "w", encoding="utf-8") as f:
            json.dump(all_tweets_by_hashtag, f, ensure_ascii=False, indent=2)
        print(f"\nSaved tweets for all hashtags to all_social_issue_tweets.json")
    else:
        print("\nNo tweets were collected.")