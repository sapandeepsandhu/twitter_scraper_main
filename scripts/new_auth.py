import asyncio
import random
from twikit import Client
from configparser import ConfigParser

async def login_and_save_cookies(section, config):
    # Read credentials from the config for this section
    username = config[section]["username"]
    email = config[section]["email"]
    password = config[section]["password"]

    # Create the Client with SOCKS proxy support via Tor.
    # Ensure that Tor is running on 127.0.0.1:9050.
    client = Client(language="en-US", proxy="socks5://127.0.0.1:9050")
    
    # Optionally, set a realistic User-Agent if supported:
    # client.set_header('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ...')
    
    # Login using your credentials.
    try:
        await client.login(auth_info_1=username, auth_info_2=email, password=password)
    except Exception as e:
        print(f"❌ Login failed for {username}: {e}")
        return

    # Save cookies to a file specific to the username.
    cookie_file = f"cookies_{username.lower()}.json"
    client.save_cookies(cookie_file)
    print(f"✅ Cookies saved to {cookie_file}")

async def main():
    # Load credentials from a config file named 'config.ini'
    config = ConfigParser()
    config.read("config.ini")

    # Instead of running logins concurrently, process each account sequentially
    # and wait between logins to avoid rapid-fire login attempts.
    for section in config.sections():
        await login_and_save_cookies(section, config)
        # Delay between login attempts – add slight randomization to mimic human behavior.
        delay = 60 + random.randint(0, 20)  # 60-80 seconds delay.
        print(f"⏳ Waiting {delay} seconds before the next login attempt...")
        await asyncio.sleep(delay)

if __name__ == "__main__":
    asyncio.run(main())
