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


async def execute(question: str, token: str, fields_from_amo, fields_to_fill):
    for field_to_fill in fields_to_fill:
        if field_to_fill['enabled']:  # поле нужно заполнять
            field = None
            for field_from_amo in fields_from_amo:
                if field_from_amo['name'] == field_to_fill['name']:
                    field = fields_from_amo  # находим нужное поле
            if not field:  # если поля нет, значит его нужно заполнить, следовательно берем вопрос и возвращаем его
                await qualification_passed(question, field, )
                return field_to_fill['message']
    return ''


question = 'fds'
token = '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'
fields_from_amo = [{'id': 1265635, 'name': 'Check', 'type': 'checkbox', 'active_value': True, 'possible_values': None},
                   {'id': 1287843, 'name': 'CRM', 'type': 'select', 'active_value': 'Есть', 'possible_values': None}]
fields_to_fill = [{'qualid': 1, 'enabled': False, 'message': '', 'field_name': 'Check', 'additional_messages': []},
                  {'qualid': 2, 'enabled': False, 'message': '', 'field_name': 'Тариф', 'additional_messages': []},
                  {'qualid': 3, 'enabled': False, 'message': '', 'field_name': 'Объявление', 'additional_messages': []},
                  {'qualid': 4, 'enabled': False, 'message': '', 'field_name': 'URL объявления',
                   'additional_messages': []},
                  {'qualid': 7, 'enabled': False, 'message': '', 'field_name': 'CRM', 'additional_messages': []},
                  {'qualid': 6, 'enabled': False, 'message': '', 'field_name': 'Вид бизнеса',
                   'additional_messages': []},
                  {'qualid': 7, 'enabled': False, 'message': '', 'field_name': 'CRM', 'additional_messages': []},
                  {'qualid': 8, 'enabled': False, 'message': '', 'field_name': 'Готовность', 'additional_messages': []},
                  {'qualid': 9, 'enabled': False, 'message': '', 'field_name': 'Ссылка zoom',
                   'additional_messages': []}]
print(asyncio.run(execute(question, token, fields_from_amo, fields_to_fill)))
