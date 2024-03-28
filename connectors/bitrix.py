import requests

from database_connect_service.src import api


async def send_message(setting, message, answer_to_sent):
    dialog_id, message_text, bot_id = message.bm.dialog_id, answer_to_sent, message.bm.bot_id
    rest_hook, client_id, message_id = setting.amo_host, message.bm.app_id, message.bm.id
    response = requests.post('http://bitrix.avatarex.tech/send-message/', data={
        'dialog_id': dialog_id,
        'message': message_text,
        'bot_id': bot_id,
        'rest_hook': rest_hook,
        'client_id': client_id,
        'message_id': message_id
    })
    api.add_message(message.id, message.lead_id, message_text, True)

    print(response.text)


async def get_fields(setting, lead_id):
    pass


async def set_fields(setting, command, lead_id):
    pass


async def move_deal(lead_id, new_stage):
    pass