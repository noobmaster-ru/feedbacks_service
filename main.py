import requests 
import json
import time
from datetime import datetime, timedelta


from constants import ARTICLES_WB, WB_TOKEN, URL_REQUEST

headers = {
    'Authorization': WB_TOKEN
}


def get_product_valuation_and_created_date(response: requests.Response):
    try:
        data = response.json()
        # извлекаем список всех отзывов 
        feedbacks = data.get("data", {}).get("feedbacks", [])
        
        # добавляем дату создания и возвращаем список кортежей (productValuation,createdDate)
        result = []
        for fb in feedbacks:
            rating = fb.get("productValuation")
            created = fb.get("createdDate")
            if rating is not None and created is not None:
                try:
                    created_dt = datetime.fromisoformat(created.replace("Z", "+00:00"))
                    result.append((rating, created_dt))
                except Exception as e:
                    print("Ошибка разбора даты:", created, e)
        return result
    except Exception as e:
        print("Ошибка при разборе ответа:", e)
        return []


with open("result.txt", "w", encoding="utf-8") as f:
    for article_wb in ARTICLES_WB:
        time.sleep(1.0)
        params_not_aswered = {
            "isAnswered": False, # False - необработанные 
            "nmId": article_wb,
            "take": 5,
            "skip": 0
        }
        params_aswered = {
            "isAnswered": True, # True - обработанные
            "nmId": article_wb,
            "take": 5,
            "skip": 0
        }
        # делаем два запроса одновременно
        response_not_answered = requests.get(URL_REQUEST, headers=headers, params=params_not_aswered)
        response_answered = requests.get(URL_REQUEST, headers=headers, params=params_aswered)
        
        
        # парсим рейтинг отзыва и время создания в список кортежей: (рейтинг, время_создания)
        feedbacks_not_answered = get_product_valuation_and_created_date(response_not_answered)
        feedbacks_answered = get_product_valuation_and_created_date(response_answered)

        all_feedbacks = feedbacks_not_answered + feedbacks_answered
        
        # сортируем по дате убывания и берём 5 последних по дате
        sorted_feedbacks = sorted(all_feedbacks, key=lambda x: x[1], reverse=True)
        last_five_feedbacks = sorted_feedbacks[:5]

        if last_five_feedbacks:
            avg = sum([r[0] for r in last_five_feedbacks]) / len(last_five_feedbacks)
            f.write(f"{article_wb}: {avg:.2f}\n")
            print(f"{article_wb}: {avg:.2f}")
        else:
            f.write(f"{article_wb}: no ratings\n")
            print(f"{article_wb}: no ratings")


