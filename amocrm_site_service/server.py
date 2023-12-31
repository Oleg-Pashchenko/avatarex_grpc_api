import asyncio
import time

import grpc
from concurrent import futures

import impl
from proto import amocrm_site_pb2, amocrm_site_pb2_grpc


class AmocrmConnectService(amocrm_site_pb2_grpc.AmocrmConnectServiceServicer):
    def TryConnect(self, request, context):
        start_time = time.time()
        success, error, answer = True, None, False
        try:
            self.host, self.login, self.password = (
                request.host,
                request.login,
                request.password,
            )
            print(self.host, self.login, self.login)
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
        print(answer, success)
        response = amocrm_site_pb2.AmocrmConnectResponse(
            answer=answer,
            success=success,
            data=amocrm_site_pb2.Data(message=error),
            execution=round(float(time.time() - start_time), 2),
        )
        return response

    def GetInfo(self, request, context):
        host, login, password = request.host.strip(), request.email.strip(), request.password.strip()
        print(host, login, password)
        amo = impl.AmoCRM(host, login, password)
        status = amo.connect()
        print("status", status)
        if not status:
            return amocrm_site_pb2.GetInfoResponse(
                pipelines=[], fields=[]
            )
        response = amocrm_site_pb2.GetInfoResponse(
            pipelines=amo.get_pipelines_info(), fields=amo.get_custom_fields()
        )
        return response


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    amocrm_site_pb2_grpc.add_AmocrmConnectServiceServicer_to_server(
        AmocrmConnectService(), server
    )
    server.add_insecure_port("0.0.0.0:50060")
    print("AMOCRM_CONNECT_SERVICE executed on port 50060!")
    server.start()
    server.wait_for_termination()


serve()
