import pytest

from scapy.all import *
from edope.ant_common import CS
from edope.ant_proto import (
    ANTMessage,
    ANTPayload,
    BroadcastData,
    UndefinedBroadcastData,
    ant_each,
    ant_map,
)
from edope.ant_fitness import *
from edope.ant_hrm import *
from edope.ant_util import has_payload

from ant_samples import TEST_DATA

DEVICE = {17: 'fitness', 120: 'hrm', 122: 'cadence'}


def make_id(val):
    return DEVICE.get(val, val)


@pytest.mark.parametrize('msg,device_type', TEST_DATA, ids=make_id)
def test_decode_ant(msg, device_type):
    pkt = ANTMessage(msg, device_type=device_type)

    print()
    hexdump(pkt)
    print(repr(pkt))
    pkt.show()

    # assert pkt[CS] is not None
    assert pkt.checksum is not None
    assert bytes(pkt) == msg
    assert pkt._calc_checksum() == pkt.checksum

    # with pytest.raises(IndexError):
    #     pkt[Raw]


@pytest.mark.parametrize(
    'msg,device_type',
    filter(lambda pkt_dt: pkt_dt[1] not in [None, 0], TEST_DATA),
    ids=make_id,
)
def test_broadcast_decoded(msg, device_type):
    pkt = ANTMessage(msg, device_type=device_type)
    assert ANTPayload._channels[pkt[BroadcastData].channel_number] == device_type
    assert not has_payload(pkt, UndefinedBroadcastData)


@pytest.mark.parametrize(
    'msg,device_type', filter(lambda pkt_dt: pkt_dt[1] == 120, TEST_DATA), ids=make_id
)
def test_broadcast_modify_hrm(msg, device_type):
    pkt = ANTMessage(msg, device_type=device_type)
    pkt.show()
    assert pkt._calc_checksum() == pkt.checksum

    pkt[HRMPayload].heart_rate = 0xFF
    assert raw(pkt) != msg

    new_pkt = ANTMessage(raw(pkt), device_type=device_type)
    assert new_pkt.checksum == new_pkt._calc_checksum()


@pytest.mark.parametrize(
    'msg,device_type', filter(lambda pkt_dt: pkt_dt[1] == 17, TEST_DATA), ids=make_id
)
@pytest.mark.parametrize(
    'target_power', [0x0, 0xF, 0xFF, 0xF0, 0xF00, 0xF0F, 0xAAA, 0x555]
)
@pytest.mark.parametrize('trainer_status', [0x0, 0x1, 0x2, 0x3])
def test_broadcast_modify_power(msg, device_type, target_power, trainer_status):
    pkt = ANTMessage(msg, device_type=device_type)
    assert pkt._calc_checksum() == pkt.checksum

    if pkt[FitnessPayload].data_page_number != 25:
        return

    pkt[FitnessPayload].instant_power = target_power
    pkt[FitnessPayload].trainer_status = trainer_status
    pkt.show()
    assert bytes(pkt) != msg

    new_pkt = ANTMessage(bytes(pkt), device_type=device_type)
    assert new_pkt.checksum == new_pkt._calc_checksum()
    assert new_pkt[FitnessPayload].instant_power == target_power
    assert new_pkt[FitnessPayload].trainer_status == trainer_status

    assert new_pkt[FitnessPayload].target_power == pkt[FitnessPayload].target_power
    assert new_pkt[FitnessPayload].accum_power == pkt[FitnessPayload].accum_power


@pytest.mark.parametrize(
    'msg,device_type', filter(lambda pkt_dt: pkt_dt[1] == 17, TEST_DATA), ids=make_id
)
def test_broadcast_modify_resistance(msg, device_type):
    pkt = ANTMessage(msg, device_type=device_type)

    if pkt[FitnessPayload].data_page_number == 48:
        assert False


@pytest.mark.parametrize(
    'msg',
    [
        b'\xa4\x0eN\x01\x03\x0b\x04\x08[\x81\xe1:\x80+\x1fx\x01-\xa4\x03@\x00c\x00\x84\xa4\x03@\x00D\x00\xa3'
    ],
)
def test_triple_ant(msg):
    count = 0
    print()

    def showme(ant):
        nonlocal count

        ant.show()
        count += 1
        return ant

    res = ant_map(msg, showme)

    assert res == msg
    assert count == 3

