import asyncio
import json
import os
from datetime import datetime

from dateparser import parse

from api import CheckInAPI
from discobot import read_channel, send_discord_message
from logger import logger


async def main(result):
    if not os.environ.get("DISCORD_BOT_TOKEN"):
        logger.error("DISCORD_BOT_TOKEN not set in env")
        return 1

    if os.path.isfile('creds.json'):
        with open('creds.json', 'r') as file:
            data = json.load(file)
    else:
        logger.error("Missing creds.json")
        return 1

    leave_user_ids = []
    messages = await read_channel("Apna Server", "leave-request")
    for author, content in messages:
        try:
            if "-" in content:
                start_date, end_date = map(str.strip, content.split("-", 1))
                start_date = parse(start_date.strip(), settings={'FUZZY': True}).date()
                end_date = parse(end_date.strip(), settings={'FUZZY': True}).date()

                if start_date <= datetime.now().date() <= end_date:
                    logger.info(f"Leave for {author.name} {content}")
                    leave_user_ids.append(f"<@{author.id}>")

            else:
                message_date = parse(content.strip(), settings={'FUZZY': True})
                message_date = message_date.date() if message_date else None
                if datetime.now().date() == message_date:
                    logger.info(f"Leave for {author.name}, {content}")
                    leave_user_ids.append(f"<@{author.id}>")
        except ValueError:
            logger.info(f"Skipping message from {author.name}: Unable to parse {content} as a date or range.")

    logger.info(f"Leave user IDs: {leave_user_ids}")
    if not result:
        for user in data:
            userid, creds = next(iter(user.items()))
            result[userid] = "Leave" if user in leave_user_ids else CheckInAPI(*creds).checkin()

    MAX_RETRIES = 3
    retries = 0
    while "Failed" in result.values() and retries < MAX_RETRIES:
        logger.info(f"Retrying failed jobs (Attempt {retries + 1}/{MAX_RETRIES})")
        for user in data:
            userid, creds = next(iter(user.items()))
            if result[userid] == "Failed":
                result[userid] = CheckInAPI(*creds).checkin()
        retries += 1

    if "Failed" in result.values():
        logger.error("Some jobs failed after maximum retries.")

    send_discord_message(json.dumps(result, indent=4).replace('"', ''))
    logger.info(f"All jobs completed successfully {json.dumps(result, indent=4)}")

if __name__ == "__main__":
    asyncio.run(main({}))
