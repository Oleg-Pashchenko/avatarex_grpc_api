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
    print("Prompt mode:", round(response.execution_time, 2))
    return response


import tiktoken as tiktoken


def tokens_counter(messages: list[dict]):
    encoding = tiktoken.get_encoding('cl100k_base')
    num_tokens = 3
    for message in messages:
        num_tokens += 3
        for key, value in message.items():
            num_tokens += len(encoding.encode(value))
    return num_tokens


def get_messages_context(messages: list[dict], context: str, tokens: int, max_tokens, fields):
    tokens *= 0.95  # На всякий случай резервируем 5% в запас
    tokens -= max_tokens  # Вычитаем выделенные токены на ответ
    messages.reverse()
    fields_to_view = []
    for field in fields:
        fields_to_view.append({'role': 'system',
                               'content': f'Если у тебя спрашивают о {field.name} отвечай про {field.active_value} и больше ничего'})

    fields_to_view.append({'role': 'system', 'content': context})

    system_settings = tokens_counter(fields_to_view)
    response = []
    for message in messages:
        response.append(message)
        if tokens < tokens_counter(response) + system_settings:
            response.pop(-1)
            break
    for f in fields_to_view:
        response.append(f)

    return response
