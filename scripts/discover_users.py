import asyncio
import yaml
import os
import json
from playwright.async_api import async_playwright
from dotenv import load_dotenv

# === Load environment ===
load_dotenv()

# === Config ===
COOKIES_FILE = "cookies_*******.json"
SETTINGS_FILE = "settings.yaml"
DEFAULT_SINCE = "2023-01-01"
DEFAULT_UNTIL = "2025-01-01"
SEARCH_TERMS = ["comedians", "influencers", "tech founders"]
MAX_HANDLES_PER_TERM = 20

# === Load existing settings ===
def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"query_list": []}
    with open(SETTINGS_FILE, "r") as f:
        data = yaml.safe_load(f) or {}
        # Ensure query_list is always a list
        if "query_list" not in data or data["query_list"] is None:
            data["query_list"] = []
        return data

def save_settings(data):
    with open(SETTINGS_FILE, "w") as f:
        yaml.dump(data, f, sort_keys=False)

def get_existing_handles(settings):
    return set(q["handle"].lower() for q in settings["query_list"])

# === Scrape handles from Twitter Search (People tab) ===
async def extract_handles_from_search(term):
    print(f"🔍 Searching: {term}")
    handles = set()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # ✅ Load cookies
        if os.path.exists(COOKIES_FILE):
            with open(COOKIES_FILE, "r") as f:
                cookies = json.load(f)
            if not isinstance(cookies, list):
                cookies = [cookies]
            # Filter out any cookies that don't have a valid 'name'
            cookies = [cookie for cookie in cookies if cookie.get("name")]
            if not cookies:
                print("⚠️ No valid cookies found in the file!")
            else:
                await context.add_cookies(cookies)

        page = await context.new_page()

        # Go to Twitter search with People filter
        search_url = f"https://twitter.com/search?q={term}&src=typed_query&f=user"
        await page.goto(search_url)
        await page.wait_for_timeout(5000)

        # Get handle texts
        elements = await page.query_selector_all('div[dir="ltr"] > span')
        for el in elements:
            try:
                text = await el.inner_text()
                if text.startswith("@"):
                    handle = text[1:].strip()
                    handles.add(handle)
                    if len(handles) >= MAX_HANDLES_PER_TERM:
                        break
            except Exception:
                continue

        await browser.close()

    print(f"✅ Found {len(handles)} handles for '{term}'")
    return list(handles)

# === Main ===
async def main():
    settings = load_settings()
    existing = get_existing_handles(settings)
    new_entries = []

    for term in SEARCH_TERMS:
        found = await extract_handles_from_search(term)
        for handle in found:
            if handle.lower() not in existing:
                new_entries.append({
                    "handle": handle,
                    "since": DEFAULT_SINCE,
                    "until": DEFAULT_UNTIL
                })
                existing.add(handle.lower())

    settings["query_list"].extend(new_entries)
    save_settings(settings)

    print(f"\n✅ Added {len(new_entries)} new handles to {SETTINGS_FILE}.")
    if new_entries:
        print("📝 Newly added handles:")
        for entry in new_entries:
            print(f" - @{entry['handle']}")

if __name__ == "__main__":
    asyncio.run(main())
