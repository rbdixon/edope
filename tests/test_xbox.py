import logging

import pygame
import pytest

from edope.xbox.controller import Controller

log = logging.getLogger(__name__)

# pygame.quit()


@pytest.fixture(autouse=True)
def setup():
    pygame.init()
    yield
    pygame.quit()


@pytest.mark.timeout(30)
def test_controller():

    try:
        controller = Controller(0)
    except pygame.error:
        pytest.skip('No XBox controller available for test')

    clock = pygame.time.Clock()
    done = False

    log.warning('Hit a key on the xbox controller')
    while not done:
        for event in pygame.event.get():
            assert event.type != pygame.QUIT, 'pygame loop quit before button press'

        if any(controller.get_buttons()):
            return

        clock.tick()
