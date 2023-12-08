import grpc
import asyncio
import time
from prompt_mode_service.proto import prompt_mode_pb2, prompt_mode_pb2_grpc


async def query_and_print_result(index, request, stub, result_queue):
    start_time = time.time()
    response = await stub.CompletePrompt(request)
    end_time = time.time()

    if response.success:
        # print(f"Query {index + 1}: Success! Time: {end_time - start_time:.2f} seconds")
        await result_queue.put((index, response))
    else:
        pass
        # print(f"Query {index + 1}: Error - {response.data.error}")


async def run():
    async with grpc.aio.insecure_channel('localhost:50051') as channel:
        stub = prompt_mode_pb2_grpc.OpenAIPromptServiceStub(channel)

        total_start_time = time.time()
        n = 100
        result_queue = asyncio.Queue()

        # Одновременная отправка 50 запросов
        tasks = [
            query_and_print_result(i, prompt_mode_pb2.OpenAIPromptRequest(
                messages=[
                    prompt_mode_pb2.Message(role=prompt_mode_pb2.Message.USER, content=f"Question {i + 1}"),
                    prompt_mode_pb2.Message(role=prompt_mode_pb2.Message.ASSISTANT,
                                            content="Be precise and concise."),
                    prompt_mode_pb2.Message(role=prompt_mode_pb2.Message.SYSTEM, content="Be precise and concise.")
                ],
                model="название модели",
                max_tokens=1000,
                temperature=1.0,
                api_token="blablabla"
            ), stub, result_queue) for i in range(n)
        ]

        # Ожидание завершения всех задач
        await asyncio.gather(*tasks)

        # Получение результатов в порядке их прихода
        results = []
        for _ in range(n):
            index, response = await result_queue.get()
            results.append((index, response))

        # Вывод результатов в порядке
        results.sort(key=lambda x: x[0])
        for index, response in results:
            # print(f"Query {index + 1} result: {response.data.message}")
            pass
        total_end_time = time.time()
        total_execution_time = total_end_time - total_start_time
        print(f"\nTotal Execution Time for 500 queries: {total_execution_time:.2f} seconds")
        print(f"Average Query Time: {total_execution_time / n:.2f} seconds")


if __name__ == '__main__':
    asyncio.run(run())
