import time
import json
import datetime 
import os 
import pandas as pd
from statistics import mean

from dotenv import load_dotenv

from services.wb_api_parsing_class import WBApiParseClass


if __name__ == "__main__":
    load_dotenv()
    WB_TOKEN = os.getenv("WB_TOKEN")
    NUMBER_OF_FEEDBACKS_NEED = int(os.getenv("NUMBER_OF_FEEDBACKS_NEED"))
    URL_FEEDBACK_LIST = os.getenv("URL_FEEDBACK_LIST")
    HEADERS = {
        "Authorization": WB_TOKEN
    }

    wb_api_parser = WBApiParseClass()

    # --- Загружаем nm_id ---
    file_path_nm_ids = 'wb_articles.csv'
    df = pd.read_csv(file_path_nm_ids)
    nm_ids = df["nmID"].tolist()

    result = {}
    total_feedbacks = 0

    for nm in nm_ids:
        feedbacks = wb_api_parser.get_last_feedbacks(nm, HEADERS, URL_FEEDBACK_LIST, NUMBER_OF_FEEDBACKS_NEED)
        if not feedbacks:
            print(f"⚠️ Нет отзывов для nm_id={nm}")
            continue

        # --- Подготовка отзывов ---
        formatted_feedbacks = []
        for fb in feedbacks:
            created_raw = fb.get("created_date") or fb.get("createdDate") or fb.get("created_at")
            try:
                created_at = (
                    created_raw if isinstance(created_raw, str)
                    else created_raw.isoformat()
                )
            except Exception:
                created_at = str(created_raw)

            formatted_feedbacks.append({
                "id": fb.get("id"),
                "created_at": created_at,
                "is_visible": fb.get("is_visible", True),
                "rating": float(fb.get("product_valuation", 0)),
                "text": fb.get("text", ""),
                "pros": fb.get("pros", ""),
                "cons": fb.get("cons", ""),
                "tags": fb.get("tags", []) or [],
                "is_answered": fb.get("is_answered"), 
                "answer_text": fb.get("answer")
            })

        # --- Сортировка по дате ---
        formatted_feedbacks.sort(key=lambda f: f["created_at"], reverse=True)

        # --- Подсчёт средних рейтингов ---
        ratings = [f["rating"] for f in formatted_feedbacks]
        def avg(n):
            return round(mean(ratings[:n]), 2) if len(ratings) >= n else round(mean(ratings), 2)

        nm_summary = {
            "last_5": avg(5),
            "last_10": avg(10),
            "last_20": avg(20),
            "last_30": avg(30),
            "feedbacks": formatted_feedbacks
        }

        result[nm] = nm_summary
        total_feedbacks += len(feedbacks)
        print(f"✅ nm_id={nm} — собрано {len(feedbacks)} отзывов")

        time.sleep(0.5)

    print(f"\n📊 Всего собрано отзывов: {total_feedbacks}")

    # --- Сохранение в JSON ---
    with open("wb_feedbacks_by_nm_id.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print("✅ Сохранено в wb_feedbacks_by_nm_id.json")
    # # Path to your CSV file
    # file_path_nm_ids = 'wb_articles.csv'
    # df = pd.read_csv(file_path_nm_ids)

    # # nm_ids = [251598270, 418395621, 394125519]  # пример списка артикулов/nmID
    # nm_ids = df["nmID"].tolist()
    # all_feedbacks = []  # здесь будут ВСЕ отзывы со всех nm_id
    # for nm in nm_ids:
    #     feedbacks = wb_api_parser.get_last_feedbacks(nm, HEADERS, URL_FEEDBACK_LIST, NUMBER_OF_FEEDBACKS_NEED) 
    #     # all_feedbacks[nm] = feedbacks
    #     all_feedbacks.append(feedbacks)
    #     print(f"complete {nm}")
    #     time.sleep(0.5)  # чтобы не превысить лимиты
    
    # # --- Группировка по nm_id ---
    # feedbacks_by_nm = {}

    # for feedback_list in all_feedbacks:
    #     if not feedback_list:
    #         continue
    #     nm_id = feedback_list[0]["nm_id"]  # nm_id общий для всех отзывов в группе
    #     feedbacks_by_nm[nm_id] = []

    #     for fb in feedback_list:
    #         # Преобразуем дату в строку для корректного JSON
    #         fb_clean = {
    #             "id": fb.get("id"),
    #             "created_date": fb.get("created_date").isoformat() if isinstance(fb.get("created_date"), datetime.datetime) else fb.get("created_date"),
    #             "rating": fb.get("product_valuation"),
    #             "imt_id": fb.get("imt_id"),
    #             "nm_id": fb.get("nm_id"),
    #             "text": fb.get("text", ""),
    #             "pros": fb.get("pros", ""),
    #             "cons": fb.get("cons", ""),
    #             "tags": fb.get("tags", ""),
    #             "photo": fb.get("photo_fullSize[0][0]", ""),
    #             "video_preview": fb.get("video_preview_image", "")
    #         }
    #         feedbacks_by_nm[nm_id].append(fb_clean)

    # # --- Сохранение в JSON ---
    # with open("wb_last_5_feedbacks_by_nm_id.json", "w", encoding="utf-8") as f:
    #     json.dump(feedbacks_by_nm, f, ensure_ascii=False, indent=2)
    # print("✅ Данные сохранены в wb_last_5_feedbacks_by_nm_id.json")
