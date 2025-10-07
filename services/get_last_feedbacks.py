import requests

from services.get_list_of_feedbacks import get_list_of_feedbacks

def get_last_feedbacks(nm_id: int, HEADERS: dict, URL_FEEDBACK_LIST: str, NUMBER_OF_FEEDBACKS_NEED: int):
    # url = "https://feedbacks-api.wildberries.ru/api/v1/feedbacks"
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
    
    feedbacks_not_answered = get_list_of_feedbacks(response_not_answered)

    response_answered = requests.get(
        URL_FEEDBACK_LIST, headers=HEADERS, params=params_answered
    )
    if response_answered.status_code != 200:
        print(f"Ошибка при запросе отзывов для nmId={nm_id}: {response_answered.status_code}, {response_answered.text}")
        return []
    
    feedbacks_answered = get_list_of_feedbacks(response_answered)
    all_feedbacks: list[dict] = feedbacks_answered + feedbacks_not_answered

    feedback_list_sorted = sorted(
        all_feedbacks, key=lambda x: x["created_date"], reverse=True
    )
    return feedback_list_sorted[:NUMBER_OF_FEEDBACKS_NEED]
