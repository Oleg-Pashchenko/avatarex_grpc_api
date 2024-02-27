from connectors import connector
from database_connect_service.src.api import get_thread_by_lead_id
from database_connect_service.src.site import ApiSettings


async def get_answer(message, setting: ApiSettings):
    return await connector.send_request(
        request={
            "assistant_id": setting.assistant_id,
            'api_token': setting.api_token,
            'question': message['message'],
            'thread_id': get_thread_by_lead_id(message['lead_id'])
        },
        url='http://178.253.22.162:9999/'
    )
