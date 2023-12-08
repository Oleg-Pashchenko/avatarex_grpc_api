import asyncio
from concurrent import futures

import aiohttp
import grpc
import openai

from prompt_mode_service.proto import prompt_mode_pb2, prompt_mode_pb2_grpc


async def complete_openai(prompt, model, max_tokens, temperature, api_token):
    api_key = ''
    async with openai.AsyncOpenAI(api_key=api_key) as client:
        completion = await client.chat.completions.create(
            model='gpt-3.5-turbo',
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Как дела?"}
            ],
            max_tokens=1000,
            temperature=1
        )
        return completion.choices[0].message.content


class OpenAIPromptServicer(prompt_mode_pb2_grpc.OpenAIPromptServiceServicer):

    async def CompletePrompt(self, request, context):
        try:
            # Обработка запроса и вызов OpenAI API
            result = await complete_openai(
                "",
                request.model,
                request.max_tokens,
                request.temperature,
                request.api_token
            )

            # Формирование успешного ответа
            response_data = prompt_mode_pb2.ResponseData(
                message=result,
                error=None
            )
            return prompt_mode_pb2.OpenAIPromptResponse(
                success=True,
                data=response_data,
                execution_time=1.23  # Замените на реальное время выполнения
            )
        except Exception as e:
            # Формирование ответа при ошибке
            response_data = prompt_mode_pb2.ResponseData(
                message=None,
                error=str(e)
            )
            return prompt_mode_pb2.OpenAIPromptResponse(
                success=False,
                data=response_data,
                execution_time=0.0
            )
async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    prompt_mode_pb2_grpc.add_OpenAIPromptServiceServicer_to_server(
        OpenAIPromptServicer(), server)
    server.add_insecure_port('[::]:50051')
    await server.start()
    await server.wait_for_termination()

if __name__ == '__main__':
    asyncio.run(serve())
