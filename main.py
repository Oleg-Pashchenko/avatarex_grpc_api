import time

from database_connect_service.src import api
import whisper_service.client
from database_connect_service.src import site
from amocrm_connect_service import client as amocrm
from database_connect_service.src.site import ApiSettings
from prompt_mode_service import client as prompt_mode
import asyncio


async def process_message(message, setting):
    start_time = time.time()
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
    message_id = await amocrm.send_message(
        setting.amo_host,
        setting.amo_email,
        setting.amo_password,
        answer.data.message,
        message.chat_id,
    )
    api.add_message(message_id, message.lead_id, answer.data.message, True)


async def cycle():
    while True:
        start_time = time.time()
        settings: list[ApiSettings] = site.get_enabled_api_settings()
        tasks = 0

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
        print(responses)
        print("Настроек:", len(settings))
        # После получения всех ответов, создаем задачи для обработки каждого сообщения
        for id, setting in enumerate(settings):
            messages = responses[id]
            for message in messages.answer:
                print(message)
                # if api.message_exists(message.lead_id, message.lead_id):
                 #    continue  # Контроль дублей

                # if api.manager_intervened(message.lead_id, message.messages_history):
                 #    continue  # Если менеджер вмешался

                api.add_message(message.id, message.lead_id, message.message, False)
                tasks += 1
                asyncio.create_task(process_message(message, setting))
        print("Задач:", tasks)

        print("Total execution time: ", round(time.time() - start_time, 2))
        print('-' * 50)


asyncio.run(cycle())
