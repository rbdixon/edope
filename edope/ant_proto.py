import logging

from types import MethodType
from scapy.all import *

from .ant_common import *
from .ant_hrm import *
from .ant_cadence import *
from .ant_fitness import *
from .ant_util import has_payload

__all__ = ['ANTMessage', 'ant_each', 'ant_map']

log = logging.getLogger(__name__)

DEVICE_TYPE_SCAN = 0
MSG_ID_CLS = {}

# Reference section 9.3: ANT Message Summary
_MSG_ID_CODE = {
    0x01: 'RF_EVENT',
    0x40: 'CHANNEL_EVENT_OR_RESPONSE',
    0x41: 'UNASSIGN_CHANNEL',
    0x42: 'ASSIGN_CHANNEL',
    0x43: 'SET_CHANNEL_PERIOD',
    0x44: 'SEARCH_TIMEOUT',
    0x45: 'SET_CHANNEL_FREQ',
    0x46: 'SET_NETWORK_KEY',
    0x47: 'TRANSMIT_POWER',
    0x4A: 'RESET_SYSTEM',
    0x4B: 'OPEN_CHANNEL',
    0x4C: 'CLOSE_CHANNEL',
    0x4D: 'REQUEST_MESSAGE',
    0x4E: 'BROADCAST_DATA',
    0x4F: 'ACKNOWLEDGE_DATA',
    0xC6: 'UNDOCUMENTED',
    0x51: 'SET_CHANNEL_ID',
    0x61: 'DEVICE_SERIAL_NUMBER',
    0x63: 'LOW_PRIORITY_SEARCH_TIMEOUT',
    0x66: 'ENABLE_EXTENDED_MSGS',
    0x6F: 'STARTUP_MESSAGE',
}
MSG_ID_CODE = {key: f'{value} (0x{key:02x})' for key, value in _MSG_ID_CODE.items()}


# Reference section 0.5.6.1: Channel Response / Event
MSG_CODE = {
    0x00: 'RESPONSE_NO_ERROR',
    0x01: 'EVENT_RX_SEARCH_TIMEOUT',
    0x02: 'EVENT_RX_FAIL',
    0x03: 'EVENT_TX_FAIL',
    0x04: 'EVENT_TRANSFER_RX_FAILED',
    0x05: 'EVENT_TRANSFER_TX_COMPLETED',
    0x06: 'EVENT_TRANSFER_TX_FAILED',
    0x07: 'EVENT_CHANNEL_CLOSED',
    0x08: 'EVENT_RX_FAIL_GO_TO_SEARCH',
    0x09: 'EVENT_CHANNEL_COLLISION',
    0x0A: 'EVENT_TRANSFER_TX_START',
    0x11: 'EVENT_TRANSFER_NEXT_DATA_BLOCK',
    0x15: 'CHANNEL_IN_WRONG_STATE',
    0x16: 'CHANNEL_NOT_OPENED',
    0x18: 'CHANNEL_ID_NOT_SET',
    0x19: 'CLOSE_ALL_CHANNELS',
    0x1F: 'TRANSFER_IN_PROGRESS',
    0x20: 'TRANSFER_SEQUENCE_NUMBER_ERROR',
    0x21: 'TRANSFER_IN_ERROR',
    0x27: 'MESSAGE_SIZE_EXCEEDS_LIMIT',
    0x28: 'INVALID_MESSAGE',
    0x29: 'INVALID_NETWORK_NUMBER',
    0x30: 'INVALID_LIST_ID',
    0x31: 'INVALID_SCAN_TX_CHANNEL',
    0x33: 'INVALID_PARAMETER_PROVIDED',
    0x34: 'EVENT_SERIAL_QUE_OVERFLOW',
    0x35: 'EVENT_QUE_OVERFLOW',
    0x38: 'ENCRYPT_NEGOTIATION_SUCCESS',
    0x39: 'ENCRYPT_NEGOTIATION_FAIL',
    0x40: 'NVM_FULL_ERROR',
    0x41: 'NVM_WRITE_ERROR',
    0x70: 'USB_STRING_WRITE_FAIL',
    0xAE: 'MSG_SERIAL_ERROR_ID',
}

ANT = 'ANT'
HOST = 'HOST'
BOTH = 'BOTH'


# Message Classes
class ANTPayload(Packet):
    _from = None

    # Intentionally shared across all instances
    _channels = {0: DEVICE_TYPE_SCAN}

    def __init_subclass__(cls, **kwargs):

        # Check packet definition
        assert (
            cls._msg_id in MSG_ID_CODE
        ), f'Assign 0x{cls._msg_id:02x} in MSG_ID_CODE dict'

        assert cls._from in [HOST, ANT, BOTH], 'Assign _from attribute'

        MSG_ID_CLS[cls._msg_id] = cls
        super().__init_subclass__(**kwargs)

    @property
    def name(self):
        return f'{self._from}: {type(self).__name__}'


class ChannelRespEvent(ANTPayload):
    _msg_id = 0x40
    _from = ANT
    fields_desc = [
        ByteField('channel_number', 0),
        XByteEnumField('msg_id', 1, MSG_ID_CODE),
        XByteEnumField('msg_code', 0, MSG_CODE),
    ]


class AssignChannel(ANTPayload):
    _msg_id = 0x42
    _from = HOST
    fields_desc = [
        ByteField('channel_number', 0),
        XByteEnumField(
            'channel_type',
            0,
            {
                0x00: 'Receive Channel (0x00)',
                0x10: 'Transmit Channel (0x10)',
                0x50: 'Transmit Only Channel (0x50)',
                0x40: 'Receive Only Channel (0x40)',
                0x20: 'Shared Bidirectional Receive Channel (0x20)',
                0x30: 'Shared Bidirectional Transmit Channel (0x30)',
            },
        ),
        ByteField('network_number', 0),
        ConditionalField(
            XByteEnumField(
                'extended_assignment',
                0,
                {
                    0x01: 'Background Scanning Enable (0x01)',
                    0x04: 'Frequency Agility Enable (0x04)',
                    0x10: 'Fast Channel Initiation Enable (0x10)',
                    0x20: 'Asynchronous Transmission Enable (0x20)',
                },
            ),
            lambda pkt: pkt.underlayer.msg_length == 4,
        ),
    ]


class SetChannelPeriod(ANTPayload):
    _msg_id = 0x43
    _from = HOST
    fields_desc = [ByteField('channel_number', 0), ShortField('period', 0)]


class SearchTimeout(ANTPayload):
    _msg_id = 0x44
    _from = HOST
    fields_desc = [ByteField('channel_number', 0), ByteField('search_timeout', 0)]


class SetChannelFreq(ANTPayload):
    _msg_id = 0x45
    _from = HOST
    fields_desc = [ByteField('channel_number', 0), ByteField('freq', 0)]


class SetNetworkKey(ANTPayload):
    _msg_id = 0x46
    _from = HOST
    fields_desc = [
        ByteField('network_number', 0),
        FieldListField('network_key', None, XByteField('x', 0), count_from=lambda p: 8),
    ]


class TransmitPower(ANTPayload):
    _msg_id = 0x47
    _from = HOST
    fields_desc = [ByteField('filler', 0), ByteField('transmit_power', 0)]


class ResetSystem(ANTPayload):
    _msg_id = 0x4A
    _from = HOST
    fields_desc = [ByteField('filler', 0)]


class OpenChannel(ANTPayload):
    _msg_id = 0x4B
    _from = HOST
    fields_desc = [ByteField('channel_number', 0)]


class CloseChannel(ANTPayload):
    _msg_id = 0x4C
    _from = HOST
    fields_desc = [ByteField('channel_number', 0)]


class RequestMessage(ANTPayload):
    _msg_id = 0x4D
    _from = HOST
    fields_desc = [
        ByteField('channel_number', 0),
        XByteEnumField('msg_id', 0, MSG_ID_CODE),
        # nvm addr
        # nvm size
    ]


class ScanBroadcastData(OptionalExtended):
    'Scanned broadcast payloads'

    fields_desc = [
        FieldListField('data', None, XByteField('x', 0), count_from=lambda p: 8)
    ]


class BroadcastData(ANTPayload):
    _msg_id = 0x4E
    _from = BOTH

    fields_desc = [ByteField('channel_number', 0)]

    _dtypes = {
        DEVICE_TYPE_SCAN: ScanBroadcastData,
        DEVICE_TYPE_HRM: HRMPayload,
        DEVICE_TYPE_CADENCE: CadencePayload,
        DEVICE_TYPE_FITNESS: FitnessPayload,
    }

    def guess_payload_class(self, pkt):
        res = UndefinedBroadcastData
        device_type = None

        if self.channel_number in self._channels:
            device_type = self._channels[self.channel_number]
        elif self.channel_number != 0:
            log.error(f'Unknown channel number {self.channel_number}')

        if device_type in self._dtypes:
            res = self._dtypes[device_type]
        elif device_type != 0 and device_type is not None:
            log.error(f'Unregistered device type {device_type}')

        return res


class AcknowledgeData(ANTPayload):
    _msg_id = 0x4F
    _from = BOTH
    fields_desc = [ByteField('channel_number', 0)]

    _dtypes = {DEVICE_TYPE_FITNESS: FitnessControlPage}

    def guess_payload_class(self, pkt):
        res = UndefinedControlPage
        device_type = None

        if self.channel_number in self._channels:
            device_type = self._channels[self.channel_number]
        elif self.channel_number != 0:
            log.error(f'Unknown channel number {self.channel_number}')

        if device_type in self._dtypes:
            res = self._dtypes[device_type]
        elif device_type != 0 and device_type is not None:
            log.error(f'Unregistered device type {device_type}')

        return res


class SetChannelID(ANTPayload):
    _msg_id = 0x51
    _from = HOST
    fields_desc = [
        ByteField('channel_number', 0),
        XShortField('device_number', 0),
        ByteEnumField('device_type', 0, ENUM_DEVICE_TYPE),
        ByteField('transmission_type', 0),
    ]

    def post_dissection(self, pkt):
        'Update channel -> device_type dict used to interpret broadcast data'

        if self.channel_number not in self._channels:
            log.info(
                f'Registering new channel {self.channel_number} with device type {self.device_type} and device number {self.device_number}'
            )
            self._channels[self.channel_number] = self.device_type


class UndocumentedC6(ANTPayload):
    _msg_id = 0xC6
    _from = HOST


class DeviceSerialNumber(ANTPayload):
    _msg_id = 0x61
    _from = ANT
    fields_desc = [
        FieldListField(
            'serial_number', None, XByteField('x', 0), count_from=lambda p: 4
        )
    ]


class LPSearchTimeout(ANTPayload):
    _msg_id = 0x63
    _from = HOST
    fields_desc = [ByteField('channel_number', 0), ByteField('search_timeout', 0)]


class StartupMessage(ANTPayload):
    _msg_id = 0x6F
    _from = ANT
    fields_desc = [
        FlagsField(
            'startup_message',
            0,
            8,
            [
                'SUSPEND_RESET',
                'SYNCHRONOUS_RESET',
                'COMMAND_RESET',
                'RESERVED',
                'RESERVED',
                'RESERVED',
                'WATCH_DOG_RESET',
                'HARDWARE_RESET_LINE',
            ],
        )
    ]


class EnableExtMsgs(ANTPayload):
    _msg_id = 0x66
    _from = HOST

    fields_desc = [
        XByteField('filler', 0),
        ByteEnumField('enable', 0, {0x0: 'disabled', 0x1: 'enabled'}),
    ]


class UndefinedPayload(Packet):
    fields_desc = [
        FieldListField(
            'data',
            None,
            XByteField('x', 0),
            count_from=lambda p: p.firstlayer().msg_length,
        )
    ]


class UndefinedBroadcastData(Packet):
    fields_desc = [
        FieldListField(
            'data',
            None,
            XByteField('x', 0),
            count_from=lambda p: p.firstlayer().msg_length - 1,
        )
    ]


class UndefinedControlPage(Packet):
    fields_desc = [
        FieldListField(
            'data',
            None,
            XByteField('x', 0),
            count_from=lambda p: p.firstlayer().msg_length - 1,
        )
    ]


class ANTCS(Field):
    'Special ANT checksum field is at the end of the packet and may have a \x00\x00 bumper.'

    __slots__ = ['bumper']

    def getfield(self, pkt, s):
        val = self.m2i(
            pkt, struct.unpack(self.fmt, s[pkt.msg_length : pkt.msg_length + 1])[0]
        )
        self.bumper = s[pkt.msg_length + 1 :]
        return s[: pkt.msg_length], val

    def addfield(self, pkt, s, val):
        previous_post_build = pkt.post_build
        value = struct.pack(self.fmt, self.i2m(pkt, val))
        bumper = self.bumper

        def _post_build(self, p, pay):
            pay += value
            pay += bumper
            pkt.post_build = previous_post_build
            return previous_post_build(p, pay)

        pkt.post_build = MethodType(_post_build, pkt)
        return s

    def i2repr(self, pkt, x):
        return lhex(self.i2h(pkt, x))


class ANTMessage(Packet):
    fields_desc = [
        XByteField('sync', 0xA4),
        ByteField('msg_length', 0),
        # Should be LenField for auto-calculation?
        # LenField('msg_length', None),
        XByteEnumField('msg_id', 0x0, MSG_ID_CODE),
        ANTCS('checksum', None, fmt='B'),
    ]

    def __init__(self, *args, device_type=None, **kwargs):
        # used for testing to set hard assign channel
        # can't use self because that triggers recursion on the
        # uninitialized packet.
        if device_type is not None:
            pkt = args[0]
            msg_id = pkt[2]
            channel = pkt[3]
            if msg_id in [0x4E, 0x4F] and device_type is not None and device_type != 0:
                ANTPayload._channels[channel] = device_type

        super().__init__(*args, **kwargs)

    @property
    def raw_packet_cache(self):
        return None

    def __setattr__(self, attr, val):
        if attr != 'raw_packet_cache':
            return super().__setattr__(attr, val)

    def guess_payload_class(self, payload):
        if self.msg_id in MSG_ID_CLS:
            return MSG_ID_CLS[self.msg_id]
        else:
            return UndefinedPayload

    def _calc_checksum(self):
        cs = self.sync
        data = bytes(self)[1 : self.msg_length + 3]
        # assert self.checksum != data[-1], f'Checksum data includes checksum: {data}'
        for byte in data:
            cs = cs ^ byte
        return cs

    def post_build(self, pkt, pay):
        cs = self.sync
        data = pkt + pay
        has_bumper = data.endswith(bytes([self.checksum]) + b'\x00\x00')

        for byte in data[1 : self.msg_length + 3]:
            cs = cs ^ byte

        data = data[: self.msg_length + 3] + bytes([cs])
        if has_bumper:
            data += b'\x00\x00'

        return data


def ant_each(data, **kwargs):
    while len(data) > 0:
        ant = ANTMessage(data, **kwargs)
        data = data[len(ant) :]
        yield ant


def ant_map(data, func, **kwargs):
    res = b''
    for ant in ant_each(data, **kwargs):
        res += bytes(func(ant))
    return res
