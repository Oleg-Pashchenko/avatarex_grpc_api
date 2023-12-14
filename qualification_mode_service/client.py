import asyncio
import grpc
from proto.qualification_pb2 import *
from proto.qualification_pb2_grpc import *
import dotenv
import os

dotenv.load_dotenv()

server_host = os.getenv("SERVER_HOST") + ":50054"


async def run_qualification_client():
    async with grpc.aio.insecure_channel(server_host) as channel:
        stub = QualificationServiceStub(channel)

        # Ваш асинхронный запрос
        request = QualificationRequest(enabled=True)

        # Вызов асинхронного RPC-метода
        response = await stub.ExecuteQualification(request)

        # Вывод результата
        print(f"Success: {response.success}")
        print(f"Data: {response.data.message}")
        print(f"Execution Time: {response.execution_time} seconds")


if __name__ == '__main__':
    asyncio.run(run_qualification_client())
