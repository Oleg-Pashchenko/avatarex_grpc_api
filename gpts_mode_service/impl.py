from openai import AsyncOpenAI


async def execute(question: str, token: str, thread_id=None, assistant_id=''):
    with AsyncOpenAI(api_key=token) as client:
        if thread_id is None:
            thread = await client.beta.threads.create()
            thread_id = thread.id

        await client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=question
        )
        run = await client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        while True:
            run = await client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if run.status != 'in_progress':
                break

        messages = await client.beta.threads.messages.list(
            thread_id=thread_id
        )
        answer = ''
        for message in messages.data[0].content:
            answer += message.text.value + '\n'
        return answer.strip(), thread_id
