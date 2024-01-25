import re
from asyncio import sleep

from openai import AsyncOpenAI


async def execute(question: str, token: str, thread_id=None, assistant_id='', attempt=1):
    client = AsyncOpenAI(api_key=token)
    if True:
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
            await sleep(1)
            run = await client.beta.threads.runs.retrieve(
                thread_id=thread_id,
                run_id=run.id
            )
            if 'complete' in run.status:
                break

        messages = await client.beta.threads.messages.list(
            thread_id=thread_id
        )
        answer = ''
        for message in messages.data[0].content:
            answer += message.text.value + '\n'

        answer = answer.replace('*', '')
        answer = re.sub(r'\【.*?】', '', answer)
        if answer.lower().strip() == question.lower().strip():
            if attempt == 1:
                return await execute(question, token, thread_id, assistant_id, 2)
            else:
                answer = 'Извините, я Вас не понял, пожалуйста, переформулируйте вопрос!'
        return answer.strip(), thread_id
