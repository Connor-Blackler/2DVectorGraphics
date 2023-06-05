from shared_python.shared_math.geometry import Vec2
from ..context_wrapper import ContextWrapper
from ..helpers import Color


class Button:
    def __init__(self, id: str, width: float, height: float, color: Color):
        self.pos = None
        self.width = width
        self.height = height
        self.color = color
        self.clicked = False
        self.selected = False

    def set_pos(self, pos: Vec2):
        self.pos = pos

    def hit_test(self, pos: Vec2):
        return (
            self.pos.x <= pos.x <= self.pos.x + self.width and
            self.pos.y <= pos.y <= self.pos.y + self.height
        )

    def draw(self, context: ContextWrapper):
        if self.selected:
            context.set_color(Color(255, 0, 255))
        elif self.clicked:
            context.set_color(Color(77, 77, 77))
        else:
            context.set_color(self.color)

        context.draw_rect(self.pos.x, self.pos.y, self.width, self.height)

    def click(self):
        self.selected = not self.selected
