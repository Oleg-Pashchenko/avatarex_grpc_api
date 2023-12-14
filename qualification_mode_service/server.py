import asyncio
import grpc
from concurrent.futures import ThreadPoolExecutor
from proto.qualification_pb2 import *
from proto.qualification_pb2_grpc import QualificationServiceServicer, add_QualificationServiceServicer_to_server


class QualificationServiceImplementation(QualificationServiceServicer):
    async def ExecuteQualification(self, request, context):
        # Ваша асинхронная логика обработки запроса
        success = True
        message = "Qualification executed successfully"
        execution_time = 0.5  # Пример времени выполнения в секундах

        response = QualificationResponse(success=success, data=message, execution_time=execution_time)
        return response


async def serve():
    server = grpc.aio.server(ThreadPoolExecutor(max_workers=10))
    add_QualificationServiceServicer_to_server(QualificationServiceImplementation(), server)
    server.add_insecure_port('[::]:50054')
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(serve())
