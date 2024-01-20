import json
import openai


async def get_request_params_function(database: list, params: dict):
    properties = {}
    required = []
    for p in params.keys():
        en = []
        for d in database:
            if isinstance(d[p], (int, float, bool)):
                break
            else:
                en.append(d[p])

        required.append(p)
        if params[p] != '':
            if len(en) > 0:
                en.append('-')
                properties[p] = {'type': 'string', 'description': str(p), 'enum': en}
            else:
                properties[p] = {'type': 'integer', 'description': str(p)}
    return [{
        "name": "get_params",
        "description": 'Get params',
        "parameters": {
            "type": "object",
            "properties": properties,
            'required': required
        }
    }]


async def classificate(database: list, search_rules: dict, question: str, api_key: str):
    func = await get_request_params_function(database, search_rules)
    async with openai.AsyncOpenAI(api_key=api_key) as client:
        completion = await client.chat.completions.create(
            model='gpt-4',
            messages=[{'role': 'system', 'content': 'Get params'},
                      {"role": "user", "content": question}],
            functions=func,
            function_call={"name": "get_params"})
        return json.loads(completion.choices[0].message.function_call.arguments)


async def get_database_answers(database: list, search_rules: dict, classifications: dict):
    results = []
    for d in database:
        fl = True
        for s in search_rules.keys():
            if search_rules[s] == '=' and d[s] != classifications[s]:
                fl = False
                break

            elif search_rules[s] == '>=' and d[s] < classifications[s]:
                fl = False
                break

            elif search_rules[s] == '<=' and d[s] > classifications[s]:
                fl = False
                break

            elif search_rules[s] == '>' and d[s] <= classifications[s]:
                fl = False
                break

            elif search_rules[s] == '<' and d[s] >= classifications[s]:
                fl = False
                break

        if fl:
            results.append(d)
    return results


async def get_answer(answers, format, rules):
    response = ''
    for a in answers:
        resp = format
        for r in rules:
            resp = resp.replace(f'``{r}``', str(a[r]))
        response += resp + '\n'
    return response.strip()


async def run(database: list, search_rules: dict, message_format: str, repeat: int, question: str, api_key: str,
              detecting_error_message: str, classification_error_message: str):
    try:
        classifications = await classificate(database, search_rules, question, api_key)
    except:
        return detecting_error_message
    try:
        answers = await get_database_answers(database, search_rules, classifications)
        answers = answers[:repeat]
        return await get_answer(answers, message_format, search_rules)
    except:
        return classification_error_message
