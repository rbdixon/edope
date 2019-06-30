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
    mass = attr.ib(converter=int)
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

        # Set initial values
        self._watts = 0

    def on_start(self):
        log.info('Initializing XBox controller')

        # Short enough to be responsive but not so short as to ramp up CPU usage
        proxy = pm.get_plugin('proxy')
        proxy.timeout = 0.01

        pygame.init()

        try:
            self._controller = xbox.Controller(0)
            self._clock = pygame.time.Clock()

        except pygame.error:
            log.error('No XBox controller available for slacking!')
            sys.exit(-1)

        self._viz = Visualizer()

    def on_stop(self):
        proxy = pm.get_plugin('proxy')
        proxy.timeout = 1
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

    def set_power(self, ant):
        'Apply the specified watts value to the FitnessPayload data page 25 packet'

        if has_payload(ant, FitnessPayload):
            if ant[FitnessPayload].data_page_number == 25:
                if ant[FitnessPayload].instant_power != self._watts:
                    log.debug(
                        f'Updating FitnessPayload data page 25 to {self._watts} watts'
                    )
                    ant[FitnessPayload].instant_power = max(
                        ant[FitnessPayload].instant_power, self._watts
                    )
        return ant

    def update_watts(self, triggers_raw):
        'Map the stick value to watts'

        new_value = max(int(triggers_raw * self.peak_power_limit * self.mass), 0)
        if new_value != self._watts:
            log.debug(f'Sweating out {new_value} watts now!')
        self._watts = new_value

    @hookimpl
    def usbq_device_modify(self, pkt):
        if is_ant(pkt):
            for cheat in [self.set_power]:
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

            # Read controller values
            buttons = self._controller.get_buttons()
            triggers = self._controller.get_triggers()
            left_stick = self._controller.get_left_stick()
            right_stick = self._controller.get_right_stick()
            pads = self._controller.get_pad()

            # Use controller values to control performance
            self.update_watts(triggers)

            self._viz.draw(buttons, left_stick, right_stick, triggers, pads)
            self._clock.tick()

    @hookimpl
    def usbq_connected(self):
        self.start()

    @hookimpl
    def usbq_disconnected(self):
        if self.is_running:
            self.stop()

    @hookimpl
    def usbq_teardown(self):
        if self.is_running:
            self.stop()


def do_slacker(params):
    plugins = usbq.opts.standard_plugin_options(**params) + [
        (
            'slacker',
            {'mass': params['mass'], 'peak_power_limit': params['peak_power_limit']},
        ),
        ('lookfor', {'usb_id': params['usb_id']}),
    ]
    enable_plugins(pm, plugins)
    proxy = pm.get_plugin('proxy')
    proxy.start()
    USBQEngine().run()
