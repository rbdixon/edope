import attr
import pygame

from edope.xbox import controller as xbox

__all__ = ['Visualizer']

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 65, 65)
GREEN = (75, 225, 25)
BLUE = (65, 65, 255)
AMBER = (255, 175, 0)
GREY = (175, 175, 175)


@attr.s
class Visualizer:
    #: XBox controller
    _controller = attr.ib()

    def __attrs_post_init__(self):
        size = [600, 670]
        self._screen = pygame.display.set_mode(size)
        pygame.display.set_caption('eDope Controller')

    def display_text(self, text, x, y):
        my_font = pygame.font.Font(None, 30)
        output = my_font.render(text, True, WHITE)
        self._screen.blit(output, [x, y])

    def draw(self):
        self._screen.fill(BLACK)
        pygame.draw.rect(self._screen, GREY, [40, 20, 520, 320], 3)

        # joystick stuff
        pressed = self._controller.get_buttons()

        a_btn = pressed[xbox.A]
        b_btn = pressed[xbox.B]
        x_btn = pressed[xbox.X]
        y_btn = pressed[xbox.Y]
        back = pressed[xbox.BACK]
        start = pressed[xbox.START]
        # guide = pressed[xbox.GUIDE]
        lt_bump = pressed[xbox.LEFT_BUMP]
        rt_bump = pressed[xbox.RIGHT_BUMP]
        lt_stick_btn = pressed[xbox.LEFT_STICK_BTN]
        rt_stick_btn = pressed[xbox.RIGHT_STICK_BTN]

        lt_x, lt_y = self._controller.get_left_stick()
        rt_x, rt_y = self._controller.get_right_stick()

        triggers = self._controller.get_triggers()

        pad_up, pad_right, pad_down, pad_left = self._controller.get_pad()

        # game logic

        # drawing
        self._screen.fill(BLACK)

        ''' controller outline '''
        pygame.draw.rect(self._screen, GREY, [40, 20, 520, 320], 3)

        ''' a, b, x, y '''
        x, y = 450, 120

        if a_btn == 1:
            pygame.draw.ellipse(self._screen, GREEN, [x + 30, y + 60, 25, 25])
        else:
            pygame.draw.ellipse(self._screen, GREEN, [x + 30, y + 60, 25, 25], 2)

        if b_btn == 1:
            pygame.draw.ellipse(self._screen, RED, [x + 60, y + 30, 25, 25])
        else:
            pygame.draw.ellipse(self._screen, RED, [x + 60, y + 30, 25, 25], 2)

        if x_btn == 1:
            pygame.draw.ellipse(self._screen, BLUE, [x, y + 30, 25, 25])
        else:
            pygame.draw.ellipse(self._screen, BLUE, [x, y + 30, 25, 25], 2)

        if y_btn == 1:
            pygame.draw.ellipse(self._screen, AMBER, [x + 30, y, 25, 25])
        else:
            pygame.draw.ellipse(self._screen, AMBER, [x + 30, y, 25, 25], 2)

        ''' back, start '''
        x, y = 250, 145

        if back == 1:
            pygame.draw.ellipse(self._screen, WHITE, [x, y, 25, 20])
        else:
            pygame.draw.ellipse(self._screen, WHITE, [x, y, 25, 20], 2)

        pygame.draw.ellipse(self._screen, GREY, [x + 40, y - 10, 40, 40])

        if start == 1:
            pygame.draw.ellipse(self._screen, WHITE, [x + 95, y, 25, 20])
        else:
            pygame.draw.ellipse(self._screen, WHITE, [x + 95, y, 25, 20], 2)

        ''' bumpers '''
        x, y = 100, 50

        if lt_bump == 1:
            pygame.draw.rect(self._screen, WHITE, [x, 50, y, 25])
        else:
            pygame.draw.rect(self._screen, WHITE, [x, 50, y, 25], 2)

        if rt_bump == 1:
            pygame.draw.rect(self._screen, WHITE, [x + 365, y, 50, 25])
        else:
            pygame.draw.rect(self._screen, WHITE, [x + 365, y, 50, 25], 2)

        ''' triggers '''
        x, y = 210, 60

        trigger_x = x + 100 + round(triggers * 100)
        pygame.draw.line(self._screen, WHITE, [x, y], [x + 200, y])
        pygame.draw.line(self._screen, WHITE, [trigger_x, y - 10], [trigger_x, y + 10])

        ''' left stick '''
        x, y = 65, 100

        left_x = x + 50 + round(lt_x * 50)
        left_y = y + 50 + round(lt_y * 50)

        pygame.draw.line(self._screen, WHITE, [x + 60, y], [x + 60, y + 120], 1)
        pygame.draw.line(self._screen, WHITE, [x, y + 60], [x + 120, y + 60], 1)
        if lt_stick_btn == 0:
            pygame.draw.ellipse(self._screen, WHITE, [left_x, left_y, 20, 20], 2)
        else:
            pygame.draw.ellipse(self._screen, WHITE, [left_x, left_y, 20, 20])

        ''' right stick '''
        x, y = 330, 190

        right_x = x + 50 + round(rt_x * 50)
        right_y = y + 50 + round(rt_y * 50)

        pygame.draw.line(self._screen, WHITE, [x + 60, y], [x + 60, y + 120], 1)
        pygame.draw.line(self._screen, WHITE, [x, y + 60], [x + 120, y + 60], 1)
        if rt_stick_btn == 0:
            pygame.draw.ellipse(self._screen, WHITE, [right_x, right_y, 20, 20], 2)
        else:
            pygame.draw.ellipse(self._screen, WHITE, [right_x, right_y, 20, 20])

        ''' hat '''
        x, y = 180, 200

        pygame.draw.ellipse(self._screen, WHITE, [x, y, 100, 100])
        if pad_up:
            pygame.draw.ellipse(self._screen, GREY, [x + 40, y, 20, 20])
        if pad_right:
            pygame.draw.ellipse(self._screen, GREY, [x + 80, y + 40, 20, 20])
        if pad_down:
            pygame.draw.ellipse(self._screen, GREY, [x + 40, y + 80, 20, 20])
        if pad_left:
            pygame.draw.ellipse(self._screen, GREY, [x, y + 40, 20, 20])

        ''' joystick values '''
        x, y = 50, 370
        self.display_text("BUTTONS", x, y)
        self.display_text("A: {}".format(a_btn), x, y + 25)
        self.display_text("B: {}".format(b_btn), x, y + 50)
        self.display_text("X: {}".format(x_btn), x, y + 75)
        self.display_text("Y: {}".format(y_btn), x, y + 100)
        self.display_text("LB: {}".format(lt_bump), x, y + 125)
        self.display_text("RB: {}".format(rt_bump), x, y + 150)
        self.display_text("Back: {}".format(back), x, y + 175)
        self.display_text("Start: {}".format(start), x, y + 200)
        self.display_text("LT Stick Btn: {}".format(lt_stick_btn), x, y + 225)
        self.display_text("RT Stick Btn: {}".format(rt_stick_btn), x, y + 250)

        self.display_text("AXES", x + 275, y)
        self.display_text(
            "Left Stick: ({}, {})".format(round(lt_x, 2), round(lt_y, 2)),
            x + 275,
            y + 25,
        )
        self.display_text(
            "Right Stick: ({}, {})".format(round(rt_x, 2), round(rt_y, 2)),
            x + 275,
            y + 50,
        )
        self.display_text("Triggers: {}".format(round(triggers, 2)), x + 275, y + 75)

        self.display_text("D-PAD", x + 275, y + 125)
        self.display_text("Up: {}".format(pad_up), x + 275, y + 150)
        self.display_text("Right: {}".format(pad_right), x + 275, y + 175)
        self.display_text("Down: {}".format(pad_down), x + 275, y + 200)
        self.display_text("Left: {}".format(pad_left), x + 275, y + 225)

        pygame.display.flip()
        # update screen
        pygame.display.flip()
