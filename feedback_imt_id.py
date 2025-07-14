import requests 
import json
import time
from datetime import datetime
import os 
from collections import defaultdict
from statistics import mean

from constants import ARTICLES_WB, WB_TOKEN, URL_REQUEST, TAKE_NUMBER, SKIP_NUMBER


def get_product_valuation_and_created_date(response: requests.Response):
    try:
        data = response.json()
        # извлекаем список всех отзывов 
        feedbacks = data.get("data", {}).get("feedbacks", [])
        
        # добавляем дату создания и возвращаем список словарей 
        # {
        #   productValuation: int,
        #   createdDate: datetime,
        #    ...
        # }
        # !!! если у нас text , pros , cons , photoLinks not Null!!!!
        result = []
        for fb in feedbacks:
            video = fb.get("video")
            photo_links = fb.get("photoLinks") or []

            text = fb.get("text", "").strip()
            pros = fb.get("pros", "").strip()
            cons = fb.get("cons", "").strip()
            try:
                product_details = fb.get("productDetails", {})
                nm_id = product_details.get("nmId")
                imt_id = product_details.get("imtId")
                
                product_valuation = fb.get("productValuation")
                created_date = fb.get("createdDate")

                created_dt = datetime.fromisoformat(created_date.replace("Z", "+00:00"))
                
                # длительность видео (если есть)
                try:
                    preview_image = video.get("previewImage", "")
                except:
                    preview_image = ""
               
                # первая ссылку на фото (если она есть)
                try:
                    photo_fullSize = photo_links[0].get("fullSize", "")
                except:
                    photo_fullSize = ""    
                if (text != "" or cons != "" or pros != "" or photo_fullSize != "" or preview_image != ""):
                    result.append({
                        "product_valuation": product_valuation,
                        "created_dt": created_dt,
                        "nm_id": nm_id,
                        "imt_id": imt_id,
                        "text": text,
                        "pros": pros,
                        "cons": cons,
                        "video_preview_image": preview_image,
                        "photo_fullSize[0][0]": photo_fullSize
                    })
            except Exception as e:
                print("❌ Ошибка при парсинге даты:", created_date, e)
        return result
    except Exception as e:
        print("❌ Ошибка при парсинге ответа:", e)
        return []

def main():
    with open("result_imt_id.txt", "w", encoding="utf-8") as f:
        for index , article_wb in enumerate(ARTICLES_WB):
            time.sleep(0.5)
            params_not_aswered = {
                "isAnswered": False, # False - необработанные 
                "nmId": article_wb,
                "take": TAKE_NUMBER,
                "skip": SKIP_NUMBER,
                "order": "dateDesc" # по убыванию даты 
            }
            params_aswered = {
                "isAnswered": True, # True - обработанные
                "nmId": article_wb,
                "take": TAKE_NUMBER,
                "skip": SKIP_NUMBER,
                "order": "dateDesc"
            }

            # делаем два запроса одновременно
            response_not_answered = requests.get(URL_REQUEST, headers=headers, params=params_not_aswered)
            response_answered = requests.get(URL_REQUEST, headers=headers, params=params_aswered)
            

            # парсим рейтинг отзыва и время создания в список кортежей: (рейтинг, время_создания)
            feedbacks_not_answered = get_product_valuation_and_created_date(response_not_answered)
            feedbacks_answered = get_product_valuation_and_created_date(response_answered)

            # Список всех словарей типа 
            # {
            #   product_valuation: int,
            #   created_dt: datetime,
            #   nm_id: int,
            #   imt_id: int,
            #   text: str,
            #   pros: str,
            #   cons: str,
            #   video_duration: str,
            #   photo_fullSize: str
            # }
            all_feedbacks: list[dict] = feedbacks_answered + feedbacks_not_answered
    
            # группируем по imt_id все отзывы
            grouped_by_imt: dict[int, list[dict]] = defaultdict(list)
            for fb in all_feedbacks:
                grouped_by_imt[fb["imt_id"]].append(fb)

            # dict{ nm_id: cредний рейтинг по последним 5 отзывам в группе imt_id }
            nm_id_to_avg_rating: dict[int, float | str] = {}

            for imt_id, feedback_list in grouped_by_imt.items():
                # сортируем все отзывы по дате убывания
                feedback_list_sorted = sorted(feedback_list, key=lambda x: x["created_dt"], reverse=True)
               
                # cобираем уникальные nm_id в этой группе
                nm_ids_in_group = {fb["nm_id"] for fb in feedback_list_sorted}
                
                # берём последние 5 отзывов
                last_5_ratings = [fb["product_valuation"] for fb in feedback_list_sorted[:5]]
                
                if not last_5_ratings:
                    # нет отзывов
                    nm_id_to_avg_rating[article_wb] = "no feedbacks"
                else:
                    for nm_id in nm_ids_in_group:
                        nm_id_to_avg_rating[nm_id] = round(mean(last_5_ratings), 1)

            for nm_id, avg in nm_id_to_avg_rating.items():
                print(f"{nm_id}: {avg}")
                f.write(f"{nm_id}: {avg}\n")


if __name__ == "__main__":
    headers = {
        'Authorization': WB_TOKEN
    }
    
    main()
