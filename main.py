import time

from database_connect_service.src import api
import whisper_service.client
from amocrm_connect_service import client as amocrm
from database_connect_service.src.api import get_thread_by_lead_id, save_thread
from database_connect_service.src.site import ApiSettings, get_enabled_api_settings
from prompt_mode_service import client as prompt_mode
from knowledge_mode_service import client as knowledge_mode
from gpts_mode_service import client as gpts
import asyncio
import os


async def send_message_to_amocrm(setting, message, text, is_bot):
    print('Отправляю сообщение', text, message.chat_id)
    st = time.time()
    message_id = await amocrm.send_message(
        setting.amo_host,
        setting.amo_email,
        setting.amo_password,
        text,
        message.chat_id,
    )
    api.add_message(message_id, message.lead_id, text, is_bot)
    api.add_stats('Crm Send', time.time() - st, message.id)


async def process_message(message, setting):
    print('Обрабатывается сообщение!', setting.amo_host)
    st = time.time()
    fields = await amocrm.get_fields_by_deal_id(message.lead_id,
                                                setting.amo_host,
                                                setting.amo_email,
                                                setting.amo_password)
    api.add_stats('CRM Fields', time.time() - st, message.id)
    # qualification_response = await qualification_mode.run_qualification_client(message.message,
    #                                                                            True,
    #                                                                            fields,
    #                                                                           setting.amocrm_fields,
    #                                                                           setting.qualification_finished,
    #                                                                           setting.api_token,
    #                                                                           setting.model_title)

    # if qualification_response.success:
    #    if qualification_response.data.message:
    #        return await send_message_to_amocrm(setting, message, qualification_response.data.message, True)

    # Если есть сообщение - новая квалификация и больше нет режимов
    #  Если нет - идем в режим

    print(setting.mode_id)
    if setting.mode_id == 1:
        st = time.time()
        database_messages = api.get_messages_history(message.lead_id)
        answer = await prompt_mode.run(
            messages=prompt_mode.get_messages_context(database_messages, setting.prompt_context, setting.model_limit,
                                                      setting.max_tokens, fields if setting.use_amocrm_fields else []),
            model=setting.model_title,
            api_token=setting.api_token,
            max_tokens=setting.max_tokens,
            temperature=setting.temperature,
        )
        api.add_stats(time.time() - st, 'Prompt mode', message.id)
        await send_message_to_amocrm(setting, message, answer.data.message, True)

    elif setting.mode_id == 4:  # Datbase mode
        answer = 'Метод в финальной разработке!'
        await send_message_to_amocrm(setting, message, answer, True)

    elif setting.mode_id == 7:  # Gpt's API
        thread_id = get_thread_by_lead_id(message.lead_id)
        answer = await gpts.send_request({
            'question': message.message,
            'token': setting.api_token,
            'thread_id': thread_id,
            'assistant_id': setting.assistant_id
        })
        if not thread_id:
            save_thread(lead_id=message.lead_id, thread_id=answer['thread_id'])
        await send_message_to_amocrm(setting, message, answer['text'], True)

    elif setting.mode_id == 3:
        if len(setting.knowledge_data) == 0:
            answer = 'Обратитесь к поддержке. База знаний не настроена!'
        else:
            answer = await knowledge_mode.send_request(
                {
                    "knowledge_data": setting.knowledge_data,
                    "question": message.message,
                    'api_key': setting.api_token,
                    'classification_error_message': setting.openai_error_message,
                    'detecting_error_message': setting.avatarex_error_message
                }
            )
            if answer == setting.openai_error_message or answer == setting.avatarex_error_message:
                database_messages = api.get_messages_history(message.lead_id)
                answer = await prompt_mode.run(
                    messages=prompt_mode.get_messages_context(database_messages, setting.prompt_context,
                                                              setting.model_limit,
                                                              setting.max_tokens,
                                                              fields if setting.use_amocrm_fields else []),
                    model=setting.model_title,
                    api_token=setting.api_token,
                    max_tokens=setting.max_tokens,
                    temperature=setting.temperature,
                )
                answer = answer.data.message
        await send_message_to_amocrm(setting, message, answer, True)

    elif setting.mode_id == 2:
        if len(setting.knowledge_data) == 0:
            answer = 'Обратитесь к поддержке. База знаний не настроена!'
        else:
            answer = await knowledge_mode.send_request(
                {
                    "knowledge_data": setting.knowledge_data,
                    "question": message.message,
                    'api_key': setting.api_token,
                    'classification_error_message': setting.openai_error_message,
                    'detecting_error_message': setting.avatarex_error_message
                }
            )
        await send_message_to_amocrm(setting, message, answer, True)
    api.add_stats('Finish time', time.time(), message.id)

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
    st = time.time()
    messages = await amocrm.read_unanswered_messages(
        setting.amo_host,
        setting.amo_email,
        setting.amo_password,
        setting.pipeline_id,
        setting.statuses_ids,
    )
    # Список задач для параллельной обработки сообщений
    tasks = []
    for message in messages.answer:
        try:
            if api.message_exists(message.lead_id, message.id):
                # print(f"DELETE FROM messages WHERE message_id='{message.id}'")
                # print('Сообщение существует!', message.id, message.message, setting.amo_host)
                continue  # Duplicate check

            if setting.manager_intervented_active and api.manager_intervened(message.lead_id, message.messages_history):
                print(setting.amo_host, 'Вмешательство менеджеров!', message.message)
                continue  # Manager intervention check

            if ".m4a" in message.message:
                if setting.voice_detection is False:
                    continue
                message.message = await whisper_service.client.run(
                    openai_api_key=setting.api_token, url=message.message
                )
            # Assuming `api.add_message` is an asynchronous function
            api.add_message(message.id, message.lead_id, message.message, False)
           #  api.create_stats(message.id, )
            api.add_stats(st, 'Start Time', message.id)
            api.add_stats(time.time() - st, 'CRM Read', message.id)

            # Создаем задачу для асинхронной обработки сообщения
            print(f'[{setting.amo_host}] Обрабатываю сообщение {message.message}')
            task = process_message(message, setting)
            tasks.append(task)

        except Exception as e:
            pass
            # print(f"Error processing message: {e}")
    # Параллельное выполнение задач
    await asyncio.gather(*tasks)


async def cycle():
    while True:
        settings: list[ApiSettings] = get_enabled_api_settings()
        for setting in settings:
            # if 'https://bosswonderscakeru.amocrm.ru' in setting.amo_host:
            #     await process_settings(setting)
            #    exit(0)

            if os.getenv('MODE') == 'testing':
                if 'chatgpt.amocrm' in setting.amo_host:
                    asyncio.ensure_future(process_settings(setting))
            else:
                if 'chatgpt.amocrm' not in setting.amo_host:
                    asyncio.ensure_future(process_settings(setting))
            # elif os.getenv('MODE') == 'developing':
            #    if 'pickpar' in setting.amo_host:
            #        await process_settings(setting)
        # else:
        #     if 'pickpar' not in setting.amo_host:            #    if 'chatgpt.amocrm' not in setting.amo_host:
        #         asyncio.ensure_future(process_settings(setting))

        await asyncio.sleep(3)


# Run the event loop
asyncio.run(cycle())
