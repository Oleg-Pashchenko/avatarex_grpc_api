from database_connect_service.src.api import get_thread_by_lead_id, save_thread
from gpts_mode_service import client as gpts


async def get_answer(message, setting):
    thread_id = get_thread_by_lead_id(message.lead_id)
    answer = await gpts.send_request({
        'question': message.message,
        'token': setting.api_token,
        'thread_id': thread_id,
        'assistant_id': setting.assistant_id
    })
    a = answer.split('|||')
    if not thread_id:
        save_thread(lead_id=message.lead_id, thread_id=a[0])
    try:
        answer_to_sent = a[1]
    except:
        answer_to_sent = answer
    return answer_to_sent
