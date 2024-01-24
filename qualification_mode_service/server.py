from aiohttp import web

import implementation


async def handle(request):
    try:
        data = await request.json()

        question = data.get("question", '')
        token = data.get("token", '')
        fields_from_amo = data.get('fields_from_amo', '')
        fields_to_fill = data.get('fields_to_fill', '')
        text = await implementation.execute(question=question,
                                            token=token,
                                            fields_from_amo=fields_from_amo,
                                            fields_to_fill=fields_to_fill)

        return web.Response(
            text=text, content_type="application/json"
        )
    except Exception as e:
        print(e)
        return web.Response(
            text='Ошибка настроек', content_type='application/json'
        )


app = web.Application()
app.router.add_post("/", handle)

if __name__ == "__main__":
    web.run_app(app, host='0.0.0.0', port=50054)
