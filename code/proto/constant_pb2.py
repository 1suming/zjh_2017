# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: constant.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='constant.proto',
  package='cardgame',
  serialized_pb=_b('\n\x0e\x63onstant.proto\x12\x08\x63\x61rdgame*\x8c\x01\n\x07IDScope\x12\r\n\tID_SYSTEM\x10\x00\x12\x0c\n\x07ID_HALL\x10\xe8\x07\x12\x0c\n\x07ID_CHAT\x10\xb0\t\x12\x0e\n\tID_REWARD\x10\xd0\x0f\x12\r\n\x08ID_TRADE\x10\xb8\x17\x12\x0b\n\x06ID_BAG\x10\xac\x1b\x12\x0e\n\tID_FRIEND\x10\xa0\x1f\x12\x0c\n\x07ID_RANK\x10\xe8 \x12\x0c\n\x07ID_GAME\x10\x88\'*w\n\x0eTableEventType\x12\x0f\n\x0bPLAYER_JOIN\x10\x01\x12\x10\n\x0cPLAYER_LEAVE\x10\x02\x12\x16\n\x12PLAYER_RECONNECTED\x10\x03\x12\x17\n\x13PLAYER_DISCONNECTED\x10\x04\x12\x11\n\rPLAYER_KICKED\x10\x05*X\n\tBetAction\x12\n\n\x06\x46OLLOW\x10\x01\x12\x07\n\x03\x41\x44\x44\x10\x02\x12\x0b\n\x07\x43OMPARE\x10\x03\x12\r\n\tSHOW_HAND\x10\x04\x12\x0b\n\x07GIVE_UP\x10\x05\x12\r\n\tSEE_POKER\x10\x06*2\n\tTableType\x12\x0b\n\x07TABLE_L\x10\x01\x12\x0b\n\x07TABLE_M\x10\x02\x12\x0b\n\x07TABLE_H\x10\x03*g\n\tPokerType\x12\x0b\n\x07P_BAOZI\x10\n\x12\x11\n\rP_TONGHUASHUN\x10\t\x12\r\n\tP_TONGHUA\x10\x08\x12\n\n\x06P_SHUN\x10\x07\x12\t\n\x05P_DUI\x10\x06\x12\t\n\x05P_DAN\x10\x05\x12\t\n\x05P_352\x10\x04*Q\n\x08RankType\x12\x0f\n\x0bRANK_WEALTH\x10\x01\x12\x0f\n\x0bRANK_CHARGE\x10\x02\x12\x0e\n\nRANK_CHARM\x10\x03\x12\x13\n\x0fRANK_MAKE_MONEY\x10\x04*\x93\x01\n\x08RankTime\x12\x11\n\rRANK_ALL_TIME\x10\x00\x12\x12\n\x0eRANK_YESTERDAY\x10\x01\x12\x0e\n\nRANK_TODAY\x10\x02\x12\x13\n\x0fRANK_LAST_MONTH\x10\x03\x12\x13\n\x0fRANK_THIS_MONTH\x10\x04\x12\x12\n\x0eRANK_LAST_WEEK\x10\x05\x12\x12\n\x0eRANK_THIS_WEEK\x10\x06*,\n\x0cShopItemType\x12\r\n\tSHOP_GOLD\x10\x01\x12\r\n\tSHOP_ITEM\x10\x02*b\n\x10NotificationType\x12\x0f\n\x0bN_BROADCAST\x10\x01\x12\n\n\x06N_MAIL\x10\x02\x12\x0c\n\x08N_REWARD\x10\x03\x12\x13\n\x0fN_GIFT_RECEIVED\x10\x04\x12\x0e\n\nN_KICK_OFF\x10\x05*9\n\nRewardType\x12\x08\n\x04\x44ONE\x10\x00\x12\x0b\n\x07SUCCESS\x10\x01\x12\x14\n\x07NO_TASK\x10\xff\xff\xff\xff\xff\xff\xff\xff\xff\x01\x42&\n\x18\x63om.zhili.cardgame.protoB\x08\x43onstantH\x03')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

_IDSCOPE = _descriptor.EnumDescriptor(
  name='IDScope',
  full_name='cardgame.IDScope',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='ID_SYSTEM', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ID_HALL', index=1, number=1000,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ID_CHAT', index=2, number=1200,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ID_REWARD', index=3, number=2000,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ID_TRADE', index=4, number=3000,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ID_BAG', index=5, number=3500,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ID_FRIEND', index=6, number=4000,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ID_RANK', index=7, number=4200,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ID_GAME', index=8, number=5000,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=29,
  serialized_end=169,
)
_sym_db.RegisterEnumDescriptor(_IDSCOPE)

IDScope = enum_type_wrapper.EnumTypeWrapper(_IDSCOPE)
_TABLEEVENTTYPE = _descriptor.EnumDescriptor(
  name='TableEventType',
  full_name='cardgame.TableEventType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='PLAYER_JOIN', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PLAYER_LEAVE', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PLAYER_RECONNECTED', index=2, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PLAYER_DISCONNECTED', index=3, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='PLAYER_KICKED', index=4, number=5,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=171,
  serialized_end=290,
)
_sym_db.RegisterEnumDescriptor(_TABLEEVENTTYPE)

TableEventType = enum_type_wrapper.EnumTypeWrapper(_TABLEEVENTTYPE)
_BETACTION = _descriptor.EnumDescriptor(
  name='BetAction',
  full_name='cardgame.BetAction',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='FOLLOW', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='ADD', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='COMPARE', index=2, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SHOW_HAND', index=3, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='GIVE_UP', index=4, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SEE_POKER', index=5, number=6,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=292,
  serialized_end=380,
)
_sym_db.RegisterEnumDescriptor(_BETACTION)

BetAction = enum_type_wrapper.EnumTypeWrapper(_BETACTION)
_TABLETYPE = _descriptor.EnumDescriptor(
  name='TableType',
  full_name='cardgame.TableType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='TABLE_L', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TABLE_M', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='TABLE_H', index=2, number=3,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=382,
  serialized_end=432,
)
_sym_db.RegisterEnumDescriptor(_TABLETYPE)

TableType = enum_type_wrapper.EnumTypeWrapper(_TABLETYPE)
_POKERTYPE = _descriptor.EnumDescriptor(
  name='PokerType',
  full_name='cardgame.PokerType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='P_BAOZI', index=0, number=10,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='P_TONGHUASHUN', index=1, number=9,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='P_TONGHUA', index=2, number=8,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='P_SHUN', index=3, number=7,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='P_DUI', index=4, number=6,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='P_DAN', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='P_352', index=6, number=4,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=434,
  serialized_end=537,
)
_sym_db.RegisterEnumDescriptor(_POKERTYPE)

PokerType = enum_type_wrapper.EnumTypeWrapper(_POKERTYPE)
_RANKTYPE = _descriptor.EnumDescriptor(
  name='RankType',
  full_name='cardgame.RankType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='RANK_WEALTH', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RANK_CHARGE', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RANK_CHARM', index=2, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RANK_MAKE_MONEY', index=3, number=4,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=539,
  serialized_end=620,
)
_sym_db.RegisterEnumDescriptor(_RANKTYPE)

RankType = enum_type_wrapper.EnumTypeWrapper(_RANKTYPE)
_RANKTIME = _descriptor.EnumDescriptor(
  name='RankTime',
  full_name='cardgame.RankTime',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='RANK_ALL_TIME', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RANK_YESTERDAY', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RANK_TODAY', index=2, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RANK_LAST_MONTH', index=3, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RANK_THIS_MONTH', index=4, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RANK_LAST_WEEK', index=5, number=5,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='RANK_THIS_WEEK', index=6, number=6,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=623,
  serialized_end=770,
)
_sym_db.RegisterEnumDescriptor(_RANKTIME)

RankTime = enum_type_wrapper.EnumTypeWrapper(_RANKTIME)
_SHOPITEMTYPE = _descriptor.EnumDescriptor(
  name='ShopItemType',
  full_name='cardgame.ShopItemType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SHOP_GOLD', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SHOP_ITEM', index=1, number=2,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=772,
  serialized_end=816,
)
_sym_db.RegisterEnumDescriptor(_SHOPITEMTYPE)

ShopItemType = enum_type_wrapper.EnumTypeWrapper(_SHOPITEMTYPE)
_NOTIFICATIONTYPE = _descriptor.EnumDescriptor(
  name='NotificationType',
  full_name='cardgame.NotificationType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='N_BROADCAST', index=0, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='N_MAIL', index=1, number=2,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='N_REWARD', index=2, number=3,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='N_GIFT_RECEIVED', index=3, number=4,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='N_KICK_OFF', index=4, number=5,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=818,
  serialized_end=916,
)
_sym_db.RegisterEnumDescriptor(_NOTIFICATIONTYPE)

NotificationType = enum_type_wrapper.EnumTypeWrapper(_NOTIFICATIONTYPE)
_REWARDTYPE = _descriptor.EnumDescriptor(
  name='RewardType',
  full_name='cardgame.RewardType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='DONE', index=0, number=0,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SUCCESS', index=1, number=1,
      options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='NO_TASK', index=2, number=-1,
      options=None,
      type=None),
  ],
  containing_type=None,
  options=None,
  serialized_start=918,
  serialized_end=975,
)
_sym_db.RegisterEnumDescriptor(_REWARDTYPE)

RewardType = enum_type_wrapper.EnumTypeWrapper(_REWARDTYPE)
ID_SYSTEM = 0
ID_HALL = 1000
ID_CHAT = 1200
ID_REWARD = 2000
ID_TRADE = 3000
ID_BAG = 3500
ID_FRIEND = 4000
ID_RANK = 4200
ID_GAME = 5000
PLAYER_JOIN = 1
PLAYER_LEAVE = 2
PLAYER_RECONNECTED = 3
PLAYER_DISCONNECTED = 4
PLAYER_KICKED = 5
FOLLOW = 1
ADD = 2
COMPARE = 3
SHOW_HAND = 4
GIVE_UP = 5
SEE_POKER = 6
TABLE_L = 1
TABLE_M = 2
TABLE_H = 3
P_BAOZI = 10
P_TONGHUASHUN = 9
P_TONGHUA = 8
P_SHUN = 7
P_DUI = 6
P_DAN = 5
P_352 = 4
RANK_WEALTH = 1
RANK_CHARGE = 2
RANK_CHARM = 3
RANK_MAKE_MONEY = 4
RANK_ALL_TIME = 0
RANK_YESTERDAY = 1
RANK_TODAY = 2
RANK_LAST_MONTH = 3
RANK_THIS_MONTH = 4
RANK_LAST_WEEK = 5
RANK_THIS_WEEK = 6
SHOP_GOLD = 1
SHOP_ITEM = 2
N_BROADCAST = 1
N_MAIL = 2
N_REWARD = 3
N_GIFT_RECEIVED = 4
N_KICK_OFF = 5
DONE = 0
SUCCESS = 1
NO_TASK = -1


DESCRIPTOR.enum_types_by_name['IDScope'] = _IDSCOPE
DESCRIPTOR.enum_types_by_name['TableEventType'] = _TABLEEVENTTYPE
DESCRIPTOR.enum_types_by_name['BetAction'] = _BETACTION
DESCRIPTOR.enum_types_by_name['TableType'] = _TABLETYPE
DESCRIPTOR.enum_types_by_name['PokerType'] = _POKERTYPE
DESCRIPTOR.enum_types_by_name['RankType'] = _RANKTYPE
DESCRIPTOR.enum_types_by_name['RankTime'] = _RANKTIME
DESCRIPTOR.enum_types_by_name['ShopItemType'] = _SHOPITEMTYPE
DESCRIPTOR.enum_types_by_name['NotificationType'] = _NOTIFICATIONTYPE
DESCRIPTOR.enum_types_by_name['RewardType'] = _REWARDTYPE


DESCRIPTOR.has_options = True
DESCRIPTOR._options = _descriptor._ParseOptions(descriptor_pb2.FileOptions(), _b('\n\030com.zhili.cardgame.protoB\010ConstantH\003'))
# @@protoc_insertion_point(module_scope)
