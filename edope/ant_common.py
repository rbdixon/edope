from scapy.all import BitEnumField
from scapy.all import BitField
from scapy.all import ByteEnumField
from scapy.all import FieldListField
from scapy.all import Packet
from scapy.all import XByteField
from scapy.all import XShortField

__all__ = ['Padding', 'ExtendedBroadcastData', 'OptionalExtended', 'ENUM_DEVICE_TYPE']

ENUM_DEVICE_TYPE = {
    11: 'BIKE POWER (11)',
    120: 'HRM (120)',
    122: 'CADENCE (122)',
    17: 'FITNESS (17)',
}


class Padding(Packet):
    fields_desc = [
        FieldListField('padding', None, XByteField('x', 0), count_from=lambda p: 2)
    ]


class ExtendedBroadcastData(Packet):

    fields_desc = [
        XByteField('extended', 0x80),
        XShortField('device_number', 0),
        ByteEnumField('device_type', 0, ENUM_DEVICE_TYPE),
        # ByteField('transmission_type', 0),
        BitEnumField(
            'channel_type',
            0,
            2,
            {
                0: 'RESERVED',
                1: 'INDEPENDENT',
                2: 'SHARED 1-BYTE ADDR',
                3: 'SHARED 2-BYTE ADDR',
            },
        ),
        BitEnumField('global_data', 0, 1, {0: 'NOT USED', 1: 'USED'}),
        BitField('undefined', 0, 1),
        BitField('ext_serial_number', 0, 4),
    ]


class OptionalExtended(Packet):
    def guess_payload_class(self, pkt):
        if pkt[0] == 0x80:
            return ExtendedBroadcastData
