import asyncio
import aiohttp
import json
import logging
import re

from bs4 import BeautifulSoup as bs
import praw

from settings import AMPL_TELEGRAM_DICT

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

MEMBER_COUNT_REGEX = r"[0-9\s]+"
AMPLE_SUBREDDIT = "AmpleforthCrypto"

with open("./secrets.json") as f:
    secrets = json.load(f)
    
REDDIT = secrets['reddit']

class Collector:
    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=REDDIT["client_id"],
            client_secret=REDDIT["client_secret"],
            password=REDDIT["password"],
            username=REDDIT["username"],
            user_agent=REDDIT["user_agent"],
        )
        self.session = None

    async def _get_session(self):
        if self.session is None:
            self.session = aiohttp.ClientSession()
        
    async def get_telegram_members(self):
        logger.info("Getting telegram subs")
        # ensure session
        await self._get_session()

        async with self.session.get("https://t.me/Ampleforth") as response:
            text = await response.text()

        # if response.ok:
        #     soup = bs(response.text, 'html.parser')
        # else:
        #     print(response.text)
        #     raise Exception("Bad response")

        soup = bs(text, 'html.parser')

        element = soup.find('div', class_='tgme_page_extra')
        member_count_total, member_count_online = element.text.split(",")
        find_member_count_total = re.findall(MEMBER_COUNT_REGEX, member_count_total)[0]
        find_member_count_online = re.findall(MEMBER_COUNT_REGEX, member_count_online)[0]
        parsed_member_count_total = int(find_member_count_total.replace(' ', ''))
        parsed_member_count_online = int(find_member_count_online.replace(' ', ''))

        # print(parsed_member_count_total, parsed_member_count_online)
        return (parsed_member_count_total, parsed_member_count_online)

    async def get_subreddit_subscribers(self):
        logger.info("Getting subreddit subs")
        subreddit = self.reddit.subreddit(AMPLE_SUBREDDIT)
        return subreddit.subscribers

    
    async def _validate_response(self, response):
        text = await response.text()

        if response.status != 200:
            self.logger.warning("Bad response")
            self.logger.warning(f"Status: {response.status}")
            self.logger.warning(f"Reason: {response.reason}")
            self.logger.warning(f"URL: {response.url}")
            self.logger.warning(f"Response: {text}")
            return self._get_error_response(response, text)

        return self._get_ok_response(response, text)

    def _get_ok_response(self, response, text):
        return {
            "ok": True,
            "data": json.loads(text) if text else ""
        }

    def _get_error_response(self, response, text=""):
        return {
            "ok": False,
            "error": {
                "status": response.status,
                "reason": response.reason,
                "url": response.url,
                "text": text,
            }
        }

if __name__ == "__main__":
    c = Collector()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(c.get_telegram_members())