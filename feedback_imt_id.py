# import requests
# from collections import defaultdict
# from statistics import mean
# import time

# from constants import ARTICLES_WB, WB_TOKEN, URL_REQUEST, TAKE_NUMBER, SKIP_NUMBER

# from services.get_list_of_feedbacks import get_list_of_feedbacks


# if __name__ == "__main__":
#     headers = {"Authorization": WB_TOKEN}

#     with open("result_imt_id.txt", "w", encoding="utf-8") as f:
#         grouped_by_imt_id = defaultdict(
#             list
#         )  # ключ: imt_id, значение: list[dict отзывов]
#         for article_wb in ARTICLES_WB:
#             time.sleep(1.0)
#             params_not_aswered = {
#                 "isAnswered": False,  # False - необработанные
#                 "nmId": article_wb,
#                 "take": TAKE_NUMBER,
#                 "skip": SKIP_NUMBER,
#                 "order": "dateDesc",  # по убыванию даты
#             }
#             params_aswered = {
#                 "isAnswered": True,  # True - обработанные
#                 "nmId": article_wb,
#                 "take": TAKE_NUMBER,
#                 "skip": SKIP_NUMBER,
#                 "order": "dateDesc",
#             }

#             # делаем два запроса одновременно
#             response_not_answered = requests.get(
#                 URL_REQUEST, headers=headers, params=params_not_aswered
#             )
#             feedbacks_not_answered = get_list_of_feedbacks(response_not_answered)

#             response_answered = requests.get(
#                 URL_REQUEST, headers=headers, params=params_aswered
#             )
#             feedbacks_answered = get_list_of_feedbacks(response_answered)

#             all_feedbacks: list[dict] = feedbacks_answered + feedbacks_not_answered

#             # группируем по imt_id все отзывы
#             for fb in all_feedbacks:
#                 grouped_by_imt_id[fb["imt_id"]].append(fb)

#         # словарь nm_id -> average_rating
#         nm_id_to_avg_rating: dict[int, float | str] = {}

#         for imt_id, feedback_list in grouped_by_imt_id.items():
#             # сортируем все отзывы по дате убывания
#             feedback_list_sorted = sorted(
#                 feedback_list, key=lambda x: x["created_dt"], reverse=True
#             )
#             last_5 = feedback_list_sorted[:5]

#             # ВСЕ уникальные nm_id по ВСЕМ отзывам в группе
#             all_nm_ids_in_group = {fb["nm_id"] for fb in feedback_list}
#             if last_5:
#                 # средний рейтинг по последним 5 отзывам
#                 avg_rating = round(mean([fb["product_valuation"] for fb in last_5]), 1)
#                 for nm_id in all_nm_ids_in_group:
#                     nm_id_to_avg_rating[nm_id] = avg_rating

#         # добавляем "no feedbacks" для тех артикулов, у которых вообще нет отзывов
#         for article_wb in ARTICLES_WB:
#             if article_wb not in nm_id_to_avg_rating:
#                 nm_id_to_avg_rating[article_wb] = "no feedbacks"

#         # nm_id: average_rating | "no feedbacks"
#         for nm_id, average_rating in nm_id_to_avg_rating.items():
#             print(f"{nm_id}: {average_rating}")
#             f.write(f"{nm_id}: {average_rating}\n")
#     f.close()


import json
import datetime
from collections import defaultdict
from dotenv import load_dotenv
import os
import pandas as pd
import time



from feedback_nm_id import get_last_feedbacks


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

    # nm_ids = [251598270, 418395621, 394125519]  # пример списка артикулов/nmID
    nm_ids = df["nmID"].tolist()
    all_feedbacks = []  # здесь будут ВСЕ отзывы со всех nm_id
    for nm in nm_ids:
        feedbacks = get_last_feedbacks(nm, HEADERS,  URL_FEEDBACK_LIST, NUMBER_OF_FEEDBACKS_NEED) 
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
