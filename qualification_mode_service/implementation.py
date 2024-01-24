import json
import openai


async def qualification_passed(question, field, message, openai_key):
    if field.type != 'field':
        required = ['param']
        properties = {'param': {'type': 'string', 'enum': []}}
        for f in field.possible_values:
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
    print(question, token, fields_from_amo, fields_to_fill)
    return ''

