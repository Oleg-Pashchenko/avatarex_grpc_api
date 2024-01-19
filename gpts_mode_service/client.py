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


if __name__ == '__main__':
    print(asyncio.run(send_request({
        'question': 'Привет',
        'token': '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',
        'thread_id': None,
        'assistant_id': 'asst_eUTMQDPg5X17rG6WuAeLzx7m'}
    )))
