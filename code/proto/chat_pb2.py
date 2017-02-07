# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: chat.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


import struct_pb2


DESCRIPTOR = _descriptor.FileDescriptor(
  name='chat.proto',
  package='cardgame',
  serialized_pb=_b('\n\nchat.proto\x12\x08\x63\x61rdgame\x1a\x0cstruct.proto\"@\n\x0bSendChatReq\x12\x10\n\x08table_id\x18\x01 \x02(\x05\x12\x0f\n\x07message\x18\x02 \x02(\t\"\x0e\n\x03\x44\x45\x46\x12\x07\n\x02ID\x10\xb0\t\"@\n\x0cSendChatResp\x12 \n\x06result\x18\x01 \x01(\x0b\x32\x10.cardgame.Result\"\x0e\n\x03\x44\x45\x46\x12\x07\n\x02ID\x10\xb1\t\"N\n\tChatEvent\x12\x0e\n\x06sender\x18\x01 \x02(\x05\x12\x10\n\x08table_id\x18\x02 \x02(\x05\x12\x0f\n\x07message\x18\x03 \x02(\t\"\x0e\n\x03\x44\x45\x46\x12\x07\n\x02ID\x10\xe2\tB\"\n\x18\x63om.zhili.cardgame.protoB\x04\x43hatH\x03')
  ,
  dependencies=[struct_pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_SENDCHATREQ_DEF = _descriptor.EnumDescriptor(
  name='DEF',
  full_name='cardgame.SendChatReq.DEF',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ID', index=0, number=1200,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=88,
  serialized_end=102,
)
_sym_db.RegisterEnumDescriptor(_SENDCHATREQ_DEF)

_SENDCHATRESP_DEF = _descriptor.EnumDescriptor(
  name='DEF',
  full_name='cardgame.SendChatResp.DEF',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ID', index=0, number=1201,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=154,
  serialized_end=168,
)
_sym_db.RegisterEnumDescriptor(_SENDCHATRESP_DEF)

_CHATEVENT_DEF = _descriptor.EnumDescriptor(
  name='DEF',
  full_name='cardgame.ChatEvent.DEF',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ID', index=0, number=1250,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=234,
  serialized_end=248,
)
_sym_db.RegisterEnumDescriptor(_CHATEVENT_DEF)


_SENDCHATREQ = _descriptor.Descriptor(
  name='SendChatReq',
  full_name='cardgame.SendChatReq',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='table_id', full_name='cardgame.SendChatReq.table_id', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='message', full_name='cardgame.SendChatReq.message', index=1,
      number=2, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _SENDCHATREQ_DEF,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=38,
  serialized_end=102,
)


_SENDCHATRESP = _descriptor.Descriptor(
  name='SendChatResp',
  full_name='cardgame.SendChatResp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='result', full_name='cardgame.SendChatResp.result', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _SENDCHATRESP_DEF,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=104,
  serialized_end=168,
)


_CHATEVENT = _descriptor.Descriptor(
  name='ChatEvent',
  full_name='cardgame.ChatEvent',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sender', full_name='cardgame.ChatEvent.sender', index=0,
      number=1, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='table_id', full_name='cardgame.ChatEvent.table_id', index=1,
      number=2, type=5, cpp_type=1, label=2,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='message', full_name='cardgame.ChatEvent.message', index=2,
      number=3, type=9, cpp_type=9, label=2,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _CHATEVENT_DEF,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=170,
  serialized_end=248,
)

_SENDCHATREQ_DEF.containing_type = _SENDCHATREQ
_SENDCHATRESP.fields_by_name['result'].message_type = struct_pb2._RESULT
_SENDCHATRESP_DEF.containing_type = _SENDCHATRESP
_CHATEVENT_DEF.containing_type = _CHATEVENT
DESCRIPTOR.message_types_by_name['SendChatReq'] = _SENDCHATREQ
DESCRIPTOR.message_types_by_name['SendChatResp'] = _SENDCHATRESP
DESCRIPTOR.message_types_by_name['ChatEvent'] = _CHATEVENT

SendChatReq = _reflection.GeneratedProtocolMessageType('SendChatReq', (_message.Message,), dict(
  DESCRIPTOR = _SENDCHATREQ,
  __module__ = 'chat_pb2'
  # @@protoc_insertion_point(class_scope:cardgame.SendChatReq)
  ))
_sym_db.RegisterMessage(SendChatReq)

SendChatResp = _reflection.GeneratedProtocolMessageType('SendChatResp', (_message.Message,), dict(
  DESCRIPTOR = _SENDCHATRESP,
  __module__ = 'chat_pb2'
  # @@protoc_insertion_point(class_scope:cardgame.SendChatResp)
  ))
_sym_db.RegisterMessage(SendChatResp)

ChatEvent = _reflection.GeneratedProtocolMessageType('ChatEvent', (_message.Message,), dict(
  DESCRIPTOR = _CHATEVENT,
  __module__ = 'chat_pb2'
  # @@protoc_insertion_point(class_scope:cardgame.ChatEvent)
  ))
_sym_db.RegisterMessage(ChatEvent)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\030com.zhili.cardgame.protoB\004ChatH\003'))
# @@protoc_insertion_point(module_scope)
