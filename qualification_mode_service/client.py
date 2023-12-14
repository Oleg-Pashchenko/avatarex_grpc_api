import asyncio
import grpc
from proto import qualification_pb2, qualification_pb2_grpc
import dotenv
import os

dotenv.load_dotenv()

server_host = os.getenv("SERVER_HOST") + ":50054"


async def run_qualification_client():
    async with grpc.aio.insecure_channel(server_host) as channel:
        stub = qualification_pb2_grpc.QualificationServiceStub(channel)

        # Ваш асинхронный запрос
        request = qualification_pb2.QualificationRequest(enabled=True)

        # Вызов асинхронного RPC-метода
        response = await stub.ExecuteQualification(request)

        # Вывод результата
        print(f"Success: {response.success}")
        print(f"Data: {response.data.message}")
        print(f"Execution Time: {response.execution_time} seconds")


if __name__ == '__main__':
    asyncio.run(run_qualification_client())
