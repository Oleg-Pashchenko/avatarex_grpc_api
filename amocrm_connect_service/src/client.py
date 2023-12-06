import grpc
from amocrm_connect_service.proto import amocrm_connect_pb2, amocrm_connect_pb2_grpc


def run():
    channel = grpc.insecure_channel('localhost:50051')
    stub = amocrm_connect_pb2_grpc.AmocrmConnectServiceStub(channel)

    # Создаем объект запроса
    request = amocrm_connect_pb2.AmocrmConnectRequest(
        login="havaisaeva19999@gmail.com",
        password="A12345mo",
        host="https://olegtest13.amocrm.ru/"
    )

    # Отправляем запрос на сервер и получаем ответ
    response = stub.TryConnect(request)

    # Обрабатываем ответ
    print(f"Answer: {response.answer}")
    print(f"Success: {response.success}")
    print(f"Data: {response.data.message}")
    print(f"Execution time: {response.execution} seconds")


if __name__ == '__main__':
    run()
