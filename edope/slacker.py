import contextlib
import logging
import sys

import attr
import usbq.opts

with contextlib.redirect_stdout(None):
    import pygame

from edope.xbox import controller as xbox
from edope.xbox.visualizer import Visualizer
from usbq.engine import USBQEngine
from usbq.pm import enable_plugins
from usbq.pm import pm
from usbq.hookspec import hookimpl
from statemachine import State
from statemachine import StateMachine

from .ant_fitness import FitnessControlPage
from .ant_fitness import FitnessPayload

# from .ant_hrm import HRMPayload
from .ant_proto import ant_map
from .ant_util import has_payload
from .ant_util import is_ant

log = logging.getLogger(__name__)

__all__ = ['do_slacker']


@attr.s(cmp=False)
class SlackerMode(StateMachine):
    weight = attr.ib(converter=int)
    peak_power_limit = attr.ib(converter=float)

    FLAT = 0x4E20

    # States
    idle = State('idle', initial=True)
    running = State('running')

    # Valid state transitions
    start = idle.to(running)
    stop = running.to(idle)

    def __attrs_post_init__(self):
        # Workaround to mesh attr and StateMachine
        super().__init__()

        # Short enough to be responsive but not so short as to ramp up CPU usage
        proxy = pm.get_plugin('proxy')
        proxy.timeout = 0.01

        self.start()

    def on_start(self):
        log.info('Initializing XBox controller')
        pygame.init()

        try:
            self._controller = xbox.Controller(0)
            self._clock = pygame.time.Clock()

        except pygame.error:
            log.error('No XBox controller available for slacking!')
            sys.exit(-1)

        self._viz = Visualizer(controller=self._controller)

    def on_stop(self):
        pygame.quit()

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

    # @hookimpl
    def usbq_device_modify(self, pkt):
        if is_ant(pkt):
            for cheat in [self.enforce_peak_power_limit]:
                pkt.content.data = ant_map(pkt.content.data, cheat)

    # @hookimpl
    def usbq_host_modify(self, pkt):
        if is_ant(pkt):
            for cheat in [self.make_flat]:
                pkt.content.data = ant_map(pkt.content.data, cheat)

    @hookimpl
    def usbq_tick(self):
        if self.is_running:
            # No event processing but must call
            # to ensure that controller events are
            # captured.
            pygame.event.get()

            buttons = self._controller.get_buttons()
            # triggers = self._controller.get_triggers()
            if any(buttons):
                log.info('Controller button pressed')

            self._viz.draw()
            self._clock.tick()

    @hookimpl
    def usbq_teardown(self):
        self.stop()


def do_slacker(params):
    plugins = usbq.opts.standard_plugin_options(**params) + [
        (
            'slacker',
            {
                'weight': params['weight'],
                'peak_power_limit': params['peak_power_limit'],
            },
        )
    ]
    enable_plugins(pm, plugins)
    proxy = pm.get_plugin('proxy')
    proxy.start()
    USBQEngine().run()
