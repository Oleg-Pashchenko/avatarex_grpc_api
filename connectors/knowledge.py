import json

import aiohttp


async def send_request(request):
    async with aiohttp.ClientSession() as session:
        async with session.post('http://178.253.22.162:10002/', json=request) as response:
            try:
                response_json = await response.json()
                resp = response_json['answer']
                print(response_json)
                if resp == '':
                    return '-'
                return resp

            except Exception as e:
                print(e)
                return '-'


async def get_answer(message, setting):
    print('getting answer')
    return await send_request(
        {
            "knowledge_data": setting.knowledge_data,
            "question": message.message,
            'api_token': setting.api_token,
            'model': setting.model_title,
            'use_another_models': True,
            'classification_error_message': setting.openai_error_message,
            'detecting_error_message': setting.avatarex_error_message
        }
    )