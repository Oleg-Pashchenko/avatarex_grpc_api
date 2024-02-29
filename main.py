import time

from connectors import bitrix, prompt, whisper
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
            await amocrm_connector.set_fields(setting, session, qualification_answer['fill_command'],
                                              message['lead_id'])

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


def is_time_between(start_time_str, end_time_str):
    from datetime import datetime

    # Получаем текущее время
    import pytz

    moscow_tz = pytz.timezone('Europe/Moscow')
    now = datetime.now(moscow_tz).time()
    # Преобразуем строки времени в объекты времени
    start_time = datetime.strptime(start_time_str, "%H:%M").time()
    end_time = datetime.strptime(end_time_str, "%H:%M").time()
    # Проверяем, находится ли текущее время между заданными временами
    if start_time <= end_time:
        return start_time <= now <= end_time
    else:
        # Если время начала больше времени окончания, проверяем два условия
        return start_time <= now or now <= end_time


async def process_settings(setting: ApiSettings):
    try:
        st = time.time()
        tasks = []

        if setting.is_date_work_active and not is_time_between(setting.datetimeValueStart, setting.datetimeValueFinish):
            return
        session = sessions.get_session(setting.amo_host)  # hard
        if session is None:
            return
        messages = await amocrm_connector.read_messages(setting, session)  # hard
        for message in messages:
            try:
                if api.message_exists(message['lead_id'], message['id']):
                    continue  # Duplicate check

                if setting.manager_intervented_active is True and api.manager_intervened(message['lead_id'],
                                                                                 message['messages_history']):
                    continue  # Manager intervention check

                if setting.voice_detection is False and ".m4a" in message['answer']:
                    continue

                if ".m4a" in message['answer']:
                    print('gc')
                    message['answer'] = await whisper.get_answer(message, setting)
                    print('gc', message['answer'])

                api.add_message(message['id'], message['lead_id'], message['answer'], False)
                tasks.append(process_message(message, setting, session))  # very hard

            except Exception as e:
                pass
        await asyncio.gather(*tasks)
    except Exception as e:
        print(setting.amo_host, e)


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
