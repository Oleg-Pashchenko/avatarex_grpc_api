import asyncio
import grpc
from knowledge_mode_service.proto import knowledge_mode_pb2 as pb2
from knowledge_mode_service.proto import knowledge_mode_pb2_grpc as pb2_grpc


async def run_client():
    channel = grpc.aio.insecure_channel('localhost:50051')
    stub = pb2_grpc.OpenAIKnowledgeServiceStub(channel)

    # Create a sample request
    request = pb2.OpenAIKnowledgeRequest(
        message="Какой главный смысл жизни",
        rules=[
            pb2.Rule(question="В чем смысл жизни?", answer="42"),
            pb2.Rule(question="Сколько лет Олегу Пащенко?", answer="Он вечно молод")
               ],
        openai_settings=pb2.OpenAISettings(model="text-davinci-003", max_tokens=50, temperature=0.7,
                                           api_token="your_api_token")
    )

    # Make an asynchronous RPC call
    response = await stub.CompleteKnowledge(request)
    print(f"Server Response: {response}")


if __name__ == '__main__':
    asyncio.run(run_client())
