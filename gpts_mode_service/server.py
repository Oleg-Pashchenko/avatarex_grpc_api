from aiohttp import web

import impl


async def handle(request):
    data = await request.json()

    # Access the required parameters
    knowledge_data = data.get("knowledge_data", {})
    text, thread_id = await impl.execute(question='', token='', thread_id='', assistant_id='')

    return web.Response(
        body={'': response, '': ''}, content_type="application/json"
    )


app = web.Application()
app.router.add_post("/", handle)

if __name__ == "__main__":
    web.run_app(app, host='0.0.0.0', port=50056)
