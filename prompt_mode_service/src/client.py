import grpc
import asyncio
import time
from prompt_mode_service.proto import prompt_mode_pb2, prompt_mode_pb2_grpc
from prompt_mode_service.proto.prompt_mode_pb2_grpc import OpenAIPromptServiceStub

server_host = 'localhost:50052'
server_host = '178.253.22.162:50051'


async def run(messages, model, max_tokens, temperature, api_token):
    channel = grpc.aio.insecure_channel('localhost:50052')
    stub = OpenAIPromptServiceStub(channel)

    grpc_messages = []
    for message in messages:
        if message['role'] == 'user':
            grpc_messages.append(
                prompt_mode_pb2.Message(content=message['content'], role=prompt_mode_pb2.Message.USER))

        elif message['role'] == 'assistant':
            grpc_messages.append(
                prompt_mode_pb2.Message(content=message['content'], role=prompt_mode_pb2.Message.ASSISTANT))
        else:
            grpc_messages.append(
                prompt_mode_pb2.Message(content=message['content'], role=prompt_mode_pb2.Message.SYSTEM))

    request = prompt_mode_pb2.OpenAIPromptRequest(
        messages=grpc_messages,
        model=model,
        max_tokens=max_tokens,
        temperature=temperature,
        api_token=api_token
    )
    response = await stub.CompletePrompt(request)
    return response

