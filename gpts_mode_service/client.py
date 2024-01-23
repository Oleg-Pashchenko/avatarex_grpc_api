import asyncio

import aiohttp
import dotenv
import os

dotenv.load_dotenv()

server_url = 'http://' + os.getenv('SERVER_HOST_EN') + ":50056"
server_url = 'http://' + '178.253.22.162' + ':50056'


async def send_request(request):
    async with aiohttp.ClientSession() as session:
        async with session.post(server_url, json=request) as response:
            return await response.text()
