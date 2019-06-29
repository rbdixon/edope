import logging

import attr
import usbq.opts
from usbq.engine import USBQEngine
from usbq.hookspec import hookimpl
from usbq.pm import enable_plugins
from usbq.pm import pm

from .ant_fitness import FitnessControlPage
from .ant_fitness import FitnessPayload
from .ant_proto import ant_map
from .ant_util import has_payload
from .ant_util import is_ant

log = logging.getLogger(__name__)

__all__ = ['do_epo']


@attr.s(cmp=False)
class EPOMode:
    mass = attr.ib(converter=int)
    power_boost = attr.ib(converter=float)
    peak_power_limit = attr.ib(converter=float)
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
                limit = int(self.mass * self.peak_power_limit)

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

    @hookimpl
    def usbq_device_modify(self, pkt):
        if is_ant(pkt):
            for cheat in [self.moar_power, self.enforce_peak_power_limit]:
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
                'mass': params['mass'],
                'power_boost': params['power_boost'],
                'peak_power_limit': params['peak_power_limit'],
                'flat': params['flat'],
            },
        )
    ]
    enable_plugins(pm, plugins)
    proxy = pm.get_plugin('proxy')
    proxy.start()
    USBQEngine().run()
