import asyncio
import json
import openai


async def qualification_passed(question, field, message, openai_key):
    """
    Какой у вас тариф?
    {'id': 1278951, 'name': 'Тариф', 'type': 'select', 'active_value': None,
     'possible_values': [{'id': 744363, 'value': 'Профи', 'sort': 500},
      {'id': 744365, 'value': 'Бизнес', 'sort': 1},
       {'id': 744367, 'value': 'Приват', 'sort': 2}]}
     профи

    """

    if field['type'] != 'field':
        required = ['param']
        properties = {'param': {'type': 'string', 'enum': []}}
        for f in field['possible_values']:
            properties['param']['enum'].append(f['value'])

    else:
        required = []
        properties = {}
    func = [{
        "name": "Function",
        "description": "Выведи вариант ответа с которым совпадает вопрос. Если нет совпадения - ничего не выводи",
        "parameters": {
            "type": "object",
            "properties": properties,
            'required': required
        }
    }]

    try:
        messages = [
            {'role': 'system',
             'content': 'Выведи вариант ответа с которым совпадает вопрос. Если нет совпадения - ничего не выводи'},
            {"role": "user",
             "content": message}]

        async with openai.AsyncOpenAI(api_key=openai_key) as client:

            response = await client.chat.completions.create(model='gpt-3.5-turbo',
                                                            messages=messages,
                                                            functions=func,
                                                            function_call="auto")
        response_message = response.choices[0].message
        print(response_message)
    except Exception as e:
        print(e)
        return False
    if response_message.function_call:
        function_args = json.loads(response_message.function_call.arguments)
        print(function_args)
        if 'is_correct' in function_args:
            if function_args['is_correct'] is True:
                return True, message
            return False, ''
        else:
            return True, function_args['param']
    else:
        return False, ''


async def execute(user_message: str, token: str, fields_from_amo, fields_to_fill, pipeline,
                  host, email, password, lead_id):
    # Проверка ответа пользователя поля
    is_filled = False
    status = True
    fill_command = None
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
                            if f['type'] != 'field':
                                for v in f['possible_values']:
                                    if v['value'].lower() == result.lower():
                                        result = v['id']
                                        break
                            is_filled = True
                            filled_field = f['name']
                            fill_command = {'lead_id': lead_id,
                                            'field_id': f['id'],
                                            'pipeline_id': pipeline,
                                            'value': result,
                                            'amo_host': host,
                                            'amo_email': email,
                                            'amo_password': password}

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
                    'message': field_to_fill['message'],
                    'fill_command': fill_command
                }
    if is_filled:
        return {'qualification_status': True, 'finished': True, 'has_updates': True, 'message': '',
                'fill_command': fill_command}
    return {'qualification_status': True, 'finished': True, 'has_updates': False, 'message': '',
            'fill_command': fill_command
            }