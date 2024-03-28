from aiohttp import web

import implementation


async def handle(request):
    try:
        data = await request.json()
        context = data.get('context', '')
        question = data.get("question", '')
        token = data.get("token", '')
        fields_from_amo = data.get('fields_from_amo', '')
        fields_to_fill = data.get('fields_to_fill', '')
        pipeline = data.get('pipeline', '')
        host = data.get('host', '')
        email = data.get('email', '')
        password = data.get('password', '')
        lead_id = data.get('lead_id', '')
        answer = await implementation.execute(
            context=context,
            user_message=question,
                                              token=token,
                                              fields_from_amo=fields_from_amo,
                                              fields_to_fill=fields_to_fill,
                                              pipeline=pipeline,
                                              host=host,
                                              email=email,
                                              password=password,
                                              lead_id=lead_id)

        return web.json_response(answer)
    except Exception as e:
        return web.Response(
            text='Ошибка настроек', content_type='application/json'
        )


app = web.Application()
app.router.add_post("/", handle)

if __name__ == "__main__":
    web.run_app(app, host='0.0.0.0', port=50054)
