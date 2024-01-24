import asyncio
import aiohttp
import json

import dotenv
import os

dotenv.load_dotenv()

server_url = 'http://' + '178.253.22.162' + ':50050'


async def send_request(request):
    async with aiohttp.ClientSession() as session:
        async with session.post(server_url, json=request) as response:
            response_text = await response.text()
            response_json = json.loads(response_text)
            return response_json
