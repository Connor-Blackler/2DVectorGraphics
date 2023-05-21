from __future__ import annotations
import contextlib
import glfw
from OpenGL import GL
import skia
from enum import Enum, auto
from skia import *
import uuid
from shared_python.shared_math.geometry import vec2

WIDTH, HEIGHT = 640, 480
UI_TOP_BAR_HEIGHT = 32
BUTTON_SIZE = 20
BUTTON_MARGIN = 6


class MOUSE_ACTION(Enum):
    LEFT_CLICK_DOWN = auto(),
    LEFT_CLICK_DRAG = auto(),
    LEFT_CLICK_UP = auto(),
    RIGHT_CLICK_DOWN = auto(),


class draggable():
    def __init__(self, start_pos: vec2, dragging_shape: shape) -> None:
        self.current_pos = start_pos
        self.shape = dragging_shape

    def work(self, pos: vec2):
        distance = pos - self.current_pos
        self.current_pos = pos
        self.shape.translate(distance)


class Button:
    def __init__(self, id: str, size: float, color: Color):
        self.pos = None
        self.size = size
        self.color = color
        self.clicked = False
        self.selected = False

    def set_pos(self, pos: vec2):
        self.pos = pos

    def hit_test(self, pos: vec2):
        return (
            self.pos.x <= pos.x <= self.pos.x + self.size and
            self.pos.y <= pos.y <= self.pos.y + self.size
        )

    def draw(self, canvas):
        paint = skia.Paint()

        if self.selected:
            paint.setColor(skia.ColorBLUE)
        elif self.clicked:
            paint.setColor(skia.ColorGRAY)
        else:
            paint.setColor(self.color)
        canvas.drawRect(skia.Rect.MakeXYWH(
            self.pos.x, self.pos.y, BUTTON_SIZE, BUTTON_SIZE), paint)

    def click(self):
        self.selected = not self.selected


class DrawArea:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.scene = Scene()
        self.toolbar = Toolbar(
            vec2(0, HEIGHT - UI_TOP_BAR_HEIGHT),
            [Button("select", BUTTON_SIZE, Color(200, 200, 200)),
             Button("delete", BUTTON_SIZE, Color(200, 200, 200))])

    def add_shape(self, shape):
        self.scene.add_shape(shape)

    def remove_shape(self, shape):
        self.scene.remove_shape(shape)

    def draw(self, canvas):
        self.scene.draw(canvas)
        self.toolbar.draw(canvas)

    def mouse_button_callback(self, window, button, action, mods):
        x, y = glfw.get_cursor_pos(window)
        pos = vec2(x, y)

        if button == glfw.MOUSE_BUTTON_LEFT:
            if action == glfw.PRESS:
                clicked_button = self.toolbar.hit_test(pos)
                if clicked_button:
                    clicked_button.click()
                else:
                    self.scene.mouse_action(MOUSE_ACTION.LEFT_CLICK_DOWN, pos)

            elif action == glfw.RELEASE:
                self.scene.mouse_action(MOUSE_ACTION.LEFT_CLICK_UP, pos)

        if button == glfw.MOUSE_BUTTON_RIGHT:
            if action == glfw.RELEASE:
                self.add_shape(Shape(pos, 40, color))

    def cursor_pos_callback(self, window, xpos, ypos):
        if glfw.get_mouse_button(window, glfw.MOUSE_BUTTON_LEFT) == glfw.PRESS:
            pos = vec2(xpos, ypos)
            self.scene.mouse_action(MOUSE_ACTION.LEFT_CLICK_DRAG, pos)

    @staticmethod
    @contextlib.contextmanager
    def skia_surface(window):
        context = GrDirectContext.MakeGL()
        (fb_width, fb_height) = glfw.get_framebuffer_size(window)
        backend_render_target = GrBackendRenderTarget(
            fb_width,
            fb_height,
            0,  # sampleCnt
            0,  # stencilBits
            GrGLFramebufferInfo(0, GL.GL_RGBA8))
        surface = skia.Surface.MakeFromBackendRenderTarget(
            context, backend_render_target, kBottomLeft_GrSurfaceOrigin,
            kRGBA_8888_ColorType, ColorSpace.MakeSRGB())
        assert surface is not None
        yield surface
        context.abandonContext()


class Toolbar:
    def __init__(self, pos: vec2, btns: list[Button]):
        self.pos = pos
        self.buttons = btns

        self._create_button_positions()

    def _create_button_positions(self):
        button_count = len(self.buttons)

        button_width = BUTTON_SIZE * button_count + \
            BUTTON_MARGIN * (button_count + 1)

        start_x = (WIDTH - button_width) // 2
        y = (UI_TOP_BAR_HEIGHT - BUTTON_SIZE) // 2

        for i, btn in enumerate(self.buttons):
            x = start_x + i * (BUTTON_SIZE + BUTTON_MARGIN)
            btn.set_pos(vec2(x, y))

    def draw(self, canvas):
        paint = skia.Paint()
        paint.setColor(skia.ColorGRAY)
        canvas.drawRect(skia.Rect.MakeXYWH(
            self.pos.x, self.pos.y + (HEIGHT - UI_TOP_BAR_HEIGHT), WIDTH, UI_TOP_BAR_HEIGHT), paint)

        for btn in self.buttons:
            btn.draw(canvas)

    def hit_test(self, pos: vec2):
        for btn in self.buttons:
            if btn.hit_test(pos):
                return btn
        return None


class Shape:
    def __init__(self, pos: vec2, radius: float, color: Color):
        self.pos = pos
        self.radius = radius
        self.color = color
        self.id = uuid.uuid4()

    def contains(self, pos: vec2):
        distance = ((pos.x - self.pos.x) ** 2 +
                    (pos.y - self.pos.y) ** 2) ** 0.5
        return distance <= self.radius

    def translate(self, pos: vec2):
        self.pos.translate(pos)

    def draw(self, canvas):
        canvas.drawCircle(self.pos.x, self.pos.y, self.radius,
                          skia.Paint(Color=self.color))


class Scene:
    def __init__(self):
        self.shapes = []
        self.draggable = None
        self.selected = None

    def add_shape(self, shape):
        self.shapes.append(shape)

    def remove_shape(self, shape):
        self.shapes.remove(shape)

    def draw(self, canvas):
        for shape in self.shapes:
            shape.draw(canvas)

    def mouse_action(self, action: MOUSE_ACTION, pos: vec2) -> bool:
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


class Wmain:
    def __init__(self):
        self.draw_area = DrawArea(WIDTH, HEIGHT - UI_TOP_BAR_HEIGHT)

    def add_shape(self, shape):
        self.draw_area.add_shape(shape)

    def remove_shape(self, shape):
        self.draw_area.remove_shape(shape)

    def run(self):
        with self.glfw_window() as window:
            glfw.set_mouse_button_callback(
                window, self.draw_area.mouse_button_callback)

            glfw.set_cursor_pos_callback(
                window, self.draw_area.cursor_pos_callback)

            while not glfw.window_should_close(window):
                GL.glClear(GL.GL_COLOR_BUFFER_BIT)

                with self.draw_area.skia_surface(window) as surface:
                    with surface as canvas:
                        self.draw_area.draw(canvas)

                    surface.flushAndSubmit()
                    glfw.swap_buffers(window)

                glfw.poll_events()

    @staticmethod
    @contextlib.contextmanager
    def glfw_window():
        if not glfw.init():
            raise RuntimeError('glfw.init() failed')
        glfw.window_hint(glfw.STENCIL_BITS, 8)
        window = glfw.create_window(WIDTH, HEIGHT, '', None, None)
        glfw.make_context_current(window)
        yield window
        glfw.terminate()


wmain = Wmain()
color = Color(0, 255, 0)
shape = Shape(vec2(55, 55), 40, color)
wmain.add_shape(shape)
wmain.run()
