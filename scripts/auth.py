import asyncio
from twikit import Client
from configparser import ConfigParser

async def login_and_save_cookies(section, config):
    username = config[section]["username"]
    email = config[section]["email"]
    password = config[section]["password"]

    client = Client(language="en-US")
    await client.login(auth_info_1=username, auth_info_2=email, password=password)
    cookie_file = f"cookies_{username.lower()}.json"
    client.save_cookies(cookie_file)
    print(f"✅ Cookies saved to {cookie_file}")

async def main():
    config = ConfigParser()
    config.read("config.ini")

    tasks = [login_and_save_cookies(section, config) for section in config.sections()]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
