from connectors import connector
from database_connect_service.src.site import ApiSettings
import os
import dotenv

dotenv.load_dotenv()

host = os.getenv('AMOCRM_HOST')


async def read_messages(setting, session):
    url = f'{host}/get-messages/'
    data = {
        'amo_host': setting.amo_host,
        'amojo_hash': session.amojo_id,
        'chat_token': session.chat_token,
        'pipeline_id': setting.pipeline_id,
        'stage_ids': setting.statuses_ids,
        'headers': session.headers
    }
    return await connector.send_request(data, url)


async def send_message(setting: ApiSettings, session, text: str, chat_id: int):
    url = f'{host}/send-message/'
    data = {
        'amo_host': setting.amo_host,
        'amojo_hash': session.amojo_id,
        'chat_token': session.chat_token,
        'message': text,
        'chat_id': chat_id
    }
    return await connector.send_request(data, url)


async def get_fields(setting: ApiSettings, session, lead_id: int):
    url = f'{host}/get-fields/'
    data = {
        'lead_id': lead_id,
        'amo_host': setting.amo_host,
        'headers': session.headers
    }
    return await connector.send_request(data, url)


async def set_fields(setting: ApiSettings, session, lead_id, field_id, field_value):
    print(lead_id)
    return
    url = f'{host}/fill-field/'
    data = {
        'lead_id': lead_id,
        'field_id': field_id,
        'pipeline_id': setting.pipeline_id,
        'value': field_value,
        'host': setting.amo_host,
        'headers': session.headers
    }
    return await connector.send_request(data, url)
