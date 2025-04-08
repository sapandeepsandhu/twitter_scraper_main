import yaml
import asyncio
from scraper import scrape_user

def load_settings():
    with open('settings.yaml', 'r') as f:
        return yaml.safe_load(f)

async def main():
    settings = load_settings()
    tasks = []

    for q in settings['query_list']:
        tasks.append(
            scrape_user(
                handle=q['handle'],
                since=q['since'],
                until=q['until'],
                lang=settings['lang'],
                min_tweets=settings['min_tweets']
            )
        )

    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
