# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: pogoprotos/data/buddy/buddy_notification_click_telemetry.proto

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
from google.protobuf import descriptor_pb2
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='pogoprotos/data/buddy/buddy_notification_click_telemetry.proto',
  package='pogoprotos.data.buddy',
  syntax='proto3',
  serialized_pb=_b('\n>pogoprotos/data/buddy/buddy_notification_click_telemetry.proto\x12\x15pogoprotos.data.buddy\"@\n\x1f\x42uddyNotificationClickTelemetry\x12\x1d\n\x15notification_category\x18\x01 \x01(\x05\x62\x06proto3')
)
_sym_db.RegisterFileDescriptor(DESCRIPTOR)




_BUDDYNOTIFICATIONCLICKTELEMETRY = _descriptor.Descriptor(
  name='BuddyNotificationClickTelemetry',
  full_name='pogoprotos.data.buddy.BuddyNotificationClickTelemetry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='notification_category', full_name='pogoprotos.data.buddy.BuddyNotificationClickTelemetry.notification_category', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      options=None),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=89,
  serialized_end=153,
)

DESCRIPTOR.message_types_by_name['BuddyNotificationClickTelemetry'] = _BUDDYNOTIFICATIONCLICKTELEMETRY

BuddyNotificationClickTelemetry = _reflection.GeneratedProtocolMessageType('BuddyNotificationClickTelemetry', (_message.Message,), dict(
  DESCRIPTOR = _BUDDYNOTIFICATIONCLICKTELEMETRY,
  __module__ = 'pogoprotos.data.buddy.buddy_notification_click_telemetry_pb2'
  # @@protoc_insertion_point(class_scope:pogoprotos.data.buddy.BuddyNotificationClickTelemetry)
  ))
_sym_db.RegisterMessage(BuddyNotificationClickTelemetry)


# @@protoc_insertion_point(module_scope)