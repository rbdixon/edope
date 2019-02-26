'''Sniffer using USBQ to intercept ANT+ communications'''

import attr
import logging
import usbq.opts

from pathlib import Path
from usbq.engine import USBQEngine
from usbq.pm import pm, enable_plugins
from usbq.hookspec import hookimpl
from usbq.usbmitm_proto import USBMessageHost, USBMessageDevice
from scapy.all import hexdump, raw

from .ant_proto import ANTMessage, ANTPayload, BroadcastData
from .ant_util import is_ant

log = logging.getLogger(__name__)
__all__ = ['do_sniff']


@attr.s(cmp=False)
class AntSniff:
    'Sniff ANT+ sensor readings'

    _pytest = attr.ib(default=Path('ant_samples.py'))
    _msgs = attr.ib(default=attr.Factory(list))
    _detected = attr.ib(default=False)

    DIR = {USBMessageDevice: 'ANT ->  PC', USBMessageHost: 'PC  -> ANT'}

    def _get_device_type(self, pkt):
        try:
            bd = pkt[BroadcastData]
            return ANTPayload._channels.get(bd.channel_number, None)
        except IndexError:
            pass

    @hookimpl
    def usbq_log_pkt(self, pkt):
        if is_ant(pkt):
            if not self._detected:
                log.info('ANT device connected to USB')
                self._detected = True

            log.debug(repr(pkt.content.data))
            ant_msg = ANTMessage(pkt.content.data)
            log.info(f'{self.DIR[type(pkt)]}: {repr(ant_msg)}')
            self._msgs.append([raw(ant_msg), self._get_device_type(ant_msg)])

    @hookimpl
    def usbq_teardown(self):
        uniq = {}
        with self._pytest.open('w') as f:
            f.write('TEST_DATA = [\n')
            for sample in self._msgs:
                if sample[0] in uniq:
                    continue
                f.write(f'   [{repr(sample[0])},{repr(sample[1])}],\n')
                uniq[sample[0]] = True
            f.write(']\n\n')


def do_sniff(params):
    plugins = usbq.opts.standard_plugin_options(**params) + [('antdump', {})]
    enable_plugins(pm, plugins)
    proxy = pm.get_plugin('proxy')
    proxy.start()
    USBQEngine().run()
