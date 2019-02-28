import logging
from scapy.all import Packet, BitField, FieldListField, ByteField, XByteField
from .ant_common import OptionalExtended

log = logging.getLogger(__name__)

DEVICE_TYPE_HRM = 120

__all__ = ['DEVICE_TYPE_HRM', 'HRMPayload']


class HRMPayload(OptionalExtended):
    fields_desc = [
        BitField('page_change_toggle', 0, 1),
        BitField('data_page_number', None, 7),
        # ignore differences between page types
        FieldListField('data', None, XByteField('x', 0), count_from=lambda p: 5),
        ByteField('beat_count', 0),
        ByteField('heart_rate', 0),
    ]
