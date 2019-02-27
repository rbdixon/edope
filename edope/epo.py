import attr
import logging
import usbq.opts
import random

from collections import deque
from usbq.engine import USBQEngine
from usbq.pm import pm, enable_plugins
from usbq.hookspec import hookimpl

from .ant_proto import ANTMessage, ant_map
from .ant_util import is_ant, has_payload
from .ant_fitness import FitnessPayload, FitnessControlPage
from .ant_hrm import HRMPayload
from .ant_cadence import CadencePayload

log = logging.getLogger(__name__)

__all__ = ['do_epo']


class LastVal(deque):
    def __init__(self, *args, size=10, no_val=0, max_val=0xFFFF, **kwargs):
        super().__init__(*args, **kwargs)
        self.max_size = size
        self.no_val = no_val
        self.max_val = max_val

    def append(self, val):
        if val not in [0, None]:
            super().append(val)

        if len(self) > self.max_size:
            self.popleft()

    def fuzz(self, val, factor=0.1):
        fval = round(val * factor)
        return val + random.randint(-fval, fval)

    def avg(self):
        if len(self) == 0:
            return self.no_val

        return min(self.max_val, self.fuzz(round(sum(self) / len(self))))


CC_FIELDS = {HRMPayload: ['heart_rate'], FitnessPayload: ['instant_power']}

CACHE = {
    (cls, field): LastVal() for cls in CC_FIELDS.keys() for field in CC_FIELDS[cls]
}


@attr.s(cmp=False)
class EPOMode:
    weight = attr.ib(converter=int)
    power_boost = attr.ib(converter=float)
    peak_power_limit = attr.ib(converter=float)
    cruise_control = attr.ib(converter=bool, default=True)
    flat = attr.ib(converter=bool, default=True)

    FLAT = 0x4E20

    def make_flat(self, ant):
        if self.flat:
            if has_payload(ant, FitnessControlPage):
                if (
                    ant[FitnessControlPage].grade != self.FLAT
                    and ant[FitnessControlPage].grade is not None
                ):
                    log.debug('GROG MAKE ROAD FLAT!')
                    ant[FitnessControlPage].grade = min(
                        self.FLAT, ant[FitnessControlPage].grade
                    )
        return ant

    def enforce_peak_power_limit(self, ant):
        if has_payload(ant, FitnessPayload) and self.peak_power_limit > 0:
            if ant[FitnessPayload].data_page_number == 25:
                limit = int(self.weight * self.peak_power_limit)

                if ant[FitnessPayload].instant_power > limit:
                    log.warning(
                        f'Limiting power to specified peak power limit of {self.peak_power_limit} w/kg ({limit} watts).'
                    )
                    ant[FitnessPayload].instant_power = min(
                        ant[FitnessPayload].instant_power, limit
                    )
        return ant

    def moar_power(self, ant):
        if has_payload(ant, FitnessPayload) and self.power_boost > 0:
            if ant[FitnessPayload].data_page_number == 25:
                if ant[FitnessPayload].instant_power != 0:
                    new_power = int(
                        ant[FitnessPayload].instant_power * self.power_boost
                    )
                    log.debug(
                        f'Applying power boost: {ant[FitnessPayload].instant_power} => {new_power} watts'
                    )
                    ant[FitnessPayload].instant_power = new_power
        return ant

    def crusin(self, ant):
        if self.cruise_control:
            for cls in CC_FIELDS.keys():
                if has_payload(ant, cls):
                    for field in CC_FIELDS[cls]:
                        value = getattr(ant[cls], field)
                        cache = CACHE[(cls, field)]
                        cache.append(value)

                        new_val = cache.avg()

                        if value != new_val:
                            log.debug(f'Cruise-control: {field} => {new_val}')
                            setattr(ant[cls], field, new_val)

        return ant

    @hookimpl
    def usbq_device_modify(self, pkt):
        if is_ant(pkt):
            for cheat in [self.moar_power, self.crusin, self.enforce_peak_power_limit]:
                pkt.content.data = ant_map(pkt.content.data, cheat)

    @hookimpl
    def usbq_host_modify(self, pkt):
        if is_ant(pkt):
            for cheat in [self.make_flat]:
                pkt.content.data = ant_map(pkt.content.data, cheat)


def do_epo(params):
    plugins = usbq.opts.standard_plugin_options(**params) + [
        (
            'epo',
            {
                'weight': params['weight'],
                'power_boost': params['power_boost'],
                'peak_power_limit': params['peak_power_limit'],
                'cruise_control': params['cruise_control'],
                'flat': params['flat'],
            },
        )
    ]
    enable_plugins(pm, plugins)
    proxy = pm.get_plugin('proxy')
    proxy.start()
    USBQEngine().run()
