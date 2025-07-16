import requests
from statistics import mean
import time
from constants import ARTICLES_WB, WB_TOKEN, URL_REQUEST, TAKE_NUMBER, SKIP_NUMBER

from services.get_list_of_feedbacks import get_list_of_feedbacks

if __name__ == "__main__":
    headers = {"Authorization": WB_TOKEN}
    with open("result_nm_id.txt", "w", encoding="utf-8") as file:
        for article_wb in ARTICLES_WB:
            time.sleep(1.0)
            params_not_aswered = {
                "isAnswered": False,  # False - необработанные
                "nmId": article_wb,
                "take": TAKE_NUMBER,
                "skip": SKIP_NUMBER,
                "order": "dateDesc",  # по убыванию даты
            }
            params_aswered = {
                "isAnswered": True,  # True - обработанные
                "nmId": article_wb,
                "take": TAKE_NUMBER,
                "skip": SKIP_NUMBER,
                "order": "dateDesc",
            }

            # делаем два запроса одновременно
            response_not_answered = requests.get(
                URL_REQUEST, headers=headers, params=params_not_aswered
            )
            feedbacks_not_answered = get_list_of_feedbacks(response_not_answered)

            response_answered = requests.get(
                URL_REQUEST, headers=headers, params=params_aswered
            )
            feedbacks_answered = get_list_of_feedbacks(response_answered)

            all_feedbacks: list[dict] = feedbacks_answered + feedbacks_not_answered

            feedback_list_sorted = sorted(
                all_feedbacks, key=lambda x: x["created_dt"], reverse=True
            )

            # берём последние 5 отзывов
            last_5_ratings = [
                fb["product_valuation"] for fb in feedback_list_sorted[:5]
            ]
            if last_5_ratings:
                avg_rating = round(mean(last_5_ratings), 1)
                print(f"{article_wb}: {avg_rating}")
                file.write(f"{article_wb}: {avg_rating}\n")
            else:
                print(f"{article_wb}: no feedbacks")
                file.write(f"{article_wb}: no feedbacks\n")
        file.close()
