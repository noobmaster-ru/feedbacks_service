import requests 
import time
from datetime import datetime
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
        #   createdDate: datetime ,
        #   ...
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
    with open("result_nm_id.txt", "w", encoding="utf-8") as file:
        for  article_wb in ARTICLES_WB:
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
            #   text: str,
            #   pros: str,
            #   cons: str,
            #   video_duration: str,
            #   photo_fullSize: str
            # }
            all_feedbacks: list[dict] = feedbacks_answered + feedbacks_not_answered

            feedback_list_sorted = sorted(all_feedbacks, key=lambda x: x["created_dt"], reverse=True)

            # берём последние 5 отзывов
            last_5_ratings = [fb["product_valuation"] for fb in feedback_list_sorted[:5]]
            if len(last_5_ratings) > 0:
                avg_rating = round(mean(last_5_ratings), 1)
                print(f"{article_wb}: {avg_rating}")
                file.write(f"{article_wb}: {avg_rating}\n")
            else:
                print(f"{article_wb}: no feedbacks")
                file.write(f"{article_wb}: no feedbacks\n")

if __name__ == "__main__":
    headers = {
        'Authorization': WB_TOKEN
    }
    main()