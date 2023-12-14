import time

import whisper_service.client
from database_connect_service.src import site
from amocrm_connect_service import client as amocrm
from database_connect_service.src.site import ApiSettings
from prompt_mode_service import client as prompt_mode
import asyncio


async def process_message(message, setting):
    start_time = time.time()

    # Check if message already in database - skip it
    # Get fields to
    # If manager already write to the client - do nothing
    # Mark message checked and save it
    # Get qualification information
    #

    if ".m4a" in message.message:
        message.message = await whisper_service.client.run(
            openai_api_key=setting.api_token, url=message.message
        )

    answer = await prompt_mode.run(
        messages=[
            {"role": "system", "content": setting.prompt_context},
            {"role": "user", "content": message.message},
        ],
        model=setting.model_title,
        api_token=setting.api_token,
        max_tokens=setting.max_tokens,
        temperature=setting.temperature,
    )
    await amocrm.send_message(
        setting.amo_host,
        setting.amo_email,
        setting.amo_password,
        answer.data.message,
        message.chat_id,
    )


async def cycle():
    while True:
        start_time = time.time()
        settings: list[ApiSettings] = site.get_enabled_api_settings()
        tasks = []

        # Создаем список корутин, каждая из которых представляет собой read_unanswered_messages
        coroutines = [
            amocrm.read_unanswered_messages(
                setting.amo_host,
                setting.amo_email,
                setting.amo_password,
                setting.pipeline_id,
                setting.statuses_ids,
            )
            for setting in settings
        ]
        # Используем asyncio.gather для выполнения всех корутин параллельно
        responses = await asyncio.gather(*coroutines)

        print("Настроек:", len(settings))
        # После получения всех ответов, создаем задачи для обработки каждого сообщения
        for id, setting in enumerate(settings):
            messages = responses[id]
            for message in messages.answer:
                tasks.append(process_message(message, setting))
        print("Задач:", len(tasks))
        # Ожидаем завершения всех задач
        await asyncio.gather(*tasks)

        print("Total execution time: ", round(time.time() - start_time, 2))
        print('-' * 50)

asyncio.run(cycle())
