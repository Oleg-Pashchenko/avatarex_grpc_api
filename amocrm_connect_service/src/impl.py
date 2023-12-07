import time

import requests

from amocrm_connect_service.proto import amocrm_connect_pb2


class AmoCRM:
    def __init__(self, host, email, password):
        self.host = host
        self.login = email
        self.password = password

    def _create_session(self):
        self.session = requests.Session()
        if '/' not in self.host[-1]:
            self.host += '/'
        if 'https://' not in self.host:
            self.host = 'https://' + self.host

        response = self.session.get(self.host)
        session_id = response.cookies.get('session_id')
        self.csrf_token = response.cookies.get('csrf_token')
        self.headers = {
            'Accept': 'application/json',
            'X-Requested-With': 'XMLHttpRequest',
            'Cookie': f'session_id={session_id}; '
                      f'csrf_token={self.csrf_token};',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/111.0.0.0 Safari/537.36'
        }

    def is_host_supported(self):
        url = 'https://www.amocrm.ru/v3/accounts'
        response = self.session.get(url)
        if response.status_code != 200:
            return False
        for account in response.json()['_embedded']['items']:
            if account['name'] in self.host:
                return True
        return False

    def connect(self) -> bool:
        self._create_session()
        response = self.session.post(f'https://www.amocrm.ru/oauth2/authorize', data={
            'csrf_token': self.csrf_token,
            'username': self.login,
            'password': self.password
        }, headers=self.headers)

        if response.status_code != 200:
            return False

        self.headers['access_token'] = response.cookies.get('access_token')
        self.headers['refresh_token'] = response.cookies.get('refresh_token')
        return True

    def get_unanswered_messages(self, search_info: list[list]):
        url = f'{self.host}ajax/v4/inbox/list'
        params = {
            'limit': 50,
            'order[sort_by]': 'first_unanswered_message_at',
            'order[sort_type]': 'desc',
            'filter[is_read][]': 'false'
        }

        for index, param in enumerate(search_info):
            params[f'filter[pipe][{param[0]}][{index}]'] = param[1]

        response = self.session.get(url=url, headers=self.headers, params=params).json()
        return response['_embedded']['talks']

    def get_pipelines_info(self):
        response = self.session.get(f'{self.host}ajax/v1/pipelines/list',
                                    headers=self.headers).json()['response']['pipelines']
        pipelines = []
        for p in response.values():
            p_id = p['id']
            p_name = p['name']
            p_sort = p['sort']
            statuses = []
            for s in p['statuses'].values():
                s_id = s['id']
                s_sort = s['sort']
                s_name = s['name']
                statuses.append(amocrm_connect_pb2.Status(id=s_id, sort=s_sort, name=s_name))
            pipelines.append(amocrm_connect_pb2.Pipeline(
                id=p_id,
                name=p_name,
                sort=p_sort,
                statuses=statuses,
                custom_fields=None
            ))
        return pipelines


