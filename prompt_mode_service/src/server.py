import grpc
from concurrent import futures
import prompt_mode_pb2
import prompt_mode_pb2_grpc

class PromptModeService(prompt_mode_pb2_grpc.PromptModeServiceServicer):
    def GetAnswer(self, request, context):
        # Ваша логика обработки запроса здесь
        response = prompt_mode_pb2.PromptModeResponse(
            answer="Your answer",
            success=True,
            data=prompt_mode_pb2.Data(message="Some data"),
            execution=0.5
        )
        return response

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    prompt_mode_pb2_grpc.add_PromptModeServiceServicer_to_server(PromptModeService(), server)
    server.add_insecure_port('[::]:50051')
    print('Server is running on port 50051...')
    server.start()
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
