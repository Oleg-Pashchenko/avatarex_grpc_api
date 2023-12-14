# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

from . import qualification_pb2 as qualification__pb2


class QualificationServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.ExecuteQualification = channel.unary_unary(
                '/qualification_service.QualificationService/ExecuteQualification',
                request_serializer=qualification__pb2.QualificationRequest.SerializeToString,
                response_deserializer=qualification__pb2.QualificationResponse.FromString,
                )


class QualificationServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def ExecuteQualification(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_QualificationServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'ExecuteQualification': grpc.unary_unary_rpc_method_handler(
                    servicer.ExecuteQualification,
                    request_deserializer=qualification__pb2.QualificationRequest.FromString,
                    response_serializer=qualification__pb2.QualificationResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'qualification_service.QualificationService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class QualificationService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def ExecuteQualification(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/qualification_service.QualificationService/ExecuteQualification',
            qualification__pb2.QualificationRequest.SerializeToString,
            qualification__pb2.QualificationResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
