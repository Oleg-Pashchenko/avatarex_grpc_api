import time

import grpc
from amocrm_connect_service.proto import amocrm_connect_pb2, amocrm_connect_pb2_grpc
from amocrm_connect_service.proto.amocrm_connect_pb2_grpc import (
    AmocrmConnectServiceStub,
)
import dotenv
import os

dotenv.load_dotenv()
server_host = os.getenv("SERVER_HOST") + ":50051"


def try_connect(login, password, host):
    channel = grpc.insecure_channel(server_host)
    stub = amocrm_connect_pb2_grpc.AmocrmConnectServiceStub(channel)
    request = amocrm_connect_pb2.AmocrmConnectRequest(
        login=login, password=password, host=host
    )
    response = stub.TryConnect(request)

    if response.success is False or response.answer is False:
        return False, response.data.message
    return True, None


def get_info(login, password, host):
    channel = grpc.insecure_channel(server_host)
    stub = AmocrmConnectServiceStub(channel)
    request = amocrm_connect_pb2.GetInfoRequest(
        email=login, password=password, host=host
    )
    response = stub.GetInfo(request)
    return response


async def send_message(host, email, password, message, chat_hash):
    channel = grpc.aio.insecure_channel(server_host)
    stub = AmocrmConnectServiceStub(channel)
    print(host, email, password, message, chat_hash)
    request = amocrm_connect_pb2.SendMessageRequest(
        host=host, email=email, password=password, message=message, chat_hash=chat_hash
    )

    response = await stub.SendMessage(request)
    print(f"SendMessage Execution time: {round(response.execution, 2)} seconds")
    return response.answer


async def read_unanswered_messages(host, email, password, pipeline_id, stage_ids):
    channel = grpc.aio.insecure_channel(server_host)
    stub = AmocrmConnectServiceStub(channel)

    request = amocrm_connect_pb2.ReadUnansweredMessagesRequest(
        host=host,
        email=email,
        password=password,
        pipeline_id=pipeline_id,
        stage_ids=stage_ids,
    )
    response = await stub.ReadUnansweredMessages(request)
    print("Amocrm Read Unanswered Execution Time: ", round(response.execution, 2))
    return response


def set_field():
    pass


async def get_fields_by_deal_id(deal_id, host, email, password):
    st = time.time()
    channel = grpc.aio.insecure_channel(server_host)
    stub = AmocrmConnectServiceStub(channel)

    request = amocrm_connect_pb2.GetFieldsRequest(
        host=host, login=email, password=password, deal_id=deal_id
    )

    response = await stub.GetFieldsByDealId(request)
    print(f"GetFieldsByDealId Execution time: {round(time.time() - st, 2)} seconds")
    return response.fields
