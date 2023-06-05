from __future__ import annotations
import uuid
import math
from ....context_wrapper import ContextWrapper, path_provider
from ....helpers import Color
from shared_python.shared_math.geometry import Vec2, BezierPathA, BezierPath, BezierContour, BezierPoint


class Shape:
    def __init__(self):
        self.id = uuid.uuid4()
        self._path = BezierPathA()
        self.stroke = Color(0, 0, 255)
        self.stroke_thickness = 3.0
        self.fill = Color(255, 0, 0)
        self.context_path = path_provider()(
            self.path, self.stroke, self.fill, self.stroke_thickness)

    @property
    def path(self) -> BezierPathA:
        return self._path

    @path.setter
    def path(self, path: BezierPathA) -> None:
        self._path = path
        self.context_path.set_path(path)

    def contains(self, pos: Vec2) -> bool:
        for path in self.context_path.path:
            if path.contains(pos.x, pos.y):
                return True

        return False

    def translate(self, pos: Vec2):
        self.path.translate(pos)
        self.context_path.translate(pos)

    def draw(self, context: ContextWrapper):
        context.set_color(self.color)
        context.draw_path(self.context_path)

    @classmethod
    def construct_polygon(cls, origin: Vec2, radius: float, sides: int, color: Color) -> Shape:
        ret = Shape()
        ret.color = color

        path = BezierPath()
        contour = BezierContour()
        contour.closed = True

        ang = -math.pi / 2
        ang_step = 2 * math.pi / sides
        for _ in range(sides):
            x = math.cos(ang) * radius + origin.x
            y = math.sin(ang) * radius + origin.y
            p = BezierPoint(Vec2(x, y))
            contour.add_point(p)
            ang += ang_step

        path.add_contour(contour)
        ret.path.paths.append(path)

        return ret

    @classmethod
    def construct_circle(cls, center: Vec2, radius: float, color: Color) -> Shape:
        """
        Construction based off: https://www.tinaja.com/glib/ellipse4.pdf
        """
        ret = Shape()
        ret.color = color

        path = BezierPath()
        contour = BezierContour()

        magic = 0.551784

        # Create the four quarters of the circle
        p1 = center + Vec2(radius, 0)
        p2 = center + Vec2(0, radius)
        p3 = center + Vec2(-radius, 0)
        p4 = center + Vec2(0, -radius)
        quarter_points = [
            (p1, p1 + Vec2(0, -magic * radius), p1 + Vec2(0, magic * radius)),
            (p2, p2 + Vec2(magic * radius, 0), p2 + Vec2(-magic * radius, 0)),
            (p3, p3 + Vec2(0, magic * radius), p3 + Vec2(0, -magic * radius)),
            (p4, p4 + Vec2(-magic * radius, 0), p4 + Vec2(magic * radius, 0)),
        ]

        for start_point, control1, control2 in quarter_points:
            end_point = start_point

            start = BezierPoint(start_point, control1, control2)
            contour.add_point(start)

        path.add_contour(contour)

        patha = BezierPathA()
        patha.paths.append(path)
        ret.path = patha

        contour.closed = True
        return ret


class ShapeCircle(Shape):
    def __init__(self, pos: Vec2, radius: float, color: Color):
        super(Shape, self).__init__()

        self.pos = pos
        self.radius = radius
        self.color = color

    def contains(self, pos: Vec2):
        distance = ((pos.x - self.pos.x) ** 2 +
                    (pos.y - self.pos.y) ** 2) ** 0.5
        return distance <= self.radius

    def translate(self, pos: Vec2):
        self.pos.translate(pos)

    def draw(self, context: ContextWrapper):
        context.set_color(self.color)
        context.draw_circle(self.pos, self.radius)
