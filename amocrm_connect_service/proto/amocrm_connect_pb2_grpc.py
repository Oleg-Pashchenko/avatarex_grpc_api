# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import amocrm_connect_pb2 as amocrm__connect__pb2


class AmocrmConnectServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.TryConnect = channel.unary_unary(
                '/amocrm_connect_service.AmocrmConnectService/TryConnect',
                request_serializer=amocrm__connect__pb2.AmocrmConnectRequest.SerializeToString,
                response_deserializer=amocrm__connect__pb2.AmocrmConnectResponse.FromString,
                )
        self.GetInfo = channel.unary_unary(
                '/amocrm_connect_service.AmocrmConnectService/GetInfo',
                request_serializer=amocrm__connect__pb2.GetInfoRequest.SerializeToString,
                response_deserializer=amocrm__connect__pb2.GetInfoResponse.FromString,
                )


class AmocrmConnectServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def TryConnect(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def GetInfo(self, request, context):
        """rpc SendMessage (SendMessageRequest) returns (AmocrmConnectResponse);
        rpc ReadUnansweredMessages (ReadUnansweredMessagesRequest) returns (AmocrmReadMessagesResponse);
        rpc GetFieldsByDealId (GetFieldsRequest) returns (AmocrmGetFieldsResponse);
        rpc SetField (SetFieldRequest) returns (AmocrmConnectResponse);
        """
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_AmocrmConnectServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'TryConnect': grpc.unary_unary_rpc_method_handler(
                    servicer.TryConnect,
                    request_deserializer=amocrm__connect__pb2.AmocrmConnectRequest.FromString,
                    response_serializer=amocrm__connect__pb2.AmocrmConnectResponse.SerializeToString,
            ),
            'GetInfo': grpc.unary_unary_rpc_method_handler(
                    servicer.GetInfo,
                    request_deserializer=amocrm__connect__pb2.GetInfoRequest.FromString,
                    response_serializer=amocrm__connect__pb2.GetInfoResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'amocrm_connect_service.AmocrmConnectService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class AmocrmConnectService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def TryConnect(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/amocrm_connect_service.AmocrmConnectService/TryConnect',
            amocrm__connect__pb2.AmocrmConnectRequest.SerializeToString,
            amocrm__connect__pb2.AmocrmConnectResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def GetInfo(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/amocrm_connect_service.AmocrmConnectService/GetInfo',
            amocrm__connect__pb2.GetInfoRequest.SerializeToString,
            amocrm__connect__pb2.GetInfoResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
