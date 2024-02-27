from connectors import connector
from database_connect_service.src.api import get_thread_by_lead_id
from database_connect_service.src.site import ApiSettings


async def get_answer(message, setting: ApiSettings):
    return await connector.send_request(
        request={
            'url': message['answer'],
            'key': setting.api_token
        },
        url='http://178.253.22.162:9999/'
    )
