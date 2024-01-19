from aiohttp import web

import impl


async def handle(request):
    data = await request.json()

    # Access the required parameters
    question = data.get("question", '')
    token = data.get("token", '')
    thread_id = data.get("thread_id", '')
    assistant_id = data.get("assistant_id", '')
    text, thread_id = await impl.execute(question=question,
                                         token=token,
                                         thread_id=thread_id,
                                         assistant_id=assistant_id)

    return web.Response(
        text=f"{thread_id}|||{text}", content_type="application/json"
    )


app = web.Application()
app.router.add_post("/", handle)

if __name__ == "__main__":
    web.run_app(app, host='0.0.0.0', port=50056)
