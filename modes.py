from connectors import prompt, knowledge, database, assistants
from database_connect_service.src.api import get_thread_by_lead_id, save_thread


async def prompt_mode(message, setting, fields):

    return await prompt.get_answer(message, setting, fields)


async def knowledge_mode(message, setting, fields):
    return await knowledge.get_answer(message, setting)


async def knowledge_prompt_mode(message, setting, fields):
    answer_to_sent = await knowledge.get_answer(message, setting)
    if answer_to_sent == '-':
        answer_to_sent = await prompt.get_answer(message, setting, fields)
    return answer_to_sent


async def database_prompt_mode(message, setting, fields):
    answer_to_sent = await database.get_answer(setting, message)
    if answer_to_sent == '-':
        answer_to_sent = await prompt.get_answer(message, setting, fields)
    return answer_to_sent


async def assistants_mode(message, setting, fields):
    response = await assistants.get_answer(message, setting)

    if not get_thread_by_lead_id(message['lead_id']):
        save_thread(lead_id=message['lead_id'], thread_id=response['thread_id'])
    return response['text']


modes = {
    1: prompt_mode,
    2: knowledge_mode,
    3: knowledge_prompt_mode,
    4: database_prompt_mode,
    7: assistants_mode
}
