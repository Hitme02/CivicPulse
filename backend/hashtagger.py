import asyncio
from playwright.async_api import async_playwright
from typing import Dict, List
import jmespath
import random
import time
import urllib.parse
import json
import os

# Parse user info
def parse_user(user_data: Dict) -> Dict:
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

# Parse tweet info
def parse_tweet(data: Dict) -> Dict:
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

# Main search function
async def search_tweets_by_hashtag(hashtag: str, max_tweets: int = 100) -> List[Dict]:
    user_data_dir = "playwright_storage"
    collected_tweets = []
    _xhr_calls = []

    # Encode the hashtag for URL
    encoded_hashtag = urllib.parse.quote(f"#{hashtag}")

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,
            viewport={"width": 1920, "height": 1080},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        )
        page = await browser.new_page()

        await page.goto("https://twitter.com/")
        await asyncio.sleep(5)

        if "login" in page.url:
            print("Not logged in. Please log in manually.")
            await asyncio.sleep(60)  # Give time to manually login
            print("Proceeding after manual login...")

        async def intercept_response(response):
            if response.request.resource_type == "xhr":
                try:
                    if "SearchTimeline" in response.url or "timeline" in response.url.lower():
                        _xhr_calls.append(response)
                except:
                    pass

        page.on("response", intercept_response)

        # Perform search
        search_url = f"https://twitter.com/search?q={encoded_hashtag}&src=typed_query&f=live"
        print(f"Searching for hashtag: {hashtag}")
        await page.goto(search_url)
        await page.wait_for_selector('article', timeout=30000)

        tweet_count = 0
        scroll_attempts = 0
        max_scroll_attempts = 20
        last_height = await page.evaluate("document.body.scrollHeight")

        while tweet_count < max_tweets and scroll_attempts < max_scroll_attempts:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await asyncio.sleep(random.uniform(2, 4))

            for xhr in _xhr_calls:
                try:
                    data = await xhr.json()

                    tweet_entries = jmespath.search("data.search_by_raw_query.search_timeline.timeline.instructions[].entries[]", data)
                    if not tweet_entries:
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

            _xhr_calls.clear()

            new_height = await page.evaluate("document.body.scrollHeight")
            if new_height == last_height:
                scroll_attempts += 1
                print("\nNo more scrolling possible")
            else:
                scroll_attempts = 0

            last_height = new_height

        await browser.close()

    # Remove duplicates
    unique_tweets = {tweet.get("id"): tweet for tweet in collected_tweets if tweet.get("id")}
    return list(unique_tweets.values())

async def scrape_tweets(htag:str):
    social_hashtags = [htag]

    all_tweets_by_hashtag = {}

    for hashtag in social_hashtags:
        try:
            print(f"\nSearching for hashtag: {hashtag}")
            tweets = await search_tweets_by_hashtag(hashtag, max_tweets=30)
            print(f"Found {len(tweets)} tweets for #{hashtag}")

            if tweets:
                all_tweets_by_hashtag[hashtag] = tweets

            delay = random.uniform(5, 10)
            print(f"Waiting {delay:.1f} seconds before next search...")
            await asyncio.sleep(delay)

        except Exception as e:
            print(f"Error processing hashtag {hashtag}: {e}")

    if all_tweets_by_hashtag:
        with open("all_social_issue_tweets.json", "w", encoding="utf-8") as f:
            json.dump(all_tweets_by_hashtag, f, ensure_ascii=False, indent=2)
            return all_tweets_by_hashtag[htag]
        print(f"\nSaved tweets for all hashtags to all_social_issue_tweets.json")
    else:
        print("\nNo tweets were collected.")

if __name__ == "__main__":
    asyncio.run(scrape_tweets())
