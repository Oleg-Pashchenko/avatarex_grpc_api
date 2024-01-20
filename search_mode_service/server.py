from aiohttp import web

import impl


async def handle(request):
    try:
        data = await request.json()
        database = data.get("database", [])
        search_rules = data.get("search_rules", {})
        message_format = data.get('message_format', "")
        repeat = data.get("repeat", 1)
        question = data.get("question", "")
        api_key = data.get('api_key', '')
        detecting_error_message = data.get('detecting_error_message', '')
        classification_error_message = data.get('classification_error_message', '')
        response = await impl.run(database, search_rules, message_format, repeat, question, api_key,
                                  detecting_error_message, classification_error_message)

        return web.Response(
            text=response, content_type="application/json"
        )
    except:
        return web.Response(
            text="Server error (search mode)", content_type='application/json'
        )


app = web.Application()
app.router.add_post("/", handle)

if __name__ == "__main__":
    web.run_app(app, host='0.0.0.0', port=50057)
