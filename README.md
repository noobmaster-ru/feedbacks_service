# feedbacks_service

feedback_nm_id.py - возвращает статистику по каждому артикулу 

feedback_imt_id.py - возвращает статистику по каждой карточке

для запуска нужен список nm_ids - получаем его get_nm_id.py

сначала запустить python get_nm_id.py, затем python feedback_nm_id/imt_id.py

```
{
    "251598270": { // nm_id or imt_id
        "last_5": 3.4,
        "last_10": 3.9,
        "last_20": 4.3,
        "last_30": 4.47,
        "feedbacks": [
            {
                "id": "5oNndPszuRzOhgcJm4sc",
                "created_at": "2025-10-05T07:00:46+00:00",
                "is_visible": true,
                "rating": 4.0,
                "text": "",
                "pros": "",
                "cons": "",
                "tags": [
                    "внешний вид"
                ],
                "is_answered": false,
                "answer": null
            },
            {
                "id": "l8nLeMSFdwbw9hZWOEJF",
                "created_at": "2025-08-29T14:01:10+00:00",
                "is_visible": true,
                "rating": 1.0,
                "text": "",
                "pros": "",
                "cons": "",
                "tags": [
                    "качество"
                ],
                "is_answered": true,
                "answer": {
                    "text": "Здравствуйте! Нам искренне жаль, что наш товар не оправдал Ваших ожиданий! Нам важно Ваше мнение и мы хотим, чтобы у Вас остались только положительные эмоции от использования нашего товара! Пожалуйста, свяжитесь с нами через \"чат с продавцом\" если у Вас остались вопросы по товару или его использованию!",
                    "state": "wbRu",
                    "editable": true
                }
            },
            ...
        ]
    }
    ...
}
```