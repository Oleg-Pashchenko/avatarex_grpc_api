import aiohttp


async def send_request(request):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://178.253.22.162:11111/', json=request) as response:
            print(await response.text())
            response_json = await response.json()
            resp = response_json['answer']
            return resp

