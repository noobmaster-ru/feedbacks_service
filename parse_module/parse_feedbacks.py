import aiohttp
import json

class ParseFeedbacks:

    @staticmethod
    async def parse_last_five_feedbacks_rating_nm_id(
        session: aiohttp.ClientSession, nm_id: int, feedbacks: dict
    ) -> dict:
        try:
            headers = {
                'accept': '*/*',
                'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                'authorization': 'Bearer eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpYXQiOjE3NTM5NzMwODcsInVzZXIiOiI1NDU3MDMyNiIsInNoYXJkX2tleSI6IjEzIiwiY2xpZW50X2lkIjoid2IiLCJzZXNzaW9uX2lkIjoiM2Y0MmQ1YTY5MDJiNDhlNjgyYjQwYmE0NDNkOTMwMmMiLCJ2YWxpZGF0aW9uX2tleSI6IjQzZTQxMWM1ZDExODBjZWMzMzFhZGU3Y2ZiNmM1ODM2NzFkYTE0Nzg3ZGYyNWVmNjk3ZjQ0MzU0ODgwOTFlMDEiLCJwaG9uZSI6ImlGenNjbHNSSW5IYWJtSEhuM2JoVGc9PSIsInVzZXJfcmVnaXN0cmF0aW9uX2R0IjoxNjc1MjA3MjY5LCJ2ZXJzaW9uIjoyfQ.SRmdcZ5qf3lS5j7hTP3EHNpYCA0yQ9XFzdXbhtCmexDkJfs6JBLf8B1ymK9p4RhN4l8HarqsRCDyC1grlCgbXE3n-Fs6xFUv1MS4Bwoe4DSdJzKMXrWkysgolBeTYxNCwdF_FYlUOoxtFWpPQowNEcDkiJAJxUSycU83zumYoU0JbnClP6vGG0jq6ExlPeVUXiquT0GIjTUlgfaJpxdoAM8N6df011Jn3q6nmwsLaGikc3QFik-bopMDz8gcVxmKJo-01lsBJO7GgTgnkCvE-K6vXqsRmleCB4k6u70knq79VrbmRjOCghGnVdgxkJdk9EB55X-qWcZxqVI_vPM4mQ',
                'origin': 'https://www.wildberries.ru',
                'priority': 'u=1, i',
                'referer': f'https://www.wildberries.ru/catalog/0/search.aspx?search={nm_id}',
                'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'sec-fetch-dest': 'empty',
                'sec-fetch-mode': 'cors',
                'sec-fetch-site': 'cross-site',
                'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36',
                'x-pow': '',
            }

            params = {
                'appType': '1',
                'curr': 'rub',
                'dest': '-446115',
                'spp': '30',
                'ab_testing': 'false',
                'lang': 'ru',
                'nm': str(nm_id),
                'ignore_stocks': 'true',
            }

            async with session.get("https://card.wb.ru/cards/v4/list",params=params,headers=headers) as response:
                print(f"{nm_id},card_resp status = ",response.status)
                data = await response.json()
                root = data["products"][0]["root"]
                print(root, nm_id)
                headers = {
                    'accept': '*/*',
                    'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                    'origin': 'https://www.wildberries.ru',
                    'priority': 'u=1, i',
                    'referer': f'https://www.wildberries.ru/catalog/{nm_id}/detail.aspx',
                    'sec-ch-ua': '"Not)A;Brand";v="8", "Chromium";v="138", "Google Chrome";v="138"',
                    'sec-ch-ua-mobile': '?1',
                    'sec-ch-ua-platform': '"Android"',
                    'sec-fetch-dest': 'empty',
                    'sec-fetch-mode': 'cors',
                    'sec-fetch-site': 'cross-site',
                    'user-agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Mobile Safari/537.36',
                }
                async with session.get(f"https://feedbacks2.wb.ru/feedbacks/v2/{str(root)}", headers=headers) as resp:
                    print(f"{nm_id},feedback_resp status = ",resp.status)
                    data = await resp.json()
                    try:
                        feedbacks_list = data.get("feedbacks",[])
                    except Exception as e:
                        print("error in data.get('feedbacks',[])")

                    print(len(feedbacks_list))
                    summa_feedbacks_rating = 0
                    count = 0
                    pros_list = []
                    cons_list = []
                    text_list = []
                    with open(f".data/feedbacks_{nm_id}.json", "w", encoding="utf-8") as f:
                        json.dump(feedbacks_list, f, indent=4, ensure_ascii=False)
                    for index, feedback in enumerate(feedbacks_list):
                        productValuation = feedback.get("productValuation")
                        feedback_nm_id = feedback["nmId"]
                        if (str(feedback_nm_id) == str(nm_id) and count < 5):
                            pros_list.append([feedback["pros"], feedback["createdDate"]])
                            cons_list.append([feedback["cons"], feedback["createdDate"]])
                            text_list.append([feedback["text"], feedback["createdDate"]])
                            video = feedback.get["video"]
                            if any([feedback["pros"],feedback["cons"],feedback["text"],video]):
                                summa_feedbacks_rating += productValuation
                                count += 1
                                if count == 5:
                                    summa_feedbacks_rating = summa_feedbacks_rating/5
                                    break
                    feedbacks[nm_id] = {
                        "nm_id": nm_id,
                        "last_five_feedback_rating": summa_feedbacks_rating,
                        "advantages": pros_list,
                        "disadvantages": cons_list,
                        "texts": text_list
                    }               
        except Exception as e:
            print(f"Error in parse_last_five_feedbacks {nm_id}: {e}")
            feedbacks[nm_id] = {
                "nm_id": nm_id,
                "last_five_feedback_rating": "Error in parse_last_five_feedbacks_rating_nm_id",
                "Error": str(e)
            }