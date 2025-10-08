import csv
import time
import requests
import os
import csv

from dotenv import load_dotenv


def fetch_page(BASE_URL: str, HEADERS: dict, limit=1000, offset=0):
    params = {"limit": limit, "offset": offset}
    resp = requests.get(BASE_URL, headers=HEADERS, params=params, timeout=30)
    return resp

def get_all_articles(BASE_URL: str, HEADERS: dict):
    all_items = []
    limit = 1000
    offset = 0
    backoff = 1.0

    while True:
        try:
            resp = fetch_page(BASE_URL, HEADERS, limit=limit, offset=offset)
        except requests.RequestException as e:
            print("Network error:", e, "— повтор через", backoff, "c")
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)
            continue

        if resp.status_code == 200:
            backoff = 1.0
            data = resp.json()
            # структура: data["data"]["listGoods"] (см. документацию)
            goods = data.get("data", {}).get("listGoods") or []
            if not goods:
                break

            for g in goods:
                nmID = g.get("nmID")
                vendorCode = g.get("vendorCode")  # это артикул продавца
                all_items.append({"nmID": nmID, "vendorCode": vendorCode})
            offset += limit
            # небольшой sleep чтобы не попасть в лимит
            time.sleep(0.15)
        elif resp.status_code == 429:
            # слишком много запросов — exponential backoff
            print("429 Too Many Requests — делаем backoff", backoff, "c")
            time.sleep(backoff)
            backoff = min(backoff * 2, 30)
        elif resp.status_code in (401, 403):
            raise SystemExit(f"Ошибка авторизации (HTTP {resp.status_code}). Проверьте токен и права.")
        else:
            raise SystemExit(f"HTTP {resp.status_code}: {resp.text}")

    return all_items

if __name__ == "__main__":
    load_dotenv()
    TOKEN = os.getenv("WB_TOKEN")

    # discounts-prices-api (возвращает listGoods с nmID и vendorCode)
    BASE_URL = "https://discounts-prices-api.wildberries.ru/api/v2/list/goods/filter"
    HEADERS = {
        "Authorization": TOKEN,
        "Content-Type": "application/json"
    }
    items = get_all_articles(BASE_URL, HEADERS)
    
    print(f"Найдено записей: {len(items)}")
    with open("wb_articles.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["nmID", "vendorCode"])
        writer.writeheader()
        writer.writerows(items)
    print("Сохранено в wb_articles.csv")