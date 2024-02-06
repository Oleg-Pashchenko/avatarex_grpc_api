import asyncio
import json

import aiohttp
import dotenv
import os

from database_connect_service.src.site import Settings, ApiSettings

dotenv.load_dotenv()

server_url = 'http://' + os.getenv('SERVER_HOST_EN') + ":8888"


async def send_request(request):
    async with aiohttp.ClientSession() as session:
        async with session.post(server_url, json=request) as response:
            response_json = await response.json()
            resp = response_json['answer']
            if resp['fill_command']:
                resp['fill_command']['pipeline_id'] = request['pipeline']
                resp['fill_command']['amo_host'] = request['host']
                resp['fill_command']['amo_email'] = request['password']
                resp['fill_command']['amo_password'] = request['email']
                resp['fill_command']['lead_id'] = request['lead_id']
            return resp


async def create_qualification(setting, message, fields):
    data = {
        'context': setting.prompt_context,
        'user_answer': message.message,
        'token': setting.api_token,
        'amo_fields': fields,
        'avatarex_fields': setting.qualification_fields,
        'pipeline': setting.pipeline_id,
        'host': setting.amo_host,
        'email': setting.amo_email,
        'password': setting.amo_password,
        'lead_id': message.lead_id
    }
    return await send_request(data)


async def need_qualification(setting: ApiSettings, message_history):
    triggers = setting.trigger_phrases
    for m in message_history:
        for trigger in triggers:
            if m['role'] == 'user' and trigger.lower().strip() in m['content'].lower().strip():
                return True

    return False
