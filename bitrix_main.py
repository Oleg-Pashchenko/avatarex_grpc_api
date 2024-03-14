import asyncio
import dataclasses

from database_connect_service.src import api
from database_connect_service.src.site import get_enabled_api_settings, ApiSettings, get_btx_statuses_by_id
from database_connect_service.src.bitrix import get_unanswered_messages
from connectors import bitrix, prompt
from modes import modes


async def qualification_execute(message, setting):
    last_q = api.get_last_question_id(message['lead_id'])
    # fields = await amocrm_connector.get_fields(setting, session, message['lead_id'])
    need_qualification, is_first_qual = await qualification.need_qualification(setting, api.get_messages_history(
        message['lead_id']), message['answer'])
    if need_qualification:  # Если есть квалификация
        qualification_answer = await qualification.create_qualification(setting, message, fields)
        if qualification_answer['fill_command'] is not None:
            await bitrix.set_fields(setting, qualification_answer['fill_command'], message['lead_id'])

        if is_first_qual:
            qualification_answer['qualification_status'] = True

        if qualification_answer['has_updates'] and qualification_answer['qualification_status']:
            if qualification_answer['finished']:
                await bitrix.move_deal(message['lead_id'], message['new_stage'])
                # await amocrm_connector.move_deal(setting, session, message['lead_id'])

                await bitrix.send_message(setting, message, setting.qualification_finished if len(
                    setting.qualification_finished) != 0 else 'Спасибо! Что вы хотели узнать?')
                return False
            else:
                params = "\n".join(qualification_answer["params"])
                await bitrix.send_message(setting, message, qualification_answer['message'] + f'\n{params}\n')
                return False
        if qualification_answer['has_updates']:
            q_m = [
                {'role': 'system',
                 'content': f'Переформулируй. Извините, я не понял ваш ответ. Вот возможные варианты ответа:'}]

            answer_to_sent = await prompt.get_answer(message, setting, fields, perephrase_message=q_m)
            params = "\n".join(qualification_answer["params"])
            answer_to_sent = answer_to_sent + f'\n{params}' + '\n' + qualification_answer['message']
            await bitrix.send_message(setting, message, answer_to_sent)
            return False
    return True


async def process_bitrix(message, setting):
    if message.message == 'restart':
        api.delete_messages(message.lead_id)
        return
    api.add_message(message.id, message.lead_id, message.message, False)
    # if not await qualification_execute(message, setting):
    #         return
    mode_function = modes.get(setting.mode_id, lambda: "Invalid Mode")
    answer_to_sent = await mode_function(dataclasses.asdict(message), setting, {})
    return await bitrix.send_message(setting, message, answer_to_sent)


async def process_settings(setting: ApiSettings):
    print(setting.amo_host)
    setting.statuses_ids = get_btx_statuses_by_id(setting.statuses_ids, setting.pipeline_id_id)
    #
    print(setting.statuses_ids)
    setting.statuses_ids = ['NEW', 'PREPARATION']
    messages = get_unanswered_messages(
        setting.amo_host,
        setting.pipeline_id,
        setting.statuses_ids
    )
    print(messages)
    tasks = []
    for message in messages:
        await process_bitrix(message, setting)


async def cycle():
    while True:
        tasks = []
        settings: list[ApiSettings] = get_enabled_api_settings()  # Получение настроек API
        for setting in settings:
            if setting.amo_email == '-' and setting.amo_password == '-':
                await process_settings(setting)
        #   await asyncio.gather(*tasks)
        await asyncio.sleep(3)


asyncio.run(cycle())
