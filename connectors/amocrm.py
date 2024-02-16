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
    answer = await connector.send_request(data, url)
    if answer == '-':
        return []
    return answer


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
    answer = await connector.send_request(data, url)
    if answer == '-':
        return {}
    return answer


async def set_fields(setting: ApiSettings, session, info, lead_id):
    url = f'{host}/fill-field/'
    data = {
        'lead_id': lead_id,
        'field_id': int(info['field_id']),
        'pipeline_id': setting.pipeline_id,
        'value': str(info['value']),
        'host': setting.amo_host,
        'headers': session.headers
    }
    return await connector.send_request(data, url)


async def move_deal(setting: ApiSettings, session, lead_id):
    url = f'{host}/move-deal/'
    data = {
        'amo_host': setting.amo_host,
        'headers': session.headers,
        'deal_id': int(lead_id),
        'pipeline_id_to_set': setting.pipeline_id,
        'status_id_to_set': int(setting.qualification_finished_stage) if setting.qualification_finished_stage.isdigit() else 0
    }
    return await connector.send_request(data, url)
