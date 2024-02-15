import aiohttp


async def send_request(request: dict, url: str):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=request) as response:
            try:
                response_json = await response.json()
                if response_json['status'] is False:
                    print(response_json)
                    return '-'
                resp = response_json['answer']
                if resp == '':
                    print(response_json)
                    return '-'
                return resp

            except Exception as e:
                return '-'
