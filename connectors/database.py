import json

import aiohttp


async def send_request(request):
    async with aiohttp.ClientSession() as session:
        print(request)
        async with session.post('http://178.253.22.162:11111/', json=request) as response:
            try:
                response_json = await response.json()
                resp = response_json['answer']
                print(response_json)
                if resp == '':
                    return '-'
                return resp

            except Exception as e:
                print(e)
                return '-'
