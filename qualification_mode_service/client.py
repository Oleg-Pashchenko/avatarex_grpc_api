import asyncio
import grpc
from qualification_mode_service.proto import qualification_pb2, qualification_pb2_grpc
import dotenv
import os

dotenv.load_dotenv()
server_host = os.getenv("SERVER_HOST") + ":50054"


async def run_qualification_client(text, enabled, amocrm, avatarex, finish, openai_key, model):
    async with grpc.aio.insecure_channel(server_host) as channel:
        stub = qualification_pb2_grpc.QualificationServiceStub(channel)

        # Ваш асинхронный запрос
        request = qualification_pb2.QualificationRequest(text=text,
                                                         enabled=enabled,
                                                         fields_amocrm=amocrm,
                                                         fields_avatarex=avatarex,
                                                         finish=finish,
                                                         openai_key=openai_key,
                                                         model=model
                                                         )

        # Вызов асинхронного RPC-метода
        response = await stub.ExecuteQualification(request)
        return response
