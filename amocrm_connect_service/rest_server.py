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

        text = await amo.get_fields_by_deal_id(lead_id)
        return web.json_response({"result": text})

    except Exception as e:
        print(e)
        return web.Response(
            text='Ошибка настроек', content_type='application/json'
        )


app = web.Application()
app.router.add_post("/", handle)

if __name__ == "__main__":
    web.run_app(app, host='0.0.0.0', port=50050)
