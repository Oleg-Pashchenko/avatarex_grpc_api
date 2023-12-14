import os
import random
from concurrent import futures

import openai

from proto import whisper_pb2, whisper_pb2_grpc

import grpc
import aiohttp
import asyncio


async def download_audio_async(url, save_path):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                with open(save_path, "wb") as file:
                    while True:
                        chunk = await response.content.read(128)
                        if not chunk:
                            break
                        file.write(chunk)


async def complete_openai(openai_api_key, file_path):
    async with openai.AsyncOpenAI(api_key=openai_api_key) as client:
        audio_file = open(file_path, "rb")
        transcript = await client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, response_format="text"
        )
    return transcript


class WhisperServiceServicer(whisper_pb2_grpc.WhisperServiceServicer):
    async def VoiceToText(self, request, context):
        file_path = f"{random.randint(1000000, 100000000)}.m4a"
        await download_audio_async(request.url, file_path)
        response = await complete_openai(request.openai_api_key, file_path)
        os.remove(file_path)
        return whisper_pb2.WisperResponse(answer=response)


async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    whisper_pb2_grpc.add_WhisperServiceServicer_to_server(
        WhisperServiceServicer(), server
    )
    server.add_insecure_port("0.0.0.0:50053")
    print("WHISPER_SERVICE executed on port 50053!")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
