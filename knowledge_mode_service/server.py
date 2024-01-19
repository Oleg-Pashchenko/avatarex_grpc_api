from aiohttp import web

from knowledge_mode_service import impl


async def handle(request):
    data = await request.json()

    # Access the required parameters
    knowledge_data = data.get("knowledge_data", {})
    question = data.get("question", "")
    api_key = data.get('api_key', "")
    classification_error_message = data.get("classification_error_message", "")
    detecting_error_message = data.get("detecting_error_message", "")
    response = await impl.run(knowledge_data, question, api_key, classification_error_message,
                              detecting_error_message)

    return web.Response(
        text=response, content_type="application/json"
    )


app = web.Application()
app.router.add_post("/", handle)

if __name__ == "__main__":
    web.run_app(app, host='0.0.0.0', port=50055)
