import logging
from scapy.all import (
    Packet,
    BitField,
    FieldListField,
    ByteField,
    XByteField,
    LEShortField,
)

log = logging.getLogger(__name__)

DEVICE_TYPE_CADENCE = 122

__all__ = ['DEVICE_TYPE_CADENCE', 'CadencePayload']


class CadencePayload(Packet):
    fields_desc = [
        BitField('page_change_toggle', 0, 1),
        BitField('data_page_number', None, 7),
        # ignore differences between page types
        FieldListField('data', None, XByteField('x', 0), count_from=lambda p: 3),
        LEShortField('cadence_event_time', 0),
        LEShortField('cadence_rev_count', 0),
    ]
