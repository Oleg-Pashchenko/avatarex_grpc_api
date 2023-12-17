import time

import knowledge_mode_hardcode
from database_connect_service.src import api
import whisper_service.client
from database_connect_service.src import site
from amocrm_connect_service import client as amocrm
from database_connect_service.src.site import ApiSettings, get_enabled_api_settings
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

    # qualification_response = await qualification_mode.run_qualification_client(message.message,
    #                                                                            True,
    #                                                                            fields,
    #                                                                            setting.amocrm_fields,
    #                                                                            setting.qualification_finished,
    #                                                                            setting.api_token,
    #                                                                           setting.model_title)

    # if qualification_response.success:
    #     if qualification_response.data.message:
    #         return await send_message_to_amocrm(setting, message, qualification_response.data.message, True)

    # Если есть сообщение - новая квалификация и больше нет режимов
    #  Если нет - идем в режим
    if setting.mode_id == 1:
        database_messages = api.get_messages_history(message.lead_id)
        answer = await prompt_mode.run(
            messages=prompt_mode.get_messages_context(database_messages, setting.prompt_context, setting.model_limit,
                                                      setting.max_tokens, fields if setting.use_amocrm_fields else []),
            model=setting.model_title,
            api_token=setting.api_token,
            max_tokens=setting.max_tokens,
            temperature=setting.temperature,
        )
        await send_message_to_amocrm(setting, message, answer.data.message, True)
    # elif setting.mode_id == 2:  # Prompt + Knowledge
    #     status, message_text = await knowledge_mode_hardcode.main(setting.knowledge_data, message, setting.api_token)
    #     if status:
    #         await send_message_to_amocrm(setting, message, message_text, True)
    #     else:
    #         await send_message_to_amocrm(setting, message, setting.openai_error_message, True)
    #
    # elif setting.mode_id == 33:
    #     status, message_text = await knowledge_mode_hardcode.main(setting.knowledge_data, message, setting.api_token)
    #     if status:
    #         await send_message_to_amocrm(setting, message, message_text, True)
    #     else:
    #         database_messages = api.get_messages_history(message.lead_id)
    #         answer = await prompt_mode.run(
    #             messages=prompt_mode.get_messages_context(database_messages, setting.prompt_context,
    #                                                       setting.model_limit,
    #                                                       setting.max_tokens,
    #                                                       fields if setting.use_amocrm_fields else []),
    #             model=setting.model_title,
    #             api_token=setting.api_token,
    #             max_tokens=setting.max_tokens,
    #             temperature=setting.temperature,
    #         )
    #         await send_message_to_amocrm(setting, message, answer.data.message, True)
    #
    # if not qualification_response.success and qualification_response.data.message:
    #     await send_message_to_amocrm(setting, message, qualification_response.data.message, True)
    #


async def process_settings(setting):
    messages = await amocrm.read_unanswered_messages(
        setting.amo_host,
        setting.amo_email,
        setting.amo_password,
        setting.pipeline_id,
        setting.statuses_ids,
    )
    loop = asyncio.get_event_loop()

    for message in messages.answer:
        try:
            if api.message_exists(message.lead_id, message.id):
                continue  # Duplicate check

            if api.manager_intervened(message.lead_id, message.messages_history):
                continue  # Manager intervention check

            if ".m4a" in message.message:
                if setting.voice_detection is False:
                    continue
                message.message = await whisper_service.client.run(
                    openai_api_key=setting.api_token, url=message.message
                )

            # Assuming `api.add_message` is an asynchronous function
            await loop.run_in_executor(None, api.add_message, message.id, message.lead_id, message.message, False)

            # Create tasks for parallel processing of messages
            asyncio.ensure_future(process_message(message, setting))
        except Exception as e:
            print(f"Error processing message: {e}")


async def cycle():
    while True:
        start_time = time.time()
        settings: list[ApiSettings] = get_enabled_api_settings()

        # Create tasks for parallel processing of settings
        for setting in settings:
            asyncio.ensure_future(process_settings(setting))

        print('-' * 50)
        elapsed_time = time.time() - start_time
        print(f"Cycle completed in {elapsed_time} seconds")
        await asyncio.sleep(5)


# Run the event loop
asyncio.run(cycle())

