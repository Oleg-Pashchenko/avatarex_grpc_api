# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from prompt_mode_service.proto import prompt_mode_pb2 as prompt__mode__pb2


class PromptModeServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.GetAnswer = channel.unary_unary(
                '/prompt_mode_service.PromptModeService/GetAnswer',
                request_serializer=prompt__mode__pb2.PromptModeRequest.SerializeToString,
                response_deserializer=prompt__mode__pb2.PromptModeResponse.FromString,
                )


class PromptModeServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def GetAnswer(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_PromptModeServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'GetAnswer': grpc.unary_unary_rpc_method_handler(
                    servicer.GetAnswer,
                    request_deserializer=prompt__mode__pb2.PromptModeRequest.FromString,
                    response_serializer=prompt__mode__pb2.PromptModeResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'prompt_mode_service.PromptModeService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class PromptModeService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def GetAnswer(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/prompt_mode_service.PromptModeService/GetAnswer',
            prompt__mode__pb2.PromptModeRequest.SerializeToString,
            prompt__mode__pb2.PromptModeResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
