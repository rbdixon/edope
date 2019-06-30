import logging
from collections import defaultdict

import attr
import usbq.opts
from usbq.engine import USBQEngine
from usbq.hookspec import hookimpl
from usbq.pm import enable_plugins
from usbq.pm import pm

from .ant_cadence import CadencePayload
from .ant_fitness import FitnessControlPage
from .ant_fitness import FitnessPayload
from .ant_hrm import HRMPayload
from .ant_proto import ANTMessage
from .ant_util import has_payload
from .ant_util import is_ant

__all__ = ['FitnessMonitor', 'do_monitor']

log = logging.getLogger(__name__)

MONITOR_FIELDS = {
    CadencePayload: ['cadence_event_time', 'cadence_rev_count'],
    HRMPayload: ['heart_rate'],
    FitnessPayload: [
        'instant_cadence',
        'accum_power',
        'wheel_ticks',
        'accum_torque',
        'instant_power',
        'resistance_level',
        'cycle_length',
        'speed',
        'distance_traveled',
    ],
    FitnessControlPage: ['grade'],
}


@attr.s(cmp=False)
class FitnessMonitor:
    def __attrs_post_init__(self):
        self._state = defaultdict(lambda: None)

    @hookimpl
    def usbq_log_pkt(self, pkt):
        if not is_ant(pkt):
            return

        pkt = ANTMessage(pkt.content.data)
        for cls in MONITOR_FIELDS.keys():
            if not has_payload(pkt, cls):
                continue

            for field in MONITOR_FIELDS[cls]:
                value = getattr(pkt[cls], field, None)
                if value is None:
                    continue

                if self._state[(cls, field)] != value:
                    log.info(f'{cls.__name__}.{field} = {value}')
                    self._state[(cls, field)] = value


def do_monitor(params):
    plugins = usbq.opts.standard_plugin_options(**params) + [
        ('monitor', {}),
        ('lookfor', {'usb_id': params['usb_id']}),
    ]
    enable_plugins(pm, plugins)
    proxy = pm.get_plugin('proxy')
    proxy.start()
    USBQEngine().run()
