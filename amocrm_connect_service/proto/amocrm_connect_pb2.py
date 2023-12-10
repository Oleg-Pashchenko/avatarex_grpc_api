# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: amocrm_connect.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x14\x61mocrm_connect.proto\x12\x16\x61mocrm_connect_service\"E\n\x14\x41mocrmConnectRequest\x12\r\n\x05login\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\x12\x0c\n\x04host\x18\x03 \x01(\t\"?\n\x0eGetInfoRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\x12\x0c\n\x04host\x18\x03 \x01(\t\"g\n\x12SendMessageRequest\x12\x0c\n\x04host\x18\x01 \x01(\t\x12\r\n\x05\x65mail\x18\x02 \x01(\t\x12\x10\n\x08password\x18\x03 \x01(\t\x12\x0f\n\x07message\x18\x04 \x01(\t\x12\x11\n\tchat_hash\x18\x05 \x01(\t\"v\n\x1dReadUnansweredMessagesRequest\x12\x0c\n\x04host\x18\x01 \x01(\t\x12\r\n\x05\x65mail\x18\x02 \x01(\t\x12\x10\n\x08password\x18\x03 \x01(\t\x12\x13\n\x0bpipeline_id\x18\x04 \x01(\x05\x12\x11\n\tstage_ids\x18\x05 \x03(\x05\"\x17\n\x04\x44\x61ta\x12\x0f\n\x07message\x18\x01 \x01(\t\"w\n\x15\x41mocrmConnectResponse\x12\x0e\n\x06\x61nswer\x18\x01 \x01(\x08\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12*\n\x04\x64\x61ta\x18\x03 \x01(\x0b\x32\x1c.amocrm_connect_service.Data\x12\x11\n\texecution\x18\x04 \x01(\x02\"F\n\x0fGetInfoResponse\x12\x33\n\tpipelines\x18\x01 \x03(\x0b\x32 .amocrm_connect_service.Pipeline\"\x9a\x01\n\x1a\x41mocrmReadMessagesResponse\x12,\n\x06\x61nswer\x18\x01 \x03(\x0b\x32\x1c.amocrm_connect_service.Chat\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12*\n\x04\x64\x61ta\x18\x03 \x01(\x0b\x32\x1c.amocrm_connect_service.Data\x12\x11\n\texecution\x18\x04 \x01(\x02\"d\n\x08Pipeline\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04sort\x18\x03 \x01(\x05\x12\x30\n\x08statuses\x18\x04 \x03(\x0b\x32\x1e.amocrm_connect_service.Status\"0\n\x06Status\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04sort\x18\x02 \x01(\x05\x12\x0c\n\x04name\x18\x03 \x01(\t\"a\n\x04\x43hat\x12\x0f\n\x07\x63hat_id\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\x13\n\x0bpipeline_id\x18\x03 \x01(\x05\x12\x0f\n\x07lead_id\x18\x04 \x01(\x05\x12\x11\n\tstatus_id\x18\x05 \x01(\x05\x32\xcd\x03\n\x14\x41mocrmConnectService\x12i\n\nTryConnect\x12,.amocrm_connect_service.AmocrmConnectRequest\x1a-.amocrm_connect_service.AmocrmConnectResponse\x12Z\n\x07GetInfo\x12&.amocrm_connect_service.GetInfoRequest\x1a\'.amocrm_connect_service.GetInfoResponse\x12h\n\x0bSendMessage\x12*.amocrm_connect_service.SendMessageRequest\x1a-.amocrm_connect_service.AmocrmConnectResponse\x12\x83\x01\n\x16ReadUnansweredMessages\x12\x35.amocrm_connect_service.ReadUnansweredMessagesRequest\x1a\x32.amocrm_connect_service.AmocrmReadMessagesResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'amocrm_connect_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_AMOCRMCONNECTREQUEST']._serialized_start=48
  _globals['_AMOCRMCONNECTREQUEST']._serialized_end=117
  _globals['_GETINFOREQUEST']._serialized_start=119
  _globals['_GETINFOREQUEST']._serialized_end=182
  _globals['_SENDMESSAGEREQUEST']._serialized_start=184
  _globals['_SENDMESSAGEREQUEST']._serialized_end=287
  _globals['_READUNANSWEREDMESSAGESREQUEST']._serialized_start=289
  _globals['_READUNANSWEREDMESSAGESREQUEST']._serialized_end=407
  _globals['_DATA']._serialized_start=409
  _globals['_DATA']._serialized_end=432
  _globals['_AMOCRMCONNECTRESPONSE']._serialized_start=434
  _globals['_AMOCRMCONNECTRESPONSE']._serialized_end=553
  _globals['_GETINFORESPONSE']._serialized_start=555
  _globals['_GETINFORESPONSE']._serialized_end=625
  _globals['_AMOCRMREADMESSAGESRESPONSE']._serialized_start=628
  _globals['_AMOCRMREADMESSAGESRESPONSE']._serialized_end=782
  _globals['_PIPELINE']._serialized_start=784
  _globals['_PIPELINE']._serialized_end=884
  _globals['_STATUS']._serialized_start=886
  _globals['_STATUS']._serialized_end=934
  _globals['_CHAT']._serialized_start=936
  _globals['_CHAT']._serialized_end=1033
  _globals['_AMOCRMCONNECTSERVICE']._serialized_start=1036
  _globals['_AMOCRMCONNECTSERVICE']._serialized_end=1497
# @@protoc_insertion_point(module_scope)
