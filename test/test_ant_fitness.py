import pytest
from scapy.all import Packet

from edope.ant_fitness import FitnessControlPage
from edope.ant_fitness import InstantPowerField
from edope.ant_fitness import TSBField
from edope.ant_proto import ANTMessage


@pytest.mark.parametrize(
    'ipval, expected',
    [
        [0x0, b'\x00\x00'],
        [0xF, b'\x0F\x00'],
        [0xFF, b'\xFF\x00'],
        [0xFFF, b'\xFF\x0F'],
        [0xFFFF, b'\xFF\x0F'],
    ],
)
def test_instant_power(ipval, expected):
    f = InstantPowerField('test', 0)
    pkt = Packet()
    pay = f.addfield(pkt, b'', ipval)
    assert pay == expected

    rem, val = f.getfield(pkt, expected)
    assert rem == expected[1:]
    assert val == ipval & 0xFFF


@pytest.mark.parametrize(
    'tsbval, expected', [[0x0, b'\x00\x00'], [0x1, b'\x00\x10'], [0xF, b'\x00\xF0']]
)
def test_tsb(tsbval, expected):
    f = TSBField('test', 0)
    pkt = Packet()
    pay = f.addfield(pkt, b'\x00\x00', tsbval)
    assert pay == expected

    rem, val = f.getfield(pkt, expected[1:])
    assert rem == b''
    assert val == tsbval


@pytest.mark.parametrize(
    'ipval, tsbval, expected',
    [
        [0x0, 0x0, b'\x00\x00'],
        [0xFF, 0x1, b'\xFF\x10'],
        [0xFFF, 0x0, b'\xFF\x0F'],
        [0xFFF, 0xA, b'\xFF\xAF'],
    ],
)
def test_ip_tsb(ipval, tsbval, expected):
    f0 = InstantPowerField('test', 0)
    f1 = TSBField('test', 0)
    pkt = Packet()
    pay = f0.addfield(pkt, b'', ipval)
    pay = f1.addfield(pkt, pay, tsbval)
    assert pay == expected


@pytest.mark.parametrize(
    'msg',
    [
        b'\xa4\tO\x013\xff\xff\xff\xff\xc5O\xff\xa5\x00\x00',
        b'\xa4\tO\x013\xff\xff\xff\xff\x8fO\xff\xef\x00\x00',
    ],
)
def test_track_resistance(msg):
    ant = ANTMessage(msg, device_type=17)
    ant.show()
    assert ant[FitnessControlPage] is not None

    ant[FitnessControlPage].grade = 0xA5A6
    assert b'\xa6\xa5' in bytes(ant)
