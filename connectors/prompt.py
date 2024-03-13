from connectors import connector
from database_connect_service.src import api
import tiktoken as tiktoken


def tokens_counter(messages: list[dict]):
    encoding = tiktoken.get_encoding('cl100k_base')
    num_tokens = 3
    for message in messages:
        num_tokens += 3
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
    return num_tokens


def get_messages_context(messages: list[dict], context: str, tokens: int, max_tokens, fields):
    tokens *= 0.95  # На всякий случай резервируем 5% в запас
    tokens -= max_tokens  # Вычитаем выделенные токены на ответ
    fields_to_view = []

    if 'fields' in fields.keys():
        for field in fields['fields']:
            fields_to_view.append({'role': 'assistant',
                                   'content': f'Какой у вас {field["name"]}?'})
            fields_to_view.append({'role': 'user', 'content': f'{field["active_value"]}'})

    fields_to_view.append({'role': 'system', 'content': context})

    system_settings = tokens_counter(fields_to_view)
    response = []
    for message in messages:
        response.append(message)
        if tokens < tokens_counter(response) + system_settings:
            response.pop(-1)
            break
    response = response[::-1]
    for f in fields_to_view:
        response.append(f)
    return response


async def get_answer(message, setting, fields, perephrase_message=None):
    if perephrase_message is not None:
        messages_context = perephrase_message
    else:
        database_messages = api.get_messages_history(message['lead_id'])
        print(setting.prompt_context)
        messages_context = get_messages_context(database_messages, setting.prompt_context, setting.model_limit,
                                                setting.max_tokens, fields if setting.use_amocrm_fields else {})

    data = {
        "prompt": messages_context[::-1],
        "model": setting.model_title,
        "max_tokens": setting.max_tokens,
        "temperature": setting.temperature,
        "api_token": setting.api_token,
        "use_another_models": True
    }

    answer = await connector.send_request(
        request=data,
        url='http://178.253.22.162:10000/'
    )
    if answer == '-':
        return 'Повторите запрос позднее!'
    return answer
