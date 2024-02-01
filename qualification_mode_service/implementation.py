async def qualification_passed_triggers(context, question, field, message, openai_key):
    for f in field['possible_values']:
        if f['value'].lower() in message.lower():
            return True, f['value']
    return False, ''


def get_params(amo, param):
    print(amo, param)
    return []


async def execute(context, user_message: str, token: str, fields_from_amo, fields_to_fill, pipeline,
                  host, email, password, lead_id):
    is_filled = False
    status = True
    fill_command = None
    filled_field = ''
    print(fields_from_amo, fields_to_fill)
    for field_to_fill in fields_to_fill:
        if field_to_fill['enabled']:
            fl = any(
                field_from_amo['name'] == field_to_fill['field_name'] for field_from_amo in fields_from_amo['fields'])
            if not fl:
                for f in fields_from_amo['all_fields']:
                    if f['name'] == field_to_fill['field_name']:
                        status, result = await qualification_passed_triggers(context, field_to_fill['message'], f,
                                                                             user_message, token)
                        if status:
                            if f['type'] != 'field':
                                result = next(
                                    v['id'] for v in f['possible_values'] if v['value'].lower() == result.lower())
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

    for field_to_fill in fields_to_fill:
        if field_to_fill['enabled'] and field_to_fill['field_name'] != filled_field:
            return {
                'qualification_status': status,
                'finished': False,
                'has_updates': True,
                'message': field_to_fill['message'],
                'fill_command': fill_command,
                'params': get_params(fields_from_amo, field_to_fill)
            }

    if is_filled:
        return {'qualification_status': True, 'finished': True, 'has_updates': True, 'message': '',
                'fill_command': fill_command, 'params': []}
    return {'qualification_status': True, 'finished': True, 'has_updates': False, 'message': '',
            'fill_command': fill_command, 'params': []}
