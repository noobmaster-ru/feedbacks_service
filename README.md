# feedbacks_service

feedback_nm_id.py - возвращает средний рейтинг последних 5 отзывов ОТДЕЛЬНО по каждому артикулу
feedback_imt_id.py - возвращает средний рейтинг последних 5 отзывов В СУММЕ ПО КАРТОЧКЕ по каждому артикулу

Парсим следующие данные:
```
    {   
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
        "photo_fullSize[0][0]": photo_full_size_link
    }
```