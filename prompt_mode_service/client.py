import grpc
import asyncio
import time

import misc
from prompt_mode_service.proto import prompt_mode_pb2, prompt_mode_pb2_grpc
from prompt_mode_service.proto.prompt_mode_pb2_grpc import OpenAIPromptServiceStub
import dotenv
import os

dotenv.load_dotenv()

server_host = os.getenv("SERVER_HOST_EN") + ":50052"


async def run(messages, model, max_tokens, temperature, api_token):
    channel = grpc.aio.insecure_channel(server_host)
    stub = OpenAIPromptServiceStub(channel)

    grpc_messages = []
    for message in messages[::-1]:
        if message["role"] == "user":
            grpc_messages.append(
                prompt_mode_pb2.Message(
                    content=message["content"], role=prompt_mode_pb2.Message.USER
                )
            )

        elif message["role"] == "assistant":
            grpc_messages.append(
                prompt_mode_pb2.Message(
                    content=message["content"], role=prompt_mode_pb2.Message.ASSISTANT
                )
            )
        else:
            grpc_messages.append(
                prompt_mode_pb2.Message(
                    content=message["content"], role=prompt_mode_pb2.Message.SYSTEM
                )
            )
    request = prompt_mode_pb2.OpenAIPromptRequest(
        messages=grpc_messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        api_token=api_token,
    )
    response = await stub.CompletePrompt(request)
    return response


