import grpc
from whisper_service.proto import whisper_pb2, whisper_pb2_grpc
from whisper_service.proto.whisper_pb2_grpc import WhisperServiceStub
import os
import dotenv

dotenv.load_dotenv()

server_host = os.getenv("SERVER_HOST") + ":50053"


async def run(url, openai_api_key):
    channel = grpc.aio.insecure_channel(server_host)
    stub = WhisperServiceStub(channel)
    request = whisper_pb2.WisperRequest(url=url, openai_api_key=openai_api_key)
    response = await stub.VoiceToText(request)
    return response.answer
