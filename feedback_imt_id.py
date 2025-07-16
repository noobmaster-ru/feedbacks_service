import requests
from collections import defaultdict
from statistics import mean
import time

from constants import ARTICLES_WB, WB_TOKEN, URL_REQUEST, TAKE_NUMBER, SKIP_NUMBER

from services.get_list_of_feedbacks import get_list_of_feedbacks


if __name__ == "__main__":
    headers = {"Authorization": WB_TOKEN}

    with open("result_imt_id.txt", "w", encoding="utf-8") as f:
        grouped_by_imt_id = defaultdict(
            list
        )  # ключ: imt_id, значение: list[dict отзывов]
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

            # группируем по imt_id все отзывы
            for fb in all_feedbacks:
                grouped_by_imt_id[fb["imt_id"]].append(fb)

        # словарь nm_id -> average_rating
        nm_id_to_avg_rating: dict[int, float | str] = {}

        for imt_id, feedback_list in grouped_by_imt_id.items():
            # сортируем все отзывы по дате убывания
            feedback_list_sorted = sorted(
                feedback_list, key=lambda x: x["created_dt"], reverse=True
            )
            last_5 = feedback_list_sorted[:5]

            # ВСЕ уникальные nm_id по ВСЕМ отзывам в группе
            all_nm_ids_in_group = {fb["nm_id"] for fb in feedback_list}

            if last_5:
                # средний рейтинг по последним 5 отзывам
                avg_rating = round(mean([fb["product_valuation"] for fb in last_5]), 1)
                for nm_id in all_nm_ids_in_group:
                    nm_id_to_avg_rating[nm_id] = avg_rating

        # добавляем "no feedbacks" для тех артикулов, у которых вообще нет отзывов
        for article_wb in ARTICLES_WB:
            if article_wb not in nm_id_to_avg_rating:
                nm_id_to_avg_rating[article_wb] = "no feedbacks"

        # nm_id: average_rating | "no feedbacks"
        for nm_id, average_rating in nm_id_to_avg_rating.items():
            print(f"{nm_id}: {average_rating}")
            f.write(f"{nm_id}: {average_rating}\n")
    f.close()
