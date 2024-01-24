from aiohttp import web

import impl


async def handle(request):
    try:
        data = await request.json()

        # Access the required parameters
        lead_id = data.get("lead_id", '')
        amo_host = data.get("amo_host", '')
        amo_email = data.get("amo_email", '')
        amo_password = data.get("amo_password", '')
        amo = impl.AmoCRM(amo_host, amo_email, amo_password)
        await amo.connect_async()
        text = await amo.get_fields_by_deal_id(lead_id)
        return web.json_response(text)

    except Exception as e:
        print(e)
        return web.Response(
            text='Ошибка настроек', content_type='application/json'
        )


async def handle2(request):
    try:
        data = await request.json()

        # Access the required parameters
        lead_id = data.get("lead_id", '')
        field_id = data.get("field_id", '')
        pipeline_id = data.get("pipeline_id", '')
        value = data.get("value", '')


        amo_host = data.get("amo_host", '')
        amo_email = data.get("amo_email", '')
        amo_password = data.get("amo_password", '')
        amo = impl.AmoCRM(amo_host, amo_email, amo_password)
        await amo.connect_async()
        await amo.set_field_by_id(deal_id=lead_id, field_id=field_id, pipeline_id=pipeline_id, value=value)
        return web.json_response({'status': 'ok'})

    except Exception as e:
        print(e)
        return web.json_response({'status': 'err'})


app = web.Application()
app.router.add_post("/", handle)
app.router.add_post('/fill-field', handle2)

if __name__ == "__main__":
    web.run_app(app, host='0.0.0.0', port=50050)
