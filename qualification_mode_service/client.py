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
            response_json = await response.json()
            resp = response_json['answer']
            resp['fill_command']['pipeline_id'] = request['pipeline']
            resp['fill_command']['amo_host'] = request['host']
            resp['fill_command']['amo_email'] = request['password']
            resp['fill_command']['amo_password'] = request['email']
            resp['fill_command']['lead_id'] = request['lead_id']
            return resp
