import asyncio
import grpc
from concurrent.futures import ThreadPoolExecutor
from proto import qualification_pb2, qualification_pb2_grpc



class QualificationServiceImplementation(qualification_pb2_grpc.QualificationServiceServicer):
    async def ExecuteQualification(self, request, context):
        # Ваша асинхронная логика обработки запроса
        success = True
        message = "Qualification executed successfully"
        execution_time = 0.5  # Пример времени выполнения в секундах

        response = qualification_pb2.QualificationResponse(success=success, data=message, execution_time=execution_time)
        return response


async def serve():
    server = grpc.aio.server(ThreadPoolExecutor(max_workers=10))
    qualification_pb2_grpc.add_QualificationServiceServicer_to_server(QualificationServiceImplementation(), server)
    server.add_insecure_port('[::]:50054')
    await server.start()
    await server.wait_for_termination()


if __name__ == '__main__':
    asyncio.run(serve())
