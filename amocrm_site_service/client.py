import grpc

from amocrm_connect_service.proto import amocrm_connect_pb2_grpc, amocrm_connect_pb2

import dotenv
import os

dotenv.load_dotenv()
server_host = os.getenv("SERVER_HOST_RU") + ":50060"


def try_connect(login, password, host):
    channel = grpc.insecure_channel(server_host)
    stub = amocrm_connect_pb2_grpc.AmocrmConnectServiceStub(channel)
    request = amocrm_connect_pb2.AmocrmConnectRequest(
        login=login,
        password=password,
        host=host
    )
    response = stub.TryConnect(request)

    if response.success is False or response.answer is False:
        return False, response.data.message
    return True, None


print(try_connect('ceo@business-robots.ru', 'cxh6pyk4TGN!mwb.vtg', 'https://chatgpt.amocrm.ru/'))
