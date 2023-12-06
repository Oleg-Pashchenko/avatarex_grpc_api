import grpc
from prompt_mode_service.proto import prompt_mode_pb2
from proto import prompt_mode_pb2_grpc

def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = prompt_mode_pb2_grpc.PromptModeServiceStub(channel)

    # Создаем объект запроса
    request = prompt_mode_pb2.PromptModeRequest(
        mode_id=1,
        message="Your message",
        chat_id=123
    )

    # Отправляем запрос на сервер и получаем ответ
    response = stub.GetAnswer(request)

    # Обрабатываем ответ
    print(f"Answer: {response.answer}")
    print(f"Success: {response.success}")
    print(f"Data: {response.data.message}")
    print(f"Execution time: {response.execution} seconds")

if __name__ == '__main__':
    run()
