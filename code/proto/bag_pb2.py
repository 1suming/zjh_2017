# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: bag.proto

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
  name='bag.proto',
  package='cardgame',
  serialized_pb=_b('\n\tbag.proto\x12\x08\x63\x61rdgame\x1a\x0cstruct.proto\"\x1d\n\x0bQueryBagReq\"\x0e\n\x03\x44\x45\x46\x12\x07\n\x02ID\x10\xe8 \"\\\n\x0cQueryBagResp\x12\x1d\n\x05items\x18\x01 \x03(\x0b\x32\x0e.cardgame.Item\x12\x1d\n\x05gifts\x18\x02 \x03(\x0b\x32\x0e.cardgame.Gift\"\x0e\n\x03\x44\x45\x46\x12\x07\n\x02ID\x10\xe9 B!\n\x18\x63om.zhili.cardgame.protoB\x03\x42\x61gH\x03')
  ,
  dependencies=[struct_pb2.DESCRIPTOR,])
_sym_db.RegisterFileDescriptor(DESCRIPTOR)



_QUERYBAGREQ_DEF = _descriptor.EnumDescriptor(
  name='DEF',
  full_name='cardgame.QueryBagReq.DEF',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ID', index=0, number=4200,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=52,
  serialized_end=66,
)
_sym_db.RegisterEnumDescriptor(_QUERYBAGREQ_DEF)

_QUERYBAGRESP_DEF = _descriptor.EnumDescriptor(
  name='DEF',
  full_name='cardgame.QueryBagResp.DEF',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ID', index=0, number=4201,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=146,
  serialized_end=160,
)
_sym_db.RegisterEnumDescriptor(_QUERYBAGRESP_DEF)


_QUERYBAGREQ = _descriptor.Descriptor(
  name='QueryBagReq',
  full_name='cardgame.QueryBagReq',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _QUERYBAGREQ_DEF,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=37,
  serialized_end=66,
)


_QUERYBAGRESP = _descriptor.Descriptor(
  name='QueryBagResp',
  full_name='cardgame.QueryBagResp',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='items', full_name='cardgame.QueryBagResp.items', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
    _descriptor.FieldDescriptor(
      name='gifts', full_name='cardgame.QueryBagResp.gifts', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _QUERYBAGRESP_DEF,
  ],
  options=None,
  is_extendable=False,
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=68,
  serialized_end=160,
)

_QUERYBAGREQ_DEF.containing_type = _QUERYBAGREQ
_QUERYBAGRESP.fields_by_name['items'].message_type = struct_pb2._ITEM
_QUERYBAGRESP.fields_by_name['gifts'].message_type = struct_pb2._GIFT
_QUERYBAGRESP_DEF.containing_type = _QUERYBAGRESP
DESCRIPTOR.message_types_by_name['QueryBagReq'] = _QUERYBAGREQ
DESCRIPTOR.message_types_by_name['QueryBagResp'] = _QUERYBAGRESP

QueryBagReq = _reflection.GeneratedProtocolMessageType('QueryBagReq', (_message.Message,), dict(
  DESCRIPTOR = _QUERYBAGREQ,
  __module__ = 'bag_pb2'
  # @@protoc_insertion_point(class_scope:cardgame.QueryBagReq)
  ))
_sym_db.RegisterMessage(QueryBagReq)

QueryBagResp = _reflection.GeneratedProtocolMessageType('QueryBagResp', (_message.Message,), dict(
  DESCRIPTOR = _QUERYBAGRESP,
  __module__ = 'bag_pb2'
  # @@protoc_insertion_point(class_scope:cardgame.QueryBagResp)
  ))
_sym_db.RegisterMessage(QueryBagResp)


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\030com.zhili.cardgame.protoB\003BagH\003'))
# @@protoc_insertion_point(module_scope)
