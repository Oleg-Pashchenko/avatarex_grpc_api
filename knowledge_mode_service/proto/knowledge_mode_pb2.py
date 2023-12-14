# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: knowledge_mode.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(
    b'\n\x14knowledge_mode.proto\x12\x18openai_knowledge_service"(\n\x04Rule\x12\x10\n\x08question\x18\x01 \x01(\t\x12\x0e\n\x06\x61nswer\x18\x02 \x01(\t"[\n\x0eOpenAISettings\x12\r\n\x05model\x18\x01 \x01(\t\x12\x12\n\nmax_tokens\x18\x02 \x01(\x05\x12\x13\n\x0btemperature\x18\x03 \x01(\x02\x12\x11\n\tapi_token\x18\x04 \x01(\t"\x9b\x01\n\x16OpenAIKnowledgeRequest\x12-\n\x05rules\x18\x01 \x03(\x0b\x32\x1e.openai_knowledge_service.Rule\x12\x41\n\x0fopenai_settings\x18\x02 \x01(\x0b\x32(.openai_knowledge_service.OpenAISettings\x12\x0f\n\x07message\x18\x03 \x01(\t".\n\x0cResponseData\x12\x0f\n\x07message\x18\x01 \x01(\t\x12\r\n\x05\x65rror\x18\x02 \x01(\t"x\n\x17OpenAIKnowledgeResponse\x12\x0f\n\x07success\x18\x01 \x01(\x08\x12\x34\n\x04\x64\x61ta\x18\x02 \x01(\x0b\x32&.openai_knowledge_service.ResponseData\x12\x16\n\x0e\x65xecution_time\x18\x03 \x01(\x02\x32\x94\x01\n\x16OpenAIKnowledgeService\x12z\n\x11\x43ompleteKnowledge\x12\x30.openai_knowledge_service.OpenAIKnowledgeRequest\x1a\x31.openai_knowledge_service.OpenAIKnowledgeResponse"\x00\x62\x06proto3'
)

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, "knowledge_mode_pb2", _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _globals["_RULE"]._serialized_start = 50
    _globals["_RULE"]._serialized_end = 90
    _globals["_OPENAISETTINGS"]._serialized_start = 92
    _globals["_OPENAISETTINGS"]._serialized_end = 183
    _globals["_OPENAIKNOWLEDGEREQUEST"]._serialized_start = 186
    _globals["_OPENAIKNOWLEDGEREQUEST"]._serialized_end = 341
    _globals["_RESPONSEDATA"]._serialized_start = 343
    _globals["_RESPONSEDATA"]._serialized_end = 389
    _globals["_OPENAIKNOWLEDGERESPONSE"]._serialized_start = 391
    _globals["_OPENAIKNOWLEDGERESPONSE"]._serialized_end = 511
    _globals["_OPENAIKNOWLEDGESERVICE"]._serialized_start = 514
    _globals["_OPENAIKNOWLEDGESERVICE"]._serialized_end = 662
# @@protoc_insertion_point(module_scope)