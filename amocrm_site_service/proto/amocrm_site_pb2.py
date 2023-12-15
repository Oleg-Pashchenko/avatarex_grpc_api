# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: amocrm_site.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x11\x61mocrm_site.proto\x12\x16\x61mocrm_connect_service\"E\n\x14\x41mocrmConnectRequest\x12\r\n\x05login\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\x12\x0c\n\x04host\x18\x03 \x01(\t\"?\n\x0eGetInfoRequest\x12\r\n\x05\x65mail\x18\x01 \x01(\t\x12\x10\n\x08password\x18\x02 \x01(\t\x12\x0c\n\x04host\x18\x03 \x01(\t\"\x17\n\x04\x44\x61ta\x12\x0f\n\x07message\x18\x01 \x01(\t\"w\n\x15\x41mocrmConnectResponse\x12\x0e\n\x06\x61nswer\x18\x01 \x01(\t\x12\x0f\n\x07success\x18\x02 \x01(\x08\x12*\n\x04\x64\x61ta\x18\x03 \x01(\x0b\x32\x1c.amocrm_connect_service.Data\x12\x11\n\texecution\x18\x04 \x01(\x02\"u\n\x0fGetInfoResponse\x12\x33\n\tpipelines\x18\x01 \x03(\x0b\x32 .amocrm_connect_service.Pipeline\x12-\n\x06\x66ields\x18\x02 \x03(\x0b\x32\x1d.amocrm_connect_service.Field\"d\n\x08Pipeline\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04sort\x18\x03 \x01(\x05\x12\x30\n\x08statuses\x18\x04 \x03(\x0b\x32\x1e.amocrm_connect_service.Status\"0\n\x06Status\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04sort\x18\x02 \x01(\x05\x12\x0c\n\x04name\x18\x03 \x01(\t\"~\n\x05\x46ield\x12\n\n\x02id\x18\x01 \x01(\x05\x12\x0c\n\x04name\x18\x02 \x01(\t\x12\x0c\n\x04type\x18\x03 \x01(\t\x12\x14\n\x0c\x61\x63tive_value\x18\x04 \x01(\t\x12\x37\n\x0fpossible_values\x18\x05 \x03(\x0b\x32\x1e.amocrm_connect_service.Select\"1\n\x06Select\x12\n\n\x02id\x18\x01 \x01(\x05\x12\r\n\x05value\x18\x02 \x01(\t\x12\x0c\n\x04sort\x18\x03 \x01(\x05\"\x87\x01\n\x04\x43hat\x12\x0f\n\x07\x63hat_id\x18\x01 \x01(\t\x12\x0f\n\x07message\x18\x02 \x01(\t\x12\n\n\x02id\x18\x03 \x01(\t\x12\x13\n\x0bpipeline_id\x18\x04 \x01(\x05\x12\x0f\n\x07lead_id\x18\x05 \x01(\x05\x12\x11\n\tstatus_id\x18\x06 \x01(\x05\x12\x18\n\x10messages_history\x18\x07 \x01(\t2\xdd\x01\n\x14\x41mocrmConnectService\x12i\n\nTryConnect\x12,.amocrm_connect_service.AmocrmConnectRequest\x1a-.amocrm_connect_service.AmocrmConnectResponse\x12Z\n\x07GetInfo\x12&.amocrm_connect_service.GetInfoRequest\x1a\'.amocrm_connect_service.GetInfoResponseb\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'amocrm_site_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_AMOCRMCONNECTREQUEST']._serialized_start=45
  _globals['_AMOCRMCONNECTREQUEST']._serialized_end=114
  _globals['_GETINFOREQUEST']._serialized_start=116
  _globals['_GETINFOREQUEST']._serialized_end=179
  _globals['_DATA']._serialized_start=181
  _globals['_DATA']._serialized_end=204
  _globals['_AMOCRMCONNECTRESPONSE']._serialized_start=206
  _globals['_AMOCRMCONNECTRESPONSE']._serialized_end=325
  _globals['_GETINFORESPONSE']._serialized_start=327
  _globals['_GETINFORESPONSE']._serialized_end=444
  _globals['_PIPELINE']._serialized_start=446
  _globals['_PIPELINE']._serialized_end=546
  _globals['_STATUS']._serialized_start=548
  _globals['_STATUS']._serialized_end=596
  _globals['_FIELD']._serialized_start=598
  _globals['_FIELD']._serialized_end=724
  _globals['_SELECT']._serialized_start=726
  _globals['_SELECT']._serialized_end=775
  _globals['_CHAT']._serialized_start=778
  _globals['_CHAT']._serialized_end=913
  _globals['_AMOCRMCONNECTSERVICE']._serialized_start=916
  _globals['_AMOCRMCONNECTSERVICE']._serialized_end=1137
# @@protoc_insertion_point(module_scope)