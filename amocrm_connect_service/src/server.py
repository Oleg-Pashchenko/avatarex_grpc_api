import time

import grpc
from concurrent import futures
from amocrm_connect_service.proto import amocrm_connect_pb2, amocrm_connect_pb2_grpc

import requests


class AmocrmConnectService(amocrm_connect_pb2_grpc.AmocrmConnectServiceServicer):
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

    def TryConnect(self, request, context):
        start_time = time.time()
        success, error, answer = True, None, False
        try:
            self.host, self.login, self.password = request.host, request.login, request.password
            connection_status = self.connect()
            if not connection_status:
                error = 'Проверьте логин и пароль!'
            else:
                if not self.is_host_supported():
                    error = 'У пользователя нет доступа к указанному Host!'
                else:
                    answer = True

        except Exception as e:
            error, success = str(e), False

        response = amocrm_connect_pb2.AmocrmConnectResponse(
            answer=answer,
            success=success,
            data=amocrm_connect_pb2.Data(message=error),
            execution=round(float(time.time() - start_time), 2)
        )
        return response

    def GetInfo(self, request, context):
        print(request.avatarex_amocrm_id)
        pipelines = [
            amocrm_connect_pb2.Pipeline(
                id=111,
                name="test",
                sort=100,
                statuses=[amocrm_connect_pb2.Status(id=111, sort=100, name="Этап")],
                custom_fields=amocrm_connect_pb2.CustomFields(
                    leads=[amocrm_connect_pb2.LeadCustomField(
                        type="select",
                        id=11111,
                        name="22222",
                        options=[amocrm_connect_pb2.Option(id=111, name="123")]
                    )]
                )
            )
        ]
        response = amocrm_connect_pb2.GetInfoResponse(pipelines=pipelines)
        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    amocrm_connect_pb2_grpc.add_AmocrmConnectServiceServicer_to_server(AmocrmConnectService(), server)
    amocrm_connect_pb2_grpc.add_AmocrmGetInfoServiceServicer_to_server(AmocrmConnectService(), server)
    server.add_insecure_port('0.0.0.0:50051')
    print('Server is running on port 50051...')
    server.start()
    server.wait_for_termination()


serve()
