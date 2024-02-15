import time

from connectors import bitrix, prompt
from database_connect_service.src import api, sessions
from database_connect_service.src.site import ApiSettings, get_enabled_api_settings
from modes import modes
from qualification_mode_service import client as qualification
import asyncio
from connectors import amocrm as amocrm_connector


async def send_message_to_amocrm(setting, session, message, text, is_bot, is_q=False, last_q=''):
    if last_q == api.get_last_question_id(message['lead_id']):  # Если нет новых сообщений
        message_id = await amocrm_connector.send_message(setting, session, text, message['chat_id'])
        api.add_message(message_id, message['lead_id'], text, is_bot, is_q)


async def process_message(message, setting, session):
    if setting.openai_error_message == '':
        setting.openai_error_message = '-'
    if setting.avatarex_error_message == '':
        setting.avatarex_error_message = '-'
    if 'start' in message['answer']:
        return

    last_q = api.get_last_question_id(message['lead_id'])
    # fields = await amocrm_connector.get_fields(setting, session, message['lead_id'])
    fields = {}
    # need_qualification, is_first_qual = await qualification.need_qualification(setting, api.get_messages_history(
    #     message['lead_id']), message['answer'])
    need_qualification = False
    if need_qualification:  # Если есть квалификация
        qualification_answer = await qualification.create_qualification(setting, message, fields)

        if qualification_answer['fill_command']:
            await amocrm_connector.set_fields(setting, session, qualification_answer['fill_command'], 1, '3')

        if is_first_qual:
            qualification_answer['qualification_status'] = True

        if qualification_answer['has_updates'] and qualification_answer['qualification_status']:
            if qualification_answer['finished']:
                if setting.mode_id == 4:  # Database mode:
                    pass  # Sending request to him
                return await send_message_to_amocrm(setting, session, message, setting.qualification_finished if len(
                    setting.qualification_finished) != 0 else 'Спасибо! Что вы хотели узнать?', True, True, last_q)
            else:
                params = "\n".join(qualification_answer["params"])

                return await send_message_to_amocrm(setting, session, message,
                                                    qualification_answer['message'] + f'\n{params}\n', True,
                                                    True, last_q)
        if qualification_answer['has_updates']:
            q_m = [
                {'role': 'system',
                 'content': f'Переформулируй. Извините, я не понял ваш ответ. Вот возможные варианты ответа:'}]

            answer_to_sent = await prompt.get_answer(message, setting, fields)
            params = "\n".join(qualification_answer["params"])
            answer_to_sent = answer_to_sent.data.message + f'\n{params}' + '\n' + qualification_answer['message']
            return await send_message_to_amocrm(setting, session, message, answer_to_sent, True, False, last_q)

    # if 'Идет поиск' in api.get_last_activity_text(message['lead_id']):
    #    return

    # if setting.mode_id == 4:
    #      await amocrm.send_message(
    #         setting.amo_host,
    #         setting.amo_email,
    #         setting.amo_password,
    #         'Идет поиск..',
    #         message.chat_id,
    #     )
    # Если нет квалификации
    mode_function = modes.get(setting.mode_id, lambda: "Invalid Mode")
    answer_to_sent = await mode_function(message, setting, fields)
    return await send_message_to_amocrm(setting, session, message, answer_to_sent, True, False, last_q)


async def process_bitrix(message, setting):
    print('BITRIX STARTED!')
    api.add_message(message.id, message['lead_id'], message['answer'], False)
    mode_function = modes.get(setting.mode_id, lambda: "Invalid Mode")
    answer_to_sent = await mode_function(message, setting, {})
    print('BITRIX Ответ:', answer_to_sent)
    return await bitrix.send_message(setting, message, answer_to_sent)


async def process_settings(setting):
    st = time.time()
    tasks = []
    # if '-' == setting.amo_email:
    #     print('yes')
    #     setting.statuses_ids = ['NEW', 'PREPARATION']
    #     messages = get_unanswered_messages(
    #         setting.amo_host,
    #         setting.pipeline_id,
    #         setting.statuses_ids
    #     )
    #     print(messages)
    #     for message in messages:
    #         task = process_bitrix(message, setting)
    #         tasks.append(task)
    #
    #         print('BITRIX TASK!')
    session = sessions.get_session(setting.amo_host)
    if session is None:
        return
    messages = await amocrm_connector.read_messages(setting, session)
    for message in messages:
        try:
            if api.message_exists(message['lead_id'], message['id']):
                continue  # Duplicate check

            if setting.manager_intervented_active and api.manager_intervened(message['lead_id'],
                                                                             message['messages_history']):
                continue  # Manager intervention check

            # if ".m4a" in message['answer']:
            #    continue  # Voice messages detection
            # if setting.voice_detection is False:
            #     continue
            # message['answer'] = await whisper_service.client.run(
            #     openai_api_key=setting.api_token, url=message['answer']
            # )
            print('Обрабатываю', message['answer'], 'для', setting.amo_host)

            api.add_message(message['id'], message['lead_id'], message['answer'], False)
            task = process_message(message, setting, session)
            tasks.append(task)

        except Exception as e:
            print(e)
            pass
    await asyncio.gather(*tasks)


async def cycle():
    while True:
        settings: list[ApiSettings] = get_enabled_api_settings()
        start = time.time()
        for setting in settings:
            await process_settings(setting)
        print(time.time() - start)
        await asyncio.sleep(3)

asyncio.run(cycle())
