import logging
from scapy.all import *
from .ant_common import OptionalExtended

log = logging.getLogger(__name__)

DEVICE_TYPE_FITNESS = 17

__all__ = ['DEVICE_TYPE_FITNESS', 'FitnessPayload', 'FitnessControlPage']

# Pages
# 16: General FE data
# 17: General Settings Page
# 26: Specific Trainer Torque Data
# 80: Manufacturer information
# 81: Product information


class InstantPowerField(LEShortField):
    def getfield(self, pkt, s):
        val = self.m2i(pkt, struct.unpack(self.fmt, s[0:2])[0] & 0xFFF)
        # Don't consume whole pkt so that Trainer Status Bit field can use low order bits
        return s[1:], val

    def addfield(self, pkt, s, val):
        value = struct.pack(self.fmt, self.i2m(pkt, val & 0xFFF))
        return s + value


class TSBField(Field):
    def getfield(self, pkt, s):
        val = self.m2i(pkt, struct.unpack('B', s[0:1])[0])
        return s[1:], val

    def addfield(self, pkt, s, val):
        ip_msn = struct.unpack('B', s[-1:])[0] & 0xF
        value = struct.pack('B', self.i2m(pkt, val) | ip_msn)
        return s[:-1] + value

    def m2i(self, pkt, val):
        return val >> 4

    def i2m(self, pkt, val):
        return val << 4


class FitnessPayload(OptionalExtended):
    fields_desc = (
        [ByteField('data_page_number', None)]
        + [
            ConditionalField(f, lambda p: p.data_page_number == 16)
            for f in [
                ByteEnumField('equip_type', 0, {}),
                ByteField('elapsed_time', 0),
                ByteField('distance_traveled', 0),
                LEShortField('speed', 0),
                ByteField('heart_rate', 0),
                BitField('capabilities', 0, 4),
                BitField('fe_status', 0, 4),
            ]
        ]
        + [
            ConditionalField(f, lambda p: p.data_page_number == 17)
            for f in [
                ByteField('reserved_1', 0),
                ByteField('reserved_2', 0),
                ByteField('cycle_length', 0),
                LEShortField('incline', 0),
                ByteField('resistance_level', 0),
                BitField('capabilities', 0, 4),
                BitField('fe_status', 0, 4),
            ]
        ]
        + [
            ConditionalField(f, lambda p: p.data_page_number == 25)
            for f in [
                ByteField('update_event_count', 0),
                ByteField('instant_cadence', 0),
                LEShortField('accum_power', 0),
                InstantPowerField('instant_power', 0),
                TSBField('trainer_status', 0),
                BitEnumField(
                    'target_power',
                    0,
                    2,
                    {
                        0x0: 'at_target_power',
                        0x1: 'speed_too_low',
                        0x2: 'speed_too_high',
                        0x3: 'undetermined',
                    },
                ),
                BitField('reserved', 0, 2),
                BitEnumField(
                    'hr_data_source',
                    0,
                    2,
                    {0x0: 'invalid', 0x1: 'ANT+', 0x2: 'HRM', 0x3: 'Contact Sensor'},
                ),
                BitEnumField(
                    'distance_traveled_enabled', 0, 1, {0x0: 'no', 0x1: 'yes'}
                ),
                BitEnumField(
                    'speed_flag', 0, 1, {0x0: 'real_speed', 0x1: 'virtual_speed'}
                ),
            ]
        ]
        + [
            ConditionalField(f, lambda p: p.data_page_number == 26)
            for f in [
                ByteField('update_event_count', 0),
                ByteField('wheel_ticks', 0),
                LEShortField('wheel_period', 0),
                LEShortField('accum_torque', 0),
                BitField('capabilities', 0, 4),
                BitField('fe_status', 0, 4),
            ]
        ]
        + [
            ConditionalField(f, lambda p: p.data_page_number == 80)
            for f in [
                ByteField('reserved1', 0xFF),
                ByteField('reserved2', 0xFF),
                ByteField('hw_revision', 0),
                LEShortField('manufacturer_id', 0),
                LEShortField('model_number', 0),
            ]
        ]
        + [
            ConditionalField(f, lambda p: p.data_page_number == 81)
            for f in [
                ByteField('reserved', 0xFF),
                ByteField('sw_revision_supplemental', 0),
                ByteField('sw_revision', 0),
                LEIntField('serial_number', 0),
            ]
        ]
    )

    def post_dissection(self, pkt):
        if self.data_page_number not in [16, 17, 25, 26, 80, 81]:
            msg = f'Unknown fitness data page {self.data_page_number}'
            log.error(msg)


class FitnessControlPage(Packet):
    fields_desc = [ByteField('data_page_number', None)] + [
        ConditionalField(f, lambda p: p.data_page_number == 51)
        for f in [
            FieldListField('reserved', 0, ByteField('x', 0), count_from=lambda p: 4),
            LEShortField('grade', 0),
            ByteField('coeff_roll', 0),
        ]
    ]
