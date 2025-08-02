import aiohttp
import asyncio
from itertools import islice
import json
import os 
import shutil

from parse_module.parse_wb_site_class import ParseWbSiteClass

from constants import ARTICLES_WB

async def main():
    SEMAPHORE = asyncio.Semaphore(100)  # можно поставить 20 или 50
    parser = ParseWbSiteClass(SEMAPHORE)
    feedbacks = {}
    tasks = []
    async with aiohttp.ClientSession() as session:
        for i in range(len(ARTICLES_WB)):
            tasks.append(parser.parse_last_five_feedbacks_rating_nm_id(session, ARTICLES_WB[i], feedbacks))
        await asyncio.gather(*tasks)

        with open(
            f".data/result_answer_parsing_feedbacks.json", "w", encoding="utf-8"
        ) as f:
            json.dump(feedbacks, f, indent=4, ensure_ascii=False)
        return None
if __name__ == "__main__":
    shutil.rmtree(".data")
    os.makedirs(".data", exist_ok=True)
    asyncio.run(main())