import json
import datetime
from collections import defaultdict
from dotenv import load_dotenv
import os
import pandas as pd
import time


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
        
        # created_raw = feedback.get("created_date") 
        # if not created_raw:
            # continue

        # try:
        #     created_date = datetime.fromisoformat(created_raw.replace("Z", "+00:00"))
        # except Exception as e:
        #     print(f"Ошибка преобразования .fromisoformat даты '{created_raw}': {e}")
        #     continue
        grouped[imt_id].append({
            "id": feedback.get("id"),
            "created_date": feedback.get("created_date").isoformat() if isinstance(feedback.get("created_date"), datetime.datetime) else feedback.get("created_date"),
            "rating": feedback.get("product_valuation"),
            "imt_id": feedback.get("imt_id"),
            "nm_id": feedback.get("nm_id"),
            "text": feedback.get("text", ""),
            "pros": feedback.get("pros", ""),
            "cons": feedback.get("cons", ""),
            "tags": feedback.get("tags", ""),
            "photo": feedback.get("photo_fullSize[0][0]", ""),
            "video_preview": feedback.get("video_preview_image", "")
        })

    # --- Формирование последних 5 отзывов по каждому imt_id ---
    result = {}

    for imt_id, revs in grouped.items():
        # сортируем по дате (от новых к старым)
        sorted_revs = sorted(revs, key=lambda r: r["created_date"], reverse=True)
        # берем последние 5
        last_5 = sorted_revs[:5]
        # преобразуем дату обратно в строку
        # for r in last_5:
        #     r["created_date"] = r["created_date"].isoformat()
        result[imt_id] = last_5

    # --- Запись в JSON ---
    with open("wb_last_5_feedbacks_by_imt_id.json", "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

    print("✅ Сохранено в wb_last_5_feedbacks_by_imt_id.json")
