import requests 
import json
import time
from datetime import datetime


from constants import ARTICLES_WB, WB_TOKEN, URL_REQUEST


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
                    print("❌ Ошибка при парсинге даты:", created, e)
        return result
    except Exception as e:
        print("❌ Ошибка при парсинге ответа:", e)
        return []

def main():
    with open("result.txt", "w", encoding="utf-8") as f:
        for index , article_wb in enumerate(ARTICLES_WB):

            params_not_aswered = {
                "isAnswered": False, # False - необработанные 
                "nmId": article_wb,
                "take": 5,
                "skip": 0,
                "order": "dateDesc" # по убыванию даты 
            }
            params_aswered = {
                "isAnswered": True, # True - обработанные
                "nmId": article_wb,
                "take": 5,
                "skip": 0,
                "order": "dateDesc"
            }
            # делаем два запроса одновременно
            response_not_answered = requests.get(URL_REQUEST, headers=headers, params=params_not_aswered)
            response_answered = requests.get(URL_REQUEST, headers=headers, params=params_aswered)
            
            # сохраняем JSON с русскими символами
            with open(f"feedbacks_json/not_answered_{index}.json", "w", encoding="utf-8") as json_file:
                json.dump(response_not_answered.json(), json_file, ensure_ascii=False, indent=2)
            with open(f"feedbacks_json/answered_{index}.json", "w", encoding="utf-8") as json_file:
                json.dump(response_answered.json(), json_file, ensure_ascii=False, indent=2)
            
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

if __name__ == "__main__":
    headers = {
        'Authorization': WB_TOKEN
    }

    main()

