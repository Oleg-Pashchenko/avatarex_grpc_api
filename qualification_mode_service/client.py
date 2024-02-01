import asyncio
import json

import aiohttp
import dotenv
import os

dotenv.load_dotenv()

server_url = 'http://' + os.getenv('SERVER_HOST_EN') + ":8888"


async def send_request(request):
    async with aiohttp.ClientSession() as session:
        async with session.post(server_url, json=request) as response:
            response_text = await response.text()
            response_json = json.loads(response_text)
            resp = response_json['answer']
            resp['pipeline_id'] = request['pipeline']
            resp['amo_host'] = request['host']
            resp['amo_email'] = request['password']
            resp['amo_password'] = request['email']
            resp['lead_id'] = request['lead_id']
            return resp
