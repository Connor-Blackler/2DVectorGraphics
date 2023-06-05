from abc import ABC, abstractmethod
from functools import cached_property
from shared_python.shared_math.geometry import Rect, Vec2, BezierPathA, BezierContour, BezierPath, BezierPoint
from typing import overload
from skia import *
import skia


class ContextPath(ABC):
    def __init__(self, path: BezierPathA, stroke=None, fill=None, stroke_thickness=1.0) -> None:
        super().__init__()

        self._path = path
        self._stroke = stroke
        self._fill = fill
        self._stroke_thickness = stroke_thickness

    @property
    def stroke_color(self) -> Color:
        return self._stroke

    @stroke_color.setter
    def stroke_color(self, color) -> None:
        self._stroke = color

    @property
    def stroke_thickness(self) -> float:
        return self._stroke_thickness

    @stroke_thickness.setter
    def stroke_thickness(self, thickness: float) -> None:
        self._stroke_thickness = thickness

    @property
    def fill_color(self) -> Color:
        return self._fill

    @fill_color.setter
    def fill_color(self, color) -> None:
        self._fill = color

    def set_path(self, path: BezierPathA) -> None:
        self._path = path
        if self.path:
            del self.path

    @abstractmethod
    def translate(self, pos: Vec2) -> None:
        pass

    @abstractmethod
    @cached_property
    def path(self):
        pass


class ContextPathSkia(ContextPath):
    @cached_property
    def path(self):
        ret = []
        for bezier_path in self._path:
            skia_path = skia.Path()

            for contour in bezier_path.contours:
                num_points = len(contour.points)

                for i in range(num_points):
                    current_point = contour.points[i].pos
                    next_point = contour.points[(i + 1) % num_points].pos
                    next_control1 = contour.points[(
                        i + 1) % num_points].control1
                    prev_control2 = contour.points[i].control2

                    if i == 0:
                        skia_path.moveTo(current_point.x, current_point.y)

                    if next_control1 and prev_control2:
                        skia_path.cubicTo(
                            prev_control2.x, prev_control2.y,
                            next_control1.x, next_control1.y,
                            next_point.x, next_point.y
                        )
                    else:
                        skia_path.lineTo(next_point.x, next_point.y)

                if contour.closed:
                    skia_path.close()

            ret.append(skia_path)

        return ret

    def translate(self, pos: Vec2) -> None:
        if self.path:
            for this_path in self.path:
                this_path.offset(pos.x, pos.y)


def path_provider() -> ContextPath:
    return ContextPathSkia


class ContextWrapper(ABC):
    def get_context_path(self) -> ContextPath:
        return ContextPath

    @overload
    def draw_rect(self, r: Rect) -> None:
        pass

    @overload
    def draw_rect(self, x: float, y: float, width: float, height: float) -> None:
        pass

    @abstractmethod
    def draw_circle(self, center: Vec2, radius: float) -> None:
        pass

    @abstractmethod
    def set_color(self, color) -> None:
        pass

    @abstractmethod
    def draw_path(self, path: BezierPathA) -> None:
        pass


class ContextWrapperSkia(ContextWrapper):
    def __init__(self, surface):
        self.surface = surface
        self.paint = skia.Paint()
        self.paint.setAntiAlias(True)

    def get_context_path(self) -> ContextPathSkia:
        return ContextPathSkia

    def set_color(self, color) -> None:
        if not isinstance(color, int):
            color = Color(color.r, color.g, color.b)

        self.paint.setColor(color)

    def draw_circle(self, center: Vec2, radius: float) -> None:
        self.surface.drawCircle(
            center.x, center.y, radius, self.paint)

    @overload
    def draw_rect(self, x: float, y: float, width: float, height: float) -> None:
        self.draw_rect(Rect(x, y, x + width, y + height))

    @overload
    def draw_rect(self, r: Rect) -> None:
        self.paint.setStyle(self.paint.kFill_Style)
        self.surface.drawRect(
            skia.Rect(r.minx, r.miny, r.width(), r.height()), self.paint)

    def draw_rect(self, x: float, y: float, width: float, height: float) -> None:
        self.paint.setStyle(self.paint.kFill_Style)
        rect = skia.Rect(x, y, x + width, y + height)
        self.surface.drawRect(rect, self.paint)

    def draw_path(self, path: ContextPathSkia) -> None:
        for sk_path in path.path:
            if path.fill_color:
                self.paint.setStyle(self.paint.kFill_Style)
                self.set_color(path.fill_color)
                self.surface.drawPath(sk_path, self.paint)

            if path.stroke_color:
                self.paint.setStyle(self.paint.kStroke_Style)
                self.paint.setStrokeWidth(path.stroke_thickness)
                self.set_color(path.stroke_color)
                self.surface.drawPath(sk_path, self.paint)
