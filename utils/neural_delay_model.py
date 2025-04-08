import random

def predict_delay(context=None):
    """
    Simulates a smarter human-like delay.
    Considers time of day, tweet count, and whether we're switching accounts.
    """
    if context is None:
        context = {}

    hour = context.get("time", 12)
    tweet_count = context.get("tweets_scraped", 0)
    is_switch = context.get("is_switch", False)

    # Base delay range
    delay = random.uniform(3, 7)

    # Simulate longer delay during off hours
    if 0 <= hour <= 6:
        delay += random.uniform(3, 6)

    # More delay when switching accounts
    if is_switch:
        delay += random.uniform(10, 20)

    # If tweet count is high, mimic fatigue
    if tweet_count > 100:
        delay += random.uniform(5, 10)

    return round(delay, 2)
