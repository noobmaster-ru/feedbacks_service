import json
import datetime
from collections import defaultdict
from dotenv import load_dotenv
import os
import pandas as pd
import time
from statistics import mean

from services.wb_api_parsing_class import WBApiParseClass

if __name__ == "__main__":
    load_dotenv()
    WB_TOKEN = os.getenv("WB_TOKEN")
    NUMBER_OF_FEEDBACKS_NEED = int(os.getenv("NUMBER_OF_FEEDBACKS_NEED"))
    URL_FEEDBACK_LIST = os.getenv("URL_FEEDBACK_LIST")
    HEADERS = {
        "Authorization": WB_TOKEN
    }
    NUMBER_OF_FEEDBACKS_NEED = 100

    # Path to your CSV file
    file_path_nm_ids = 'wb_articles.csv'
    df = pd.read_csv(file_path_nm_ids)

    wb_api_parser = WBApiParseClass()

    nm_ids = df["nmID"].tolist()
    all_feedbacks = []  # здесь будут ВСЕ отзывы со всех nm_id


    for nm in nm_ids:
        feedbacks = wb_api_parser.get_last_feedbacks(nm, HEADERS,  URL_FEEDBACK_LIST, NUMBER_OF_FEEDBACKS_NEED) 
        if feedbacks:
            all_feedbacks.extend(feedbacks)  # добавляем ВСЕ отзывы из списка
        print(f"✅ complete nm_id={nm}, total_feedbacks={len(feedbacks) if feedbacks else 0}")
        time.sleep(0.5)  # чтобы не превысить лимиты WB API
    
    print(f"Всего собрано отзывов: {len(all_feedbacks)}")

    # --- Группировка по imt_id ---
    grouped = defaultdict(list)

    for feedback in all_feedbacks:
        imt_id = feedback.get("imt_id")
        if not imt_id:
            continue
        
        created_raw = feedback.get("created_date") or feedback.get("createdDate") or feedback.get("created_at")
        try:
            created_at = (
                created_raw if isinstance(created_raw, str)
                else created_raw.isoformat()
            )
        except Exception:
            created_at = str(created_raw)

        grouped[imt_id].append({
            "nm_id": feedback.get("nm_id"),
            "id": feedback.get("id"),
            "created_at": created_at,
            "is_visible": feedback.get("is_visible", True),
            "rating": float(feedback.get("product_valuation", 0)),
            "text": feedback.get("text", ""),
            "pros": feedback.get("pros", ""),
            "cons": feedback.get("cons", ""),
            "tags": feedback.get("tags", ""),
            "is_answered": feedback.get("is_answered"), 
            "answer": feedback.get("answer")
        })

    # --- Формирование последних 5 отзывов по каждому imt_id ---
    result = {}

    for imt_id, feedbacks in grouped.items():
        # сортируем по дате (от новых к старым)
        sorted_revs = sorted(
            feedbacks,
            key=lambda r: r["created_at"],
            reverse=True
        )
        def avg_rating(n):
            return round(mean([r["rating"] for r in sorted_revs[:n]]) if sorted_revs[:n] else 0, 3)
        
        result[imt_id] = {
            "last_5": avg_rating(5),
            "last_10": avg_rating(10),
            "last_20": avg_rating(20),
            "last_30": avg_rating(30),
            "feedbacks": sorted_revs
        }
        # берем последние 5
        # last_5 = sorted_revs[:5]

        # result[imt_id] = last_5

    # --- Запись в JSON ---
    with open("wb_feedbacks_by_imt_id.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print("✅ Сохранено в wb_feedbacks_by_imt_id.json")
