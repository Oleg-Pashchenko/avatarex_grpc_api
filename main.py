import time

from database_connect_service.src import api
import whisper_service.client
from amocrm_connect_service import client as amocrm
from amocrm_connect_service import rest_client as rest_amo
from database_connect_service.src.api import get_thread_by_lead_id, save_thread
from database_connect_service.src.site import ApiSettings, get_enabled_api_settings
from prompt_mode_service import client as prompt_mode
from knowledge_mode_service import client as knowledge_mode
from gpts_mode_service import client as gpts
from search_mode_service import client as search
from qualification_mode_service import client as qualification
from connectors import database
import asyncio
import os


def delete_questions(message):
    result = ''
    current_word = ''

    for char in message:
        if char.isupper():
            result += current_word
            current_word = char
        elif char == '?':
            current_word = ''
        else:
            current_word += char

    return result


async def send_message_to_amocrm(setting, message, text, is_bot, is_q=False):
    try:
        st = time.time()
        message_id = await amocrm.send_message(
            setting.amo_host,
            setting.amo_email,
            setting.amo_password,
            text,
            message.chat_id,
        )
        api.add_message(message_id, message.lead_id, text, is_bot, is_q)
        api.add_stats('Crm Send', time.time() - st, message.id)
    except:
        pass


async def process_message(message, setting):
    if 'start' in message.message:
        return

    last_q = api.get_last_question_id(message.lead_id)
    print(message.message, 'обрабатывается')
    st = time.time()
    try:
        fields = await rest_amo.send_request({
            'lead_id': message.lead_id,
            'amo_host': setting.amo_host,
            'amo_email': setting.amo_email,
            'amo_password': setting.amo_password
        })
    except Exception as e:
        fields = {'all_fields': [], 'fields': []}

    api.add_stats('CRM Fields', time.time() - st, message.id)
    qualification_answer = await qualification.send_request({
        'context': setting.prompt_context,
        'user_answer': message.message,
        'token': setting.api_token,
        'amo_fields': fields,
        'avatarex_fields': setting.qualification_fields,
        'pipeline': setting.pipeline_id,
        'host': setting.amo_host,
        'email': setting.amo_email,
        'password': setting.amo_password,
        'lead_id': message.lead_id
    })
    if qualification_answer['fill_command']:
        await rest_amo.send_request(qualification_answer['fill_command'], '/fill-field')
    if qualification_answer['has_updates'] and qualification_answer['qualification_status']:
        setting.mode_id = -1
        if qualification_answer['finished']:
            await send_message_to_amocrm(setting, message, setting.qualification_finished if len(
                setting.qualification_finished) != 0 else 'Спасибо! Что вы хотели узнать?', True, True)
        else:
            params = "\n- ".join(qualification_answer["params"])

            await send_message_to_amocrm(setting, message,
                                         qualification_answer['message'] + f'\n- {params}\n', True,
                                         True)
    answer_to_sent = ''

    if not qualification_answer['qualification_status']:
        setting.mode_id = -1

    if setting.mode_id == 1:
        st = time.time()
        database_messages = api.get_messages_history(message.lead_id)
        answer = await prompt_mode.run(
            messages=prompt_mode.get_messages_context(database_messages, setting.prompt_context, setting.model_limit,
                                                      setting.max_tokens, fields if setting.use_amocrm_fields else {}),
            model=setting.model_title,
            api_token=setting.api_token,
            max_tokens=setting.max_tokens,
            temperature=setting.temperature,
        )
        api.add_stats(time.time() - st, 'Prompt mode', message.id)
        answer_to_sent = answer.data.message

    elif setting.mode_id == 4:  # Datbase mode
        print('yes')
        data = {
            'database': database,
            'question': message.message,
            'answer_format': setting.message_format,
            'positions_count': setting.repeat,
            'openai_api_key': setting.api_token,
            'classification_error_message': setting.openai_error_message,
            'detecting_error_message': setting.avatarex_error_message,
        }

        answer = await database.send_request(data)
        answer_to_sent = answer

    elif setting.mode_id == 8:  # Database + Knowledge + Prompt mode
        answer = await search.send_request({
            'database': setting.database_data,
            'search_rules': setting.search_rules,
            'message_format': setting.message_format,
            'repeat': setting.repeat,
            'question': message.message,
            'api_key': setting.api_token,
            'detecting_error_message': setting.openai_error_message,
            'classification_error_message': setting.avatarex_error_message
        })
        if answer == setting.openai_error_message or answer == setting.avatarex_error_message:
            answer = await knowledge_mode.send_request(
                {
                    "knowledge_data": setting.knowledge_data,
                    "question": message.message,
                    'api_key': setting.api_token,
                    'classification_error_message': setting.openai_error_message,
                    'detecting_error_message': setting.avatarex_error_message
                }
            )
            if answer == setting.openai_error_message or answer == setting.avatarex_error_message:
                database_messages = api.get_messages_history(message.lead_id)
                answer = await prompt_mode.run(
                    messages=prompt_mode.get_messages_context(database_messages, setting.prompt_context,
                                                              setting.model_limit,
                                                              setting.max_tokens,
                                                              fields if setting.use_amocrm_fields else {}),
                    model=setting.model_title,
                    api_token=setting.api_token,
                    max_tokens=setting.max_tokens,
                    temperature=setting.temperature,
                )
                answer = answer.data.message

        answer_to_sent = answer
    elif setting.mode_id == 7:  # Gpt's API
        thread_id = get_thread_by_lead_id(message.lead_id)
        answer = await gpts.send_request({
            'question': message.message,
            'token': setting.api_token,
            'thread_id': thread_id,
            'assistant_id': setting.assistant_id
        })
        a = answer.split('|||')
        if not thread_id:
            save_thread(lead_id=message.lead_id, thread_id=a[0])
        try:
            answer_to_sent = a[1]
        except:
            answer_to_sent = answer
    elif setting.mode_id == 3:
        if len(setting.knowledge_data) == 0:
            answer_to_sent = 'Обратитесь к поддержке. База знаний не настроена!'
        else:
            answer = await knowledge_mode.send_request(
                {
                    "knowledge_data": setting.knowledge_data,
                    "question": message.message,
                    'api_key': setting.api_token,
                    'classification_error_message': setting.openai_error_message,
                    'detecting_error_message': setting.avatarex_error_message
                }
            )
            if answer == setting.openai_error_message or answer == setting.avatarex_error_message:
                database_messages = api.get_messages_history(message.lead_id)
                answer = await prompt_mode.run(
                    messages=prompt_mode.get_messages_context(database_messages, setting.prompt_context,
                                                              setting.model_limit,
                                                              setting.max_tokens,
                                                              fields if setting.use_amocrm_fields else {}),
                    model=setting.model_title,
                    api_token=setting.api_token,
                    max_tokens=setting.max_tokens,
                    temperature=setting.temperature,
                )
                answer_to_sent = answer.data.message

    elif setting.mode_id == 2:
        if len(setting.knowledge_data) == 0:
            answer_to_sent = 'Обратитесь к поддержке. База знаний не настроена!'
        else:
            answer_to_sent = await knowledge_mode.send_request(
                {
                    "knowledge_data": setting.knowledge_data,
                    "question": message.message,
                    'api_key': setting.api_token,
                    'classification_error_message': setting.openai_error_message,
                    'detecting_error_message': setting.avatarex_error_message
                }
            )

    if not qualification_answer['qualification_status']:
        q_m = [
            {'role': 'system',
             'content': f'Переформулируй. Извините, я не понял ваш ответ. Вот возможные варианты ответа:'}]

        # without_questions_answer = delete_questions(answer_to_sent)
        answer_to_sent = await prompt_mode.run(
            messages=q_m,
            model=setting.model_title,
            api_token=setting.api_token,
            max_tokens=setting.max_tokens,
            temperature=setting.temperature,
        )
        params = "\n- ".join(qualification_answer["params"])
        answer_to_sent = answer_to_sent.data.message + f'\n- {params}'
        # without_questions_answer = without_questions_answer.data.message
        answer_to_sent = answer_to_sent + '\n' + qualification_answer['message']

    if last_q == api.get_last_question_id(message.lead_id):
        await send_message_to_amocrm(setting, message, answer_to_sent, True)
    api.add_stats('Finish time', time.time(), message.id)


async def process_settings(setting):
    st = time.time()
    messages = await amocrm.read_unanswered_messages(
        setting.amo_host,
        setting.amo_email,
        setting.amo_password,
        setting.pipeline_id,
        setting.statuses_ids,
    )
    # Список задач для параллельной обработки сообщений
    tasks = []
    for message in messages.answer:
        try:
            if api.message_exists(message.lead_id, message.id):
                continue  # Duplicate check

            if setting.manager_intervented_active and api.manager_intervened(message.lead_id, message.messages_history):
                continue  # Manager intervention check

            if ".m4a" in message.message:
                if setting.voice_detection is False:
                    continue
                message.message = await whisper_service.client.run(
                    openai_api_key=setting.api_token, url=message.message
                )
            # Assuming `api.add_message` is an asynchronous function

            #  api.create_stats(message.id, )
            api.add_stats(st, 'Start Time', message.id)
            api.add_stats(time.time() - st, 'CRM Read', message.id)
            api.add_message(message.id, message.lead_id, message.message, False)
            # Создаем задачу для асинхронной обработки сообщения
            task = process_message(message, setting)
            tasks.append(task)

        except Exception as e:
            pass
            # print(f"Error processing message: {e}")
    # Параллельное выполнение задач
    await asyncio.gather(*tasks)


async def cycle():
    while True:
        settings: list[ApiSettings] = get_enabled_api_settings()
        for setting in settings:
            # if 'https://bosswonderscakeru.amocrm.ru' in setting.amo_host:
            #     await process_settings(setting)
            #    exit(0)

            if os.getenv('MODE') == 'testing':
                if 'chatgpt.amocrm' in setting.amo_host:
                    asyncio.ensure_future(process_settings(setting))
            else:
                if 'chatgpt.amocrm' not in setting.amo_host:
                    asyncio.ensure_future(process_settings(setting))
            # elif os.getenv('MODE') == 'developing':
            #    if 'pickpar' in setting.amo_host:
            #        await process_settings(setting)
        # else:
        #     if 'pickpar' not in setting.amo_host:            #    if 'chatgpt.amocrm' not in setting.amo_host:
        #         asyncio.ensure_future(process_settings(setting))

        await asyncio.sleep(5)


# Run the event loop
asyncio.run(cycle())
