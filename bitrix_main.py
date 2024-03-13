import asyncio
import dataclasses

from database_connect_service.src import api
from database_connect_service.src.site import get_enabled_api_settings, ApiSettings, get_btx_statuses_by_id
from database_connect_service.src.bitrix import get_unanswered_messages
from connectors import bitrix
from modes import modes


async def process_bitrix(message, setting):
    api.add_message(message.id, message.lead_id, message.message, False)
    mode_function = modes.get(setting.mode_id, lambda: "Invalid Mode")
    answer_to_sent = await mode_function(dataclasses.asdict(message), setting, {})
    return await bitrix.send_message(setting, message, answer_to_sent)


async def process_settings(setting: ApiSettings):
    print(setting.amo_host)
    setting.statuses_ids = get_btx_statuses_by_id(setting.id)
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
