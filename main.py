import time

from database_connect_service.src import api
import whisper_service.client
from amocrm_connect_service import client as amocrm
from amocrm_connect_service import rest_client as rest_amo
from database_connect_service.src.site import ApiSettings, get_enabled_api_settings
from modes import modes
from prompt_mode_service import client as prompt_mode
from qualification_mode_service import client as qualification
import asyncio
import os


async def get_fields(message, setting):
    try:
        fields = await rest_amo.send_request({
            'lead_id': message.lead_id,
            'amo_host': setting.amo_host,
            'amo_email': setting.amo_email,
            'amo_password': setting.amo_password
        })
    except Exception as e:
        fields = {'all_fields': [], 'fields': []}
    return fields


async def send_message_to_amocrm(setting, message, text, is_bot, is_q=False):
    try:
        st = time.time()
        message_id = await amocrm.send_message(
            setting.amo_host,
            setting.amo_email,
            setting.amo_password,
            text,
            message.chat_id,
        )
        api.add_message(message_id, message.lead_id, text, is_bot, is_q)
        api.add_stats('Crm Send', time.time() - st, message.id)
    except:
        pass


async def process_message(message, setting):
    if setting.openai_error_message == '':
        setting.openai_error_message = '-'
    if setting.avatarex_error_message == '':
        setting.avatarex_error_message = '-'
    if 'start' in message.message:
        return

    last_q = api.get_last_question_id(message.lead_id)
    fields = await get_fields(message, setting)
    need_qualification = await qualification.need_qualification(setting, api.get_messages_history(message.lead_id))

    if need_qualification:  # Если есть квалификация
        qualification_answer = await qualification.create_qualification(setting, message, fields)

        if qualification_answer['fill_command']:
            await rest_amo.send_request(qualification_answer['fill_command'], '/fill-field')
        if qualification_answer['has_updates'] and qualification_answer['qualification_status']:
            if qualification_answer['finished']:
                return await send_message_to_amocrm(setting, message, setting.qualification_finished if len(
                    setting.qualification_finished) != 0 else 'Спасибо! Что вы хотели узнать?', True, True)
            else:
                params = "\n- ".join(qualification_answer["params"])

                return await send_message_to_amocrm(setting, message,
                                                    qualification_answer['message'] + f'\n- {params}\n', True,
                                                    True)

        q_m = [
            {'role': 'system',
             'content': f'Переформулируй. Извините, я не понял ваш ответ. Вот возможные варианты ответа:'}]

        answer_to_sent = await prompt_mode.run(
            messages=q_m,
            model=setting.model_title,
            api_token=setting.api_token,
            max_tokens=setting.max_tokens,
            temperature=setting.temperature,
        )
        params = "\n".join(qualification_answer["params"])
        answer_to_sent = answer_to_sent.data.message + f'\n{params}' + '\n' + qualification_answer['message']
        return await send_message_to_amocrm(setting, message, answer_to_sent, True)

    else:  # Если нет квалификации
        mode_function = modes.get(setting.mode_id, lambda: "Invalid Mode")
        answer_to_sent = await mode_function(message, setting, fields)
        if last_q == api.get_last_question_id(message.lead_id):  # Если нет новых сообщений
            return await send_message_to_amocrm(setting, message, answer_to_sent, True)


async def process_settings(setting):
    st = time.time()
    messages = await amocrm.read_unanswered_messages(
        setting.amo_host,
        setting.amo_email,
        setting.amo_password,
        setting.pipeline_id,
        setting.statuses_ids,
    )
    tasks = []
    for message in messages.answer:
        try:
            if api.message_exists(message.lead_id, message.id):
                continue  # Duplicate check

            if setting.manager_intervented_active and api.manager_intervened(message.lead_id, message.messages_history):
                continue  # Manager intervention check

            if ".m4a" in message.message:
                if setting.voice_detection is False:
                    continue
                message.message = await whisper_service.client.run(
                    openai_api_key=setting.api_token, url=message.message
                )
            api.add_message(message.id, message.lead_id, message.message, False)
            task = process_message(message, setting)
            tasks.append(task)

        except Exception as e:
            pass
    await asyncio.gather(*tasks)


async def cycle():
    while True:
        settings: list[ApiSettings] = get_enabled_api_settings()
        for setting in settings:
            if os.getenv('MODE') == 'testing':
                if 'chatgpt.amocrm' in setting.amo_host:
                    asyncio.ensure_future(process_settings(setting))
            else:
                if 'chatgpt.amocrm' not in setting.amo_host:
                    asyncio.ensure_future(process_settings(setting))
        await asyncio.sleep(5)


# Run the event loop
asyncio.run(cycle())
