import json

import openai
import dotenv
import os

dotenv.load_dotenv()
function_description = 'Ищет соотвтествующий вопрос'


async def get_classification_function(questions):
    properties = {}
    for q in questions:
        properties[q] = {'type': 'boolean',
                         'description': 'Вопрос полностью по смыслу соответствует заданному сообщению?'}

    return [{
        "name": "get_question_by_context",
        "description": function_description,
        "parameters": {
            "type": "object",
            "properties": properties,
            'required': questions
        }
    }]


async def classificate(questions: list, question: str, api_key: str):
    func = await get_classification_function(questions)
    async with openai.AsyncOpenAI(api_key=api_key) as client:
        completion = await client.chat.completions.create(
            model='gpt-4',
            messages=[{'role': 'system', 'content': function_description},
                      {"role": "user", "content": question}],
            functions=func,
            function_call={"name": "get_question_by_context"})
        return json.loads(completion.choices[0].message.function_call.arguments)


async def run(knowledge_data: dict, question: str, api_key: str, classification_error_message: str,
              detecting_error_message: str):
    print('Запустил knowledge')
    try:
        classifications = await classificate(list(knowledge_data.keys()), question, api_key)
    except:
        return detecting_error_message
    try:
        first_true_key = next(key for key, value in classifications.items() if value)
        return knowledge_data[first_true_key]
    except:
        return classification_error_message


async def test():
    response = await run(
        knowledge_data={
            'Кто ты?': 'Олег',
            'Как дела?': 'Хорошо'
        },
        question='Как у вас дела?',
        api_key=os.getenv('OPENAI_TOKEN'),
        classification_error_message='Ошибка распознавания ;(',
        detecting_error_message='Ошибка Avatarex ;('
    )
    print(response)

# asyncio.run(test())
