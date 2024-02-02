import json

import aiohttp


async def send_request(request):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://178.253.22.162:11111/', json=json.dumps(request)) as response:
            try:
                response_json = await response.json()
                resp = response_json['answer']
                if resp == '':
                    return '-'
                return resp

            except:
                return '-'
