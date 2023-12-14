import grpc
from amocrm_connect_service.proto import amocrm_connect_pb2, amocrm_connect_pb2_grpc
from amocrm_connect_service.proto.amocrm_connect_pb2_grpc import AmocrmConnectServiceStub

server_host = 'localhost:50051'


# server_host = '178.253.22.162:50051'

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


def get_info(login, password, host):
    channel = grpc.insecure_channel(server_host)
    stub = AmocrmConnectServiceStub(channel)
    request = amocrm_connect_pb2.GetInfoRequest(
        email=login,
        password=password,
        host=host
    )
    response = stub.GetInfo(request)
    return response


async def send_message(host, email, password, message, chat_hash):
    channel = grpc.aio.insecure_channel(server_host)
    stub = AmocrmConnectServiceStub(channel)

    request = amocrm_connect_pb2.SendMessageRequest(
        host=host,
        email=email,
        password=password,
        message=message,
        chat_hash=chat_hash
    )

    response = await stub.SendMessage(request)
    print(f"SendMessage Execution time: {round(response.execution, 2)} seconds")


async def read_unanswered_messages(host, email, password, pipeline_id, stage_ids):
    channel = grpc.aio.insecure_channel(server_host)
    stub = AmocrmConnectServiceStub(channel)

    request = amocrm_connect_pb2.ReadUnansweredMessagesRequest(
        host=host,
        email=email,
        password=password,
        pipeline_id=pipeline_id,
        stage_ids=stage_ids
    )
    response = await stub.ReadUnansweredMessages(request)
    print('Amocrm Read Unanswered Execution Time: ', round(response.execution, 2))
    return response


def set_field():
    pass


def get_fields_by_deal_id():
    pass


host = "https://olegtest12.amocrm.ru/"
email = "havaisaeva19999@gmail.com"
password = "A12345mo"

# print(get_info(email, password, host))
# if __name__ == '__main__':
# try_connect()
# get_info()
# send_message()
# read_unanswered_messages()
# set field by id
# get fields by deal id
