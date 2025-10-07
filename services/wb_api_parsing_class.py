import requests
from datetime import datetime

class WBApiParseClass():
    def __init__(self):
        pass

    def get_list_of_feedbacks(self, response: requests.Response):
        try:
            data = response.json()
            # извлекаем список всех отзывов
            feedbacks = data.get("data", {}).get("feedbacks", [])

            # вспомогательный словарь для хранения всех отзывов
            feedback_by_id = {}
            # парсим данные и сохраняем в словарь , ключом будет feedback_id
            for fb in feedbacks:
                feedback_id = fb.get("id")
                parent_feedback_id = fb.get("parentFeedbackId")

                text = fb.get("text", "").strip()
                pros = fb.get("pros", "").strip()
                cons = fb.get("cons", "").strip()
                state = fb.get("state") or {}
                if state == "wbRu":
                    is_answered = True
                else:
                    is_answered = False
                
                answer = None
                if is_answered:
                    answer = fb.get("answer")

                product_details = fb.get("productDetails", {})
                nm_id = product_details.get("nmId")
                imt_id = product_details.get("imtId")

                product_valuation = fb.get("productValuation", "")
                created_date = fb.get("createdDate", "")
                created_dt = datetime.fromisoformat(created_date.replace("Z", "+00:00"))

                # длительность видео (если есть)
                video = fb.get("video")
                preview_image = (video or {}).get("previewImage", "")

                # первая ссылку на фото (если она есть)
                photo_links = fb.get("photoLinks")
                photo_full_size_link = (
                    photo_links[0].get("fullSize", "")
                    if isinstance(photo_links, list) and len(photo_links) > 0
                    else ""
                )

                # теги покупателя 
                bables = fb.get("bables")
                tags = (
                    bables
                    if isinstance(bables, list) and len(bables) > 0
                    else ""
                )
                # фильтр на непустой отзыв(тк только такие видны на сайте вб)
                if any([text, cons, pros, photo_full_size_link, preview_image, tags]):
                    # добавляем текущий отзыв
                    feedback_by_id[feedback_id] = {
                        "id": feedback_id,
                        "parent_feedback_id": parent_feedback_id,
                        "product_valuation": product_valuation,
                        "created_date": created_dt,
                        "nm_id": nm_id,
                        "imt_id": imt_id,
                        "text": text,
                        "pros": pros,
                        "cons": cons,
                        "tags": tags,
                        "is_answered": is_answered,
                        "answer": answer,
                        "video_preview_image": preview_image,
                        "photo_fullSize[0][0]": photo_full_size_link,
                    }

            # второй проход - безопасное удаление "старого/измененного" отзыва parent_feedback_id
            for feedback_id, feedback_data in list(feedback_by_id.items()):
                parent_feedback_id = feedback_data.get("parent_feedback_id")
                if parent_feedback_id is not None and parent_feedback_id in feedback_by_id:
                    del feedback_by_id[parent_feedback_id]

            return list(feedback_by_id.values())
        except Exception as e:
            print("❌ Ошибка при парсинге ответа:", e)
            return []
    
    def get_last_feedbacks(self, nm_id: int, HEADERS: dict, URL_FEEDBACK_LIST: str, NUMBER_OF_FEEDBACKS_NEED: int):
        params_answered = {
            "isAnswered": True, 
            "nmId": nm_id,
            "take": 100,    
            "skip": 0,
            "order": "desc"   # последние сначала
        }
        params_not_answered = {
            "isAnswered": False, 
            "nmId": nm_id,
            "take": 100,    
            "skip": 0,
            "order": "desc"   # последние сначала  
        }
        # делаем два запроса одновременно
        response_not_answered = requests.get(
            URL_FEEDBACK_LIST, headers=HEADERS, params=params_not_answered
        )
        if response_not_answered.status_code != 200:
            print(f"Ошибка при запросе отзывов для nmId={nm_id}: {response_not_answered.status_code}, {response_not_answered.text}")
            return []
        
        feedbacks_not_answered = self.get_list_of_feedbacks(response_not_answered)

        response_answered = requests.get(
            URL_FEEDBACK_LIST, headers=HEADERS, params=params_answered
        )
        if response_answered.status_code != 200:
            print(f"Ошибка при запросе отзывов для nmId={nm_id}: {response_answered.status_code}, {response_answered.text}")
            return []
        
        feedbacks_answered = self.get_list_of_feedbacks(response_answered)
        all_feedbacks: list[dict] = feedbacks_answered + feedbacks_not_answered

        feedback_list_sorted = sorted(
            all_feedbacks, key=lambda x: x["created_date"], reverse=True
        )
        return feedback_list_sorted[:NUMBER_OF_FEEDBACKS_NEED]
