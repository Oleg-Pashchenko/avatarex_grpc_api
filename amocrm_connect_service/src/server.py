import time

import grpc
from concurrent import futures
from amocrm_connect_service.proto import amocrm_connect_pb2, amocrm_connect_pb2_grpc
from amocrm_connect_service.src import impl


class AmocrmConnectService(amocrm_connect_pb2_grpc.AmocrmConnectServiceServicer):

    def TryConnect(self, request, context):
        start_time = time.time()
        success, error, answer = True, None, False
        try:
            self.host, self.login, self.password = request.host, request.login, request.password
            amo = impl.AmoCRM(self.host, self.login, self.password)
            connection_status = amo.connect()
            if not connection_status:
                error = 'Проверьте логин и пароль!'
            else:
                if not amo.is_host_supported():
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
        host, login, password = request.host, request.email, request.password
        amo = impl.AmoCRM(host, login, password)
        amo.connect()
        pipelines = amo.get_pipelines_info()
        response = amocrm_connect_pb2.GetInfoResponse(pipelines=pipelines)
        return response

    def SendMessage(self, request, context):
        success = True
        error = None
        start_time = time.time()
        try:
            host, login, password, message, chat_hash = request.host, request.email, request.password, request.message, request.chat_hash
            amo = impl.AmoCRM(host, login, password)
            amo.connect()
            status = amo.send_message(message, chat_hash)
        except Exception as e:
            success, status, error = False, False, str(e)
        return amocrm_connect_pb2.AmocrmConnectResponse(
            answer=status,
            success=success,
            data=amocrm_connect_pb2.Data(message=error),
            execution=round(float(time.time() - start_time), 2)
        )

    def ReadUnansweredMessages(self, request, context):
        success, error = True, None
        start_time = time.time()
        try:
            host, login, password, pipeline_id, stage_ids = request.host, request.email, request.password, request.pipeline_id, list(request.stage_ids)
            amo = impl.AmoCRM(host, login, password)
            amo.connect()
            chats = amo.get_unanswered_messages([[pipeline_id, stage_ids]])
        except Exception as e:
            success, status, error = False, False, str(e)
            chats = []
        return amocrm_connect_pb2.AmocrmReadMessagesResponse(
            answer=chats,
            success=success,
            data=amocrm_connect_pb2.Data(message=error),
            execution=round(float(time.time() - start_time), 2)
        )


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    amocrm_connect_pb2_grpc.add_AmocrmConnectServiceServicer_to_server(AmocrmConnectService(), server)
    amocrm_connect_pb2_grpc.add_AmocrmConnectServiceServicer_to_server(AmocrmConnectService(), server)
    server.add_insecure_port('0.0.0.0:50051')
    print('Server is running on port 50051...')
    server.start()
    server.wait_for_termination()


serve()
