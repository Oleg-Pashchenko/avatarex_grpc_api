import grpc
from amocrm_connect_service.proto import amocrm_connect_pb2, amocrm_connect_pb2_grpc
from amocrm_connect_service.proto.amocrm_connect_pb2_grpc import AmocrmConnectServiceStub

host = 'localhost:50051'
# host = '178.253.22.162:50051'

def try_connect():
    channel = grpc.insecure_channel(host)
    stub = AmocrmConnectServiceStub(channel)

    request = amocrm_connect_pb2.AmocrmConnectRequest(
        login="havaisaeva19999@gmail.com",
        password="A12345mo",
        host="https://olegtest13.amocrm.ru/"
    )

    response = stub.TryConnect(request)

    print(f"TryConnect Answer: {response.answer}")
    print(f"TryConnect Success: {response.success}")
    print(f"TryConnect Data: {response.data.message}")
    print(f"TryConnect Execution time: {response.execution} seconds")


def get_info():
    channel = grpc.insecure_channel(host)
    stub = AmocrmConnectServiceStub(channel)

    request = amocrm_connect_pb2.GetInfoRequest(
        email="havaisaeva19999@gmail.com",
        password="A12345mo",
        host="https://olegtest13.amocrm.ru/"
    )
    response = stub.GetInfo(request)

    print("GetInfo Response:")
    for pipeline in response.pipelines:
        print(f"  Pipeline ID: {pipeline.id}")
        print(f"  Pipeline Name: {pipeline.name}")
        print(f"  Pipeline Sort: {pipeline.sort}")
        for status in pipeline.statuses:
            print(f"    Status ID: {status.id}")
            print(f"    Status Name: {status.name}")
            print(f"    Status Sort: {status.sort}")
        print()

def send_message():
    channel = grpc.insecure_channel(host)
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
    channel = grpc.insecure_channel(host)
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

if __name__ == '__main__':
    # try_connect()
    # get_info()
    # send_message()
    read_unanswered_messages()
