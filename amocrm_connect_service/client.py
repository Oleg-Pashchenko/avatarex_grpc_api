import time

import grpc

import misc
from amocrm_connect_service.proto import amocrm_connect_pb2, amocrm_connect_pb2_grpc
from amocrm_connect_service.proto.amocrm_connect_pb2_grpc import (
    AmocrmConnectServiceStub,
)
import dotenv
import os

dotenv.load_dotenv()
server_host = os.getenv("SERVER_HOST_RU") + ":50051"


def try_connect(login, password, host):
    options = [('grpc.max_receive_message_length', 14242778)]
    channel = grpc.insecure_channel(server_host, options=options)
    stub = amocrm_connect_pb2_grpc.AmocrmConnectServiceStub(channel)
    request = amocrm_connect_pb2.AmocrmConnectRequest(
        login=login, password=password, host=host
    )
    response = stub.TryConnect(request)

    if response.success is False or response.answer is False:
        return False, response.data.message
    return True, None


def get_info(login, password, host):
    options = [('grpc.max_receive_message_length', 14242778)]
    channel = grpc.insecure_channel(server_host, options=options)
    stub = AmocrmConnectServiceStub(channel)
    request = amocrm_connect_pb2.GetInfoRequest(
        email=login, password=password, host=host
    )
    response = stub.GetInfo(request)
    return response


async def send_message(host, email, password, message, chat_hash):
    options = [('grpc.max_receive_message_length', 14242778)]
    channel = grpc.aio.insecure_channel(server_host, options=options)
    stub = AmocrmConnectServiceStub(channel)
    request = amocrm_connect_pb2.SendMessageRequest(
        host=host, email=email, password=password, message=message, chat_hash=chat_hash
    )

    response = await stub.SendMessage(request)
    return response.answer


async def read_unanswered_messages(host, email, password, pipeline_id, stage_ids):
    options = [('grpc.max_receive_message_length', 14242778)]
    channel = grpc.aio.insecure_channel(server_host, options=options)
    stub = AmocrmConnectServiceStub(channel)

    request = amocrm_connect_pb2.ReadUnansweredMessagesRequest(
        host=host,
        email=email,
        password=password,
        pipeline_id=pipeline_id,
        stage_ids=stage_ids,
    )
    response = await stub.ReadUnansweredMessages(request)
    return response


def set_field():
    pass


async def get_fields_by_deal_id(deal_id, host, email, password):
    try:
        st = time.time()
        options = [('grpc.max_receive_message_length', 14242778)]

        channel = grpc.aio.insecure_channel(server_host, options=options)
        stub = AmocrmConnectServiceStub(channel)

        request = amocrm_connect_pb2.GetFieldsRequest(
            host=host, login=email, password=password, deal_id=deal_id
        )

        response = await stub.GetFieldsByDealId(request)
        return response.fields
    except:
        return []
