import time

from database_connect_service.src import api
import whisper_service.client
from database_connect_service.src import site
from amocrm_connect_service import client as amocrm
from database_connect_service.src.site import ApiSettings
from prompt_mode_service import client as prompt_mode
from qualification_mode_service import client as qualification_mode
import asyncio


async def send_message_to_amocrm(setting, message, text, is_bot):
    message_id = await amocrm.send_message(
        setting.amo_host,
        setting.amo_email,
        setting.amo_password,
        text,
        message.chat_id,
    )
    api.add_message(message_id, message.lead_id, text, is_bot)


async def process_message(message, setting):
    fields = await amocrm.get_fields_by_deal_id(message.lead_id,
                                                setting.amo_host,
                                                setting.amo_email,
                                                setting.amo_password)

    qualification_response = await qualification_mode.run_qualification_client(message.message,
                                                                               True,
                                                                               fields,
                                                                               setting.amocrm_fields,
                                                                               setting.qualification_finished,
                                                                               setting.openai_key,
                                                                               setting.model)

    if qualification_response.success:
        if qualification_response.data.message:
            return await send_message_to_amocrm(setting, message, qualification_response.data.message, True)

        # Если есть сообщение - новая квалификация и больше нет режимов
        #  Если нет - идем в режим

    database_messages = api.get_messages_history(message.lead_id)
    answer = await prompt_mode.run(
        messages=prompt_mode.get_messages_context(database_messages, setting.prompt_context, setting.model_limit,
                                                  setting.max_tokens, fields if setting.use_amocrm_fields else []),
        model=setting.model_title,
        api_token=setting.api_token,
        max_tokens=setting.max_tokens,
        temperature=setting.temperature,
    )
    await send_message_to_amocrm(setting, message, answer, True)
    if not qualification_response.success:
        await send_message_to_amocrm(setting, message, qualification_response.data.message, True)


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
        print("Настроек:", len(settings))
        # После получения всех ответов, создаем задачи для обработки каждого сообщения
        for id, setting in enumerate(settings):
            messages = responses[id]
            for message in messages.answer:
                if api.message_exists(message.lead_id, message.id):
                    continue  # Контроль дублей

                if api.manager_intervened(message.lead_id, message.messages_history):
                    continue  # Если менеджер вмешался

                if ".m4a" in message.message:
                    if setting.voice_detection is False:
                        continue
                    message.message = await whisper_service.client.run(
                        openai_api_key=setting.api_token, url=message.message
                    )

                api.add_message(message.id, message.lead_id, message.message, False)
                tasks += 1
                asyncio.create_task(process_message(message, setting))
        print("Задач:", tasks)

        print("Total execution time: ", round(time.time() - start_time, 2))
        print('-' * 50)


asyncio.run(cycle())
