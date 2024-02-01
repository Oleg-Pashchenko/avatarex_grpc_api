import asyncio
import time
from concurrent import futures

import aiohttp
import grpc
import openai

from proto import prompt_mode_pb2, prompt_mode_pb2_grpc


async def complete_openai(prompt, model, max_tokens, temperature, api_token):
    try:
        async with openai.AsyncOpenAI(api_key=api_token) as client:
            completion = await client.chat.completions.create(
                model=model, messages=prompt, max_tokens=max_tokens, temperature=temperature
            )
            return completion.choices[0].message.content
    except:
        for model in ['gpt-3.5-turbo', 'gpt-4', 'gpt-4-32k']:
            try:
                async with openai.AsyncOpenAI(api_key=api_token) as client:
                    completion = await client.chat.completions.create(
                        model=model, messages=prompt, max_tokens=max_tokens, temperature=temperature
                    )
                    return completion.choices[0].message.content
            except Exception as e:
                pass

class OpenAIPromptServicer(prompt_mode_pb2_grpc.OpenAIPromptServiceServicer):
    async def CompletePrompt(self, request, context):
        start = time.time()
        try:
            json_messages = []
            messages = request.messages
            for message in messages:
                if message.role == prompt_mode_pb2.Message.USER:
                    json_messages.append({"role": "user", "content": message.content})
                elif message.role == prompt_mode_pb2.Message.ASSISTANT:
                    json_messages.append(
                        {"role": "assistant", "content": message.content}
                    )
                else:
                    json_messages.append({"role": "system", "content": message.content})
            # Обработка запроса и вызов OpenAI API
            result = await complete_openai(
                json_messages,
                request.model,
                request.max_tokens,
                request.temperature,
                request.api_token,
            )
            # Формирование успешного ответа
            response_data = prompt_mode_pb2.ResponseData(message=result, error=None)
            return prompt_mode_pb2.OpenAIPromptResponse(
                success=True,
                data=response_data,
                execution_time=round(time.time() - start),  # Замените на реальное время выполнения
            )
        except Exception as e:
            # Формирование ответа при ошибке
            response_data = prompt_mode_pb2.ResponseData(message=None, error=str(e))
            return prompt_mode_pb2.OpenAIPromptResponse(
                success=False, data=response_data, execution_time=0.0
            )


async def serve():
    server = grpc.aio.server(futures.ThreadPoolExecutor(max_workers=10))
    prompt_mode_pb2_grpc.add_OpenAIPromptServiceServicer_to_server(
        OpenAIPromptServicer(), server
    )
    server.add_insecure_port("0.0.0.0:50052")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(serve())
