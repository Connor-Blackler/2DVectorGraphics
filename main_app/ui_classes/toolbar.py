from shared_python.shared_math.geometry import Vec2
from ..context_wrapper import ContextWrapper
from .button import Button
from ..helpers import Color


class Toolbar:
    def __init__(self, pos: Vec2, width: float, height: float, btns: list[Button]):
        self.pos = pos
        self.buttons = btns
        self.bg_color = Color(244, 244, 244)
        self.width = width
        self.height = height
        self.margin = 0.0

        self._create_button_positions()

    def _create_button_positions(self):
        buttons_width = sum([btn.width for btn in self.buttons])
        buttons_height = max([btn.height for btn in self.buttons])

        start_x = self.pos.x  # (self.width - buttons_width) // 2
        y = self.pos.y + ((self.height - buttons_height) // 2)

        for i, btn in enumerate(self.buttons):
            x = start_x + \
                sum([self.buttons[j].width for j in range(i)]) + \
                i * self.margin
            btn.set_pos(Vec2(x, y))

    def draw(self, context: ContextWrapper):
        context.set_color(self.bg_color)
        context.draw_rect(self.pos.x, self.pos.y, self.width, self.height)

        for btn in self.buttons:
            btn.draw(context)

    def hit_test(self, pos: Vec2):
        for btn in self.buttons:
            if btn.hit_test(pos):
                return btn
        return None
