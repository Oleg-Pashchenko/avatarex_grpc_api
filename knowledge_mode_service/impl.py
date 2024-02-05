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
            model='gpt-4-0125-preview',
            messages=[{'role': 'system', 'content': function_description},
                      {"role": "user", "content": question}],
            functions=func,
            function_call={"name": "get_question_by_context"})
        return json.loads(completion.choices[0].message.function_call.arguments)


async def run(knowledge_data: dict, question: str, api_key: str, classification_error_message: str,
              detecting_error_message: str):
    try:
        classifications = await classificate(list(knowledge_data.keys()), question, api_key)
        print(classifications)
    except Exception as e:
        print(e, detecting_error_message)
        return detecting_error_message
    try:
        first_true_key = next(key for key, value in classifications.items() if value)
        return knowledge_data[first_true_key]
    except Exception as e:
        print(e, classification_error_message)
        return classification_error_message
