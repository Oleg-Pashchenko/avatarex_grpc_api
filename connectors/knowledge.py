import json

from connectors import connector


async def get_answer(message, setting):
    print('Mode 2: Knowledge')
    if len(setting.knowledge_data) == 0:
        return 'Обратитесь к поддержке. База знаний не настроена!'
    else:
        return await connector.send_request(
            request={
                "knowledge_data": setting.knowledge_data,
                "question": message['text'],
                'api_token': setting.api_token,
                'model': setting.model_title,
                'use_another_models': True,
                'classification_error_message': setting.openai_error_message,
                'detecting_error_message': setting.avatarex_error_message
            },
            url='http://178.253.22.162:10002/'
        )
