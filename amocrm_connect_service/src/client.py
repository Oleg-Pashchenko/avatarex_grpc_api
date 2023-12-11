import grpc
from amocrm_connect_service.proto import amocrm_connect_pb2, amocrm_connect_pb2_grpc
from amocrm_connect_service.proto.amocrm_connect_pb2_grpc import AmocrmConnectServiceStub

server_host = 'localhost:50051'


# host = '178.253.22.162:50051'

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
        login=login,
        password=password,
        host=host
    )
    response = stub.GetInfo(request)
    return response


def send_message():
    channel = grpc.insecure_channel(server_host)
    stub = AmocrmConnectServiceStub(channel)

    request = amocrm_connect_pb2.SendMessageRequest(
        host="https://olegtest12.amocrm.ru/",
        email="havaisaeva19999@gmail.com",
        password="A12345mo",
        message="Ты пидор!",
        chat_hash="db1d26fc-6940-441b-bde4-b22be72c14cb"
    )

    response = stub.SendMessage(request)

    print(f"SendMessage Answer: {response.answer}")
    print(f"SendMessage Success: {response.success}")
    print(f"SendMessage Data: {response.data.message}")
    print(f"SendMessage Execution time: {response.execution} seconds")


def read_unanswered_messages():
    channel = grpc.insecure_channel(server_host)
    stub = AmocrmConnectServiceStub(channel)

    request = amocrm_connect_pb2.ReadUnansweredMessagesRequest(
        host="https://olegtest12.amocrm.ru/",
        email="havaisaeva19999@gmail.com",
        password="A12345mo",
        pipeline_id=7519106,
        stage_ids=[62333722]
    )
    print(request)
    response = stub.ReadUnansweredMessages(request)
    print(response)
    print("ReadUnansweredMessages Response:")
    for chat in response.answer:
        print(f"  Chat ID: {chat.chat_id}")
        print(f"  Message: {chat.message}")
        print(f"  Pipeline ID: {chat.pipeline_id}")
        print(f"  Lead ID: {chat.lead_id}")
        print(f"  Status ID: {chat.status_id}")
        print()


def set_field():
    pass


def get_fields_by_deal_id():
    pass


# if __name__ == '__main__':
    # try_connect()
    # get_info()
    # send_message()
    # read_unanswered_messages()
    # set field by id
    # get fields by deal id
