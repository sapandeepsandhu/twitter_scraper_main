import csv
import time
import yaml
import asyncio
from datetime import datetime
from twikit import Client, TooManyRequests
import sys
import os
import logging
from tqdm.asyncio import tqdm_asyncio

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from utils.neural_delay_model import predict_delay
from utils.relevance_classifier import is_relevant

# ✅ Setup logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
logging.basicConfig(
    filename=os.path.join(log_dir, "scraper_errors.log"),
    level=logging.ERROR,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

success_log_file = os.path.join(log_dir, "scraper_success.log")

def log_success(message):
    with open(success_log_file, "a") as f:
        f.write(f"{datetime.now()} - {message}\n")

# ✅ Load settings.yaml
with open("settings.yaml", "r") as f:
    config = yaml.safe_load(f)

# ✅ Load progress if any
progress_file = "scrape_progress.txt"
last_scraped_index = 0
if os.path.exists(progress_file):
    with open(progress_file, "r") as pf:
        last_scraped_index = int(pf.read().strip())

# ✅ Cookie rotation setup
cookie_files = [
    "cookies/cookie1.json",
]

# ✅ Scraping logic
async def scrape():
    total_handles = len(config["query_list"])
    cookie_index = 0

    for i in tqdm_asyncio(range(last_scraped_index, total_handles), desc="Scraping Progress"):
        handle = config["query_list"][i]["handle"]
        print(f"\n📦 Scraping @{handle} with account {cookie_files[cookie_index]}...")

        client = Client(language="en-US")
        client.load_cookies(cookie_files[cookie_index])

        try:
            user = await client.get_user_by_screen_name(handle)
            tweets = await user.get_tweets(tweet_type="Tweets")
            tweet_count = 0
            filename = f"data/tweets_{handle}.csv"
            empty_cycles = 0

            with open(filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Username", "Created At", "Text", "Likes", "Retweets"])

            while tweet_count < config["min_tweets"]:
                batch_collected = 0
                for tweet in tweets:
                    if not is_relevant(tweet.text):
                        continue
                    tweet_count += 1
                    batch_collected += 1
                    tweet_data = [handle, tweet.created_at, tweet.text, tweet.favorite_count, tweet.retweet_count]
                    with open(filename, "a", newline="", encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerow(tweet_data)

                if batch_collected == 0:
                    empty_cycles += 1
                else:
                    empty_cycles = 0

                if empty_cycles >= 2:
                    print(f"⚠️ No tweets for @{handle} after 5 tries. Skipping.")
                    break

                print(f"{datetime.now()} - {handle}: {tweet_count} tweets collected.")
                delay = predict_delay({
                    "time": datetime.now().hour,
                    "tweets_scraped": tweet_count,
                    "is_switch": False
                })
                print(f"⏳ Sleeping {delay}s to mimic human behavior...")
                await asyncio.sleep(delay)
                tweets = await tweets.next()

            with open(progress_file, "w") as pf:
                pf.write(str(i + 1))

            log_success(f"✅ @{handle} scraped successfully with {tweet_count} tweets.")

        except TooManyRequests as e:
            print(f"🚫 Rate limit hit. Sleeping until {e.rate_limit_reset}")
            from datetime import datetime as dt
            reset_time = dt.fromtimestamp(e.rate_limit_reset)
            wait_time = (reset_time - dt.now()).total_seconds()
            wait_time = max(wait_time, 60)
            print(f"🕒 Waiting {wait_time:.2f} seconds due to rate limit...")
            await asyncio.sleep(wait_time)

        except Exception as ex:
            logging.error(f"Error scraping @{handle}: {ex}")
            print(f"❌ Error scraping {handle}: {ex}")

        # ✅ Rotate account every 5 users or manually
        if (i + 1) % 5 == 0:
            cookie_index = (cookie_index + 1) % len(cookie_files)
            print(f"🔄 Rotating account to: {cookie_files[cookie_index]}")
            await asyncio.sleep(predict_delay({"is_switch": True}))

# ✅ CSV Merging logic

def merge_all_tweet_csvs():
    import glob
    import pandas as pd

    all_files = glob.glob("data/tweets_*.csv")
    if not all_files:
        print("⚠️ No tweet CSVs found to merge.")
        return

    df_list = [pd.read_csv(f) for f in all_files]
    combined = pd.concat(df_list, ignore_index=True)
    combined.to_csv("data/all_tweets_combined.csv", index=False)
    print(f"✅ Merged {len(df_list)} files into data/all_tweets_combined.csv")

# ✅ Entry point
if __name__ == "__main__":
    asyncio.run(scrape())
    merge_all_tweet_csvs()