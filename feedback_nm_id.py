import time
import requests
import json
import datetime 
import os 
import pandas as pd

from dotenv import load_dotenv

from services.get_list_of_feedbacks import get_list_of_feedbacks


def get_last_feedbacks(nm_id: int, HEADERS: dict, URL_FEEDBACK_LIST: str, NUMBER_OF_FEEDBACKS_NEED: int):
    # url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks"
    params_answered = {
        "isAnswered": True, 
        "nmId": nm_id,
        "take": 100,    
        "skip": 0,
        "order": "desc"   # последние сначала
    }
    params_not_answered = {
        "isAnswered": False, 
        "nmId": nm_id,
        "take": 100,    
        "skip": 0,
        "order": "desc"   # последние сначала  
    }
    # делаем два запроса одновременно
    response_not_answered = requests.get(
        URL_FEEDBACK_LIST, headers=HEADERS, params=params_not_answered
    )
    if response_not_answered.status_code != 200:
        print(f"Ошибка при запросе отзывов для nmId={nm_id}: {response_not_answered.status_code}, {response_not_answered.text}")
        return []
    
    feedbacks_not_answered = get_list_of_feedbacks(response_not_answered)

    response_answered = requests.get(
        URL_FEEDBACK_LIST, headers=HEADERS, params=params_answered
    )
    if response_answered.status_code != 200:
        print(f"Ошибка при запросе отзывов для nmId={nm_id}: {response_answered.status_code}, {response_answered.text}")
        return []
    
    feedbacks_answered = get_list_of_feedbacks(response_answered)
    all_feedbacks: list[dict] = feedbacks_answered + feedbacks_not_answered

    feedback_list_sorted = sorted(
        all_feedbacks, key=lambda x: x["created_date"], reverse=True
    )
    return feedback_list_sorted[:NUMBER_OF_FEEDBACKS_NEED]


if __name__ == "__main__":
    load_dotenv()
    WB_TOKEN = os.getenv("WB_TOKEN")
    NUMBER_OF_FEEDBACKS_NEED = int(os.getenv("NUMBER_OF_FEEDBACKS_NEED"))
    URL_FEEDBACK_LIST = os.getenv("URL_FEEDBACK_LIST")
    HEADERS = {
        "Authorization": WB_TOKEN
    }

    # Path to your CSV file
    file_path_nm_ids = 'wb_articles.csv'
    df = pd.read_csv(file_path_nm_ids)

    # nm_ids = [251598270, 418395621, 394125519]  # пример списка артикулов/nmID
    nm_ids = df["nmID"].tolist()
    all_feedbacks = []  # здесь будут ВСЕ отзывы со всех nm_id
    for nm in nm_ids:
        feedbacks = get_last_feedbacks(nm, HEADERS, URL_FEEDBACK_LIST, NUMBER_OF_FEEDBACKS_NEED) 
        # all_feedbacks[nm] = feedbacks
        all_feedbacks.append(feedbacks)
        print(f"complete {nm}")
        time.sleep(0.5)  # чтобы не превысить лимиты
    
    # --- Группировка по nm_id ---
    feedbacks_by_nm = {}

    for feedback_list in all_feedbacks:
        if not feedback_list:
            continue
        nm_id = feedback_list[0]["nm_id"]  # nm_id общий для всех отзывов в группе
        feedbacks_by_nm[nm_id] = []

        for fb in feedback_list:
            # Преобразуем дату в строку для корректного JSON
            fb_clean = {
                "id": fb.get("id"),
                "created_date": fb.get("created_date").isoformat() if isinstance(fb.get("created_date"), datetime.datetime) else fb.get("created_date"),
                "rating": fb.get("product_valuation"),
                "imt_id": fb.get("imt_id"),
                "nm_id": fb.get("nm_id"),
                "text": fb.get("text", ""),
                "pros": fb.get("pros", ""),
                "cons": fb.get("cons", ""),
                "tags": fb.get("tags", ""),
                "photo": fb.get("photo_fullSize[0][0]", ""),
                "video_preview": fb.get("video_preview_image", "")
            }
            feedbacks_by_nm[nm_id].append(fb_clean)

    # --- Сохранение в JSON ---
    with open("wb_last_5_feedbacks_by_nm_id.json", "w", encoding="utf-8") as f:
        json.dump(feedbacks_by_nm, f, ensure_ascii=False, indent=2)
    print("✅ Данные сохранены в wb_last_5_feedbacks_by_nm_id.json")
