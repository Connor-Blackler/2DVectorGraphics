from enum import Enum, auto


class MOUSE_ACTION(Enum):
    LEFT_CLICK_DOWN = auto(),
    LEFT_CLICK_DRAG = auto(),
    LEFT_CLICK_UP = auto(),
    RIGHT_CLICK_DOWN = auto(),


class Color():
    def __init__(self, r: int, g: int, b: int) -> None:
        self.r = r
        self.g = g
        self.b = b
