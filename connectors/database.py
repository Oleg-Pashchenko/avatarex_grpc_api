import aiohttp


async def send_request(request):
    print(request)
    async with aiohttp.ClientSession() as session:
        async with session.post('http://178.253.22.162:11111/', data=request) as response:
            print(await response.text())
            try:
                response_json = await response.json()
                resp = response_json['answer']
                if resp == '':
                    return '-'
                return resp

            except:
                return '-'
