import asyncio
import json
import openai


async def qualification_passed(question, field, message, openai_key):
    if field['type'] != 'field':
        required = ['param']
        properties = {'param': {'type': 'string', 'enum': []}}
        for f in field['possible_values']:
            properties['param']['enum'].append(f['value'])

    else:
        required = ['is_correct']
        properties = {'is_correct':
                          {'type': 'boolean',
                           'description': question,
                           }}
    func = [{
        "name": "Function",
        "description": "Function description",
        "parameters": {
            "type": "object",
            "properties": properties,
            'required': required
        }
    }]

    try:
        messages = [
            {'role': 'system', 'content': 'Give answer:'},
            {"role": "user",
             "content": message}]

        async with openai.AsyncOpenAI(api_key=openai_key) as client:

            response = await client.chat.completions.create(model='gpt-4',
                                                            messages=messages,
                                                            functions=func,
                                                            function_call="auto")
        response_message = response.choices[0].message
    except:
        return False
    if response_message.function_call:
        function_args = json.loads(response_message.function_call.arguments)
        if 'is_correct' in function_args:
            if function_args['is_correct'] is True:
                return True, message
            return False, ''
        else:
            return True, function_args['param']
    else:
        return False, ''


async def fill_field(pipeline, host, email, password, lead_id, field_id, value):
    import asyncio
    import aiohttp
    import json

    import dotenv
    import os

    dotenv.load_dotenv()

    server_url = 'http://' + os.getenv('SERVER_HOST_RU') + ':50050'

    async def send_request(request):
        async with aiohttp.ClientSession() as session:
            async with session.post(server_url, json=request) as response:
                response_text = await response.text()
                response_json = json.loads(response_text)
                return response_json

    await send_request(
        {'lead_id': lead_id,
         'field_id': field_id,
         'pipeline_id': pipeline,
         'value': value,
         'amo_host': host,
         'amo_email': email,
         'amo_password': password}
    )


async def execute(user_message: str, token: str, fields_from_amo, fields_to_fill, pipeline,
                  host, email, password, lead_id):
    # Проверка ответа пользователя поля
    is_filled = False
    status = True
    filled_field = ''
    for field_to_fill in fields_to_fill:
        if field_to_fill['enabled']:  # поле нужно заполнять
            fl = True
            for field_from_amo in fields_from_amo['fields']:
                if field_from_amo['name'] == field_to_fill['field_name']:
                    fl = False
                    break
            if fl:
                for f in fields_from_amo['all_fields']:
                    if f['name'] == field_to_fill['field_name']:
                        print(field_to_fill['message'], f, user_message)
                        status, result = await qualification_passed(field_to_fill['message'], f, user_message, token)
                        print(status, result)
                        if status:
                            print(f)
                            await fill_field(pipeline, host, email, password, lead_id, f['id'], result)
                        break
                break

    # Заполнение полей
    for field_to_fill in fields_to_fill:
        if field_to_fill['enabled']:  # поле нужно заполнять
            fl = True
            for field_from_amo in fields_from_amo['fields']:
                if field_from_amo['name'] == field_to_fill['field_name']:
                    fl = False
                    break
            if fl and field_to_fill['field_name'] != filled_field:
                return {
                    'qualification_status': status,
                    'finished': False,
                    'has_updates': True,
                    'message': field_to_fill['message']
                }
    if is_filled:
        return {'qualification_status': True, 'finished': True, 'has_updates': True, 'message': ''}
    return {'qualification_status': True, 'finished': True, 'has_updates': False, 'message': ''}
