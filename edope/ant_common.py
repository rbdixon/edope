from scapy.all import XByteField, FieldListField, Packet

__all__ = ['Padding', 'ExtendedBroadcastData', 'PageOptionalExtended']


class Padding(Packet):
    fields_desc = [
        FieldListField('padding', None, XByteField('x', 0), count_from=lambda p: 2)
    ]


class ExtendedBroadcastData(Packet):

    fields_desc = [
        XByteField('extended', 0x80),
        FieldListField('data', None, XByteField('x', 0), count_from=lambda p: 4),
    ]


class PageOptionalExtended(Packet):
    def guess_payload_class(self, pkt):
        if pkt[0] == 0x80:
            return ExtendedBroadcastData
