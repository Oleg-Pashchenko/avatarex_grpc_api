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
    fields = await amocrm_connector.get_fields(setting, session, message['lead_id'])
    need_qualification, is_first_qual = await qualification.need_qualification(setting, api.get_messages_history(
         message['lead_id']), message['answer'])
    if need_qualification:  # Если есть квалификация
        qualification_answer = await qualification.create_qualification(setting, message, fields)
        if qualification_answer['fill_command'] is not None:
            await amocrm_connector.set_fields(setting, session, qualification_answer['fill_command'], message['lead_id'])

        if is_first_qual:
            qualification_answer['qualification_status'] = True

        if qualification_answer['has_updates'] and qualification_answer['qualification_status']:
            if qualification_answer['finished']:
                await amocrm_connector.move_deal(setting, session, message['lead_id'])
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

            answer_to_sent = await prompt.get_answer(message, setting, fields, perephrase_message=q_m)
            params = "\n".join(qualification_answer["params"])
            answer_to_sent = answer_to_sent + f'\n{params}' + '\n' + qualification_answer['message']
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


async def process_settings(setting):
    st = time.time()
    tasks = []
    session = sessions.get_session(setting.amo_host)  # hard
    if session is None:
        return
    messages = await amocrm_connector.read_messages(setting, session)  # hard
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

            api.add_message(message['id'], message['lead_id'], message['answer'], False)
            tasks.append(process_message(message, setting, session))  # very hard

        except Exception as e:
            pass
    await asyncio.gather(*tasks)


async def cycle():
    print('Script started!')
    tick = 0
    while True:
        tick += 1
        print(tick)
        # if tick % 30 == 0 or tick == 1:
        settings = get_enabled_api_settings()  # Получение настроек API
        tasks = [process_settings(setting) for setting in settings]
        await asyncio.gather(*tasks)

asyncio.run(cycle())
