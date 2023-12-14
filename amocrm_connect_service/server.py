import asyncio
import time

import grpc
from concurrent import futures
from proto import amocrm_connect_pb2, amocrm_connect_pb2_grpc
import impl


class AmocrmConnectService(amocrm_connect_pb2_grpc.AmocrmConnectServiceServicer):
    def TryConnect(self, request, context):
        start_time = time.time()
        success, error, answer = True, None, False
        try:
            self.host, self.login, self.password = (
                request.host,
                request.login,
                request.password,
            )
            amo = impl.AmoCRM(self.host, self.login, self.password)
            connection_status = amo.connect()
            if not connection_status:
                error = "Проверьте логин и пароль!"
            else:
                if not amo.is_host_supported():
                    error = "У пользователя нет доступа к указанному Host!"
                else:
                    answer = True

        except Exception as e:
            error, success = str(e), False

        response = amocrm_connect_pb2.AmocrmConnectResponse(
            answer=answer,
            success=success,
            data=amocrm_connect_pb2.Data(message=error),
            execution=round(float(time.time() - start_time), 2),
        )
        return response

    def GetInfo(self, request, context):
        print("yes")
        host, login, password = request.host, request.email, request.password
        amo = impl.AmoCRM(host, login, password)
        amo.connect()
        print("yes")
        response = amocrm_connect_pb2.GetInfoResponse(
            pipelines=amo.get_pipelines_info(), fields=amo.get_custom_fields()
        )
        return response

    async def SendMessage(self, request, context):
        success = True
        error = None
        start_time = time.time()
        try:
            host, login, password, message, chat_hash = (
                request.host,
                request.email,
                request.password,
                request.message,
                request.chat_hash,
            )
            amo = impl.AmoCRM(host, login, password)
            await amo.connect_async()
            status = await amo.send_message(message, chat_hash)
        except Exception as e:
            print(e)
            success, status, error = False, False, str(e)
        return amocrm_connect_pb2.AmocrmConnectResponse(
            answer=status,
            success=success,
            data=amocrm_connect_pb2.Data(message=error),
            execution=round(float(time.time() - start_time), 2),
        )

    async def ReadUnansweredMessages(self, request, context):
        success, error = True, None
        start_time = time.time()
        try:
            host, login, password, pipeline_id, stage_ids = (
                request.host,
                request.email,
                request.password,
                request.pipeline_id,
                list(request.stage_ids),
            )
            amo = impl.AmoCRM(host, login, password)
            status = await amo.connect_async()

            print("Connect status:", status)
            chats = await amo.get_unanswered_messages([[pipeline_id, stage_ids]])
        except Exception as e:
            success, status, error = False, False, str(e)
            chats = []
        return amocrm_connect_pb2.AmocrmReadMessagesResponse(
            answer=chats,
            success=success,
            data=amocrm_connect_pb2.Data(message=error),
            execution=round(float(time.time() - start_time), 2),
        )

    async def GetFieldsByDealId(self, request, context):
        login, password, host, deal_id = (
            request.login,
            request.password,
            request.host,
            request.deal_id,
        )
        amo = impl.AmoCRM(host, login, password)
        status = await amo.connect_async()


        return amocrm_connect_pb2.AmocrmGetFieldsResponse(
            fields=await amo.get_fields_by_deal_id(deal_id)
        )

    def SetFieldRequest(self, request, context):
        login, password, host = request.login, request.password, request.host
        field_id, value, pipeline_id = (
            request.field_id,
            request.value,
            request.pipeline_id,
        )
        deal_id = request.deal_id
        amo = impl.AmoCRM(host, login, password)
        amo.connect()
        amo.set_field_by_id(field_id, value, pipeline_id, deal_id)
        return amocrm_connect_pb2.AmocrmConnectResponse(
            answer="+", success=True, data=None, execution=0
        )


async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    amocrm_connect_pb2_grpc.add_AmocrmConnectServiceServicer_to_server(
        AmocrmConnectService(), server
    )
    server.add_insecure_port("0.0.0.0:50051")
    print("AMOCRM_CONNECT_SERVICE executed on port 50051!")
    await server.start()
    await server.wait_for_termination()


asyncio.run(serve())
