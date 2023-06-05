from .scene.scene import Scene
from ..context_wrapper import ContextWrapper
from ..helpers import MOUSE_ACTION
from shared_python.shared_math.geometry import Vec2


class Session():
    def __init__(self) -> None:
        self.scene = Scene()

    def add_shape(self, shape):
        self.scene.add_shape(shape)

    def remove_shape(self, shape):
        self.scene.remove_shape(shape)

    def draw(self, context: ContextWrapper):
        self.scene.draw(context)

    def mouse_action(self, action: MOUSE_ACTION, pos: Vec2) -> bool:
        return self.scene.mouse_action(action, pos)
