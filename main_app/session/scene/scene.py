from shared_python.shared_math.geometry import Vec2
from ...context_wrapper import ContextWrapper
from ...helpers import MOUSE_ACTION
from .shapes.shapes import Shape


class draggable():
    def __init__(self, start_pos: Vec2, dragging_shape: Shape) -> None:
        self.current_pos = start_pos
        self.shape = dragging_shape

    def work(self, pos: Vec2):
        distance = pos - self.current_pos
        self.current_pos = pos
        self.shape.translate(distance)


class Scene:
    def __init__(self):
        self.shapes = []
        self.draggable = None
        self.selected = None

    def add_shape(self, shape):
        self.shapes.append(shape)

    def remove_shape(self, shape):
        self.shapes.remove(shape)

    def draw(self, context: ContextWrapper):
        for shape in self.shapes:
            shape.draw(context)

    def mouse_action(self, action: MOUSE_ACTION, pos: Vec2) -> bool:
        match action:
            case MOUSE_ACTION.LEFT_CLICK_DOWN:
                if self.selected is None:
                    for this_shape in self.shapes:
                        if this_shape.contains(pos):
                            self.selected = this_shape
                            return True

            case MOUSE_ACTION.LEFT_CLICK_DRAG:
                if self.selected is None:
                    return False

                if self.draggable is None:
                    self.draggable = draggable(pos, self.selected)
                else:
                    self.draggable.work(pos)

            case MOUSE_ACTION.LEFT_CLICK_UP:
                self.draggable = None
                self.selected = None
