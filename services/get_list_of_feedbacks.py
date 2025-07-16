from requests import Response
from datetime import datetime


# return a list of feedbacks: "fedback_id": {...}
def get_list_of_feedbacks(response: Response):
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

            product_details = fb.get("productDetails", {})
            nm_id = product_details.get("nmId")
            imt_id = product_details.get("imtId")

            product_valuation = fb.get("productValuation", "")
            created_date = fb.get("createdDate", "")
            created_dt = datetime.fromisoformat(created_date.replace("Z", "+00:00"))

            # длительность видео (если есть)
            video = fb.get("video") or ""
            preview_image = (video or {}).get("previewImage", "")

            # первая ссылку на фото (если она есть)
            photo_links = fb.get("photoLinks") or []
            photo_full_size_link = (
                photo_links[0].get("fullSize", "")
                if isinstance(photo_links, list) and len(photo_links) > 0
                else ""
            )

            # фильтр на непустой отзыв(тк только такие видны на сайте вб)
            if any([text, cons, pros, photo_full_size_link, preview_image]):
                # добавляем текущий отзыв
                feedback_by_id[feedback_id] = {
                    "id": feedback_id,
                    "parent_feedback_id": parent_feedback_id,
                    "product_valuation": product_valuation,
                    "created_dt": created_dt,
                    "nm_id": nm_id,
                    "imt_id": imt_id,
                    "text": text,
                    "pros": pros,
                    "cons": cons,
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
