import time

from connectors import bitrix, prompt, whisper
from database_connect_service.src import api, sessions, site
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
    if ".m4a" in message['text']:
        message['text'] = await whisper.get_answer(message, setting)

    if setting.openai_error_message == '':
        setting.openai_error_message = '-'
    if setting.avatarex_error_message == '':
        setting.avatarex_error_message = '-'
    if 'start' in message['text']:
        return

    last_q = api.get_last_question_id(message['lead_id'])
    fields = await amocrm_connector.get_fields(setting, session, message['lead_id'])
    need_qualification, is_first_qual = await qualification.need_qualification(setting, api.get_messages_history(
        message['lead_id']), message['text'])
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


async def run():
    print('Script started')
    messages: list[dict] = api.get_new_messages()
    for message in messages:
        api.mark_message_as_readed(message)
        setting = site.get_setting_by_host(message['host'])
        session = sessions.get_session(message['host'])
        asyncio.create_task(process_message(message, setting, session))


asyncio.run(run())
