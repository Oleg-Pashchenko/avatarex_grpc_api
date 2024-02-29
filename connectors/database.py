from connectors import connector


async def get_answer(setting, message):
    data = {
        'database': setting.database_data,
        'question': message['text'],
        'answer_format': setting.message_format,
        'positions_count': setting.repeat,
        'openai_api_key': setting.api_token,
        'classification_error_message': setting.openai_error_message,
        'detecting_error_message': setting.avatarex_error_message,
    }

    return await connector.send_request(
        request=data,
        url='http://178.253.22.162:11111/'
    )
