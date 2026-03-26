from __future__ import annotations

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3


class OrbitCameraController:
    def __init__(self, app: ShowBase, *, arena_size: float) -> None:
        self._app = app
        self._arena_size = float(arena_size)
        self._focus_margin = self._arena_size * 0.25
        self._default_distance = max(90.0, self._arena_size * 1.20)
        self._distance = self._default_distance
        self._pan_speed = max(20.0, self._arena_size * 0.30)
        self._orbit_speed = 70.0
        self._pitch_speed = 45.0
        self._zoom_step = max(8.0, self._arena_size * 0.04)
        self._mouse_pan_scale = max(35.0, self._arena_size * 0.70)
        self._mouse_orbit_scale = 140.0
        self._mouse_pitch_scale = 100.0
        self._drag_action: str | None = None
        self._last_mouse_pos: tuple[float, float] | None = None
        self._keys = {
            "w": False,
            "s": False,
            "a": False,
            "d": False,
            "q": False,
            "e": False,
            "r": False,
            "f": False,
        }

        self._focus_np = app.render.attachNewNode("camera_focus")
        self._yaw_np = self._focus_np.attachNewNode("camera_yaw")
        self._pitch_np = self._yaw_np.attachNewNode("camera_pitch")
        app.camera.reparentTo(self._pitch_np)

        for key_name in self._keys:
            app.accept(key_name, self._set_key_state, [key_name, True])
            app.accept(f"{key_name}-up", self._set_key_state, [key_name, False])
        app.accept("mouse1", self._set_drag_state, ["pan", True])
        app.accept("mouse1-up", self._set_drag_state, ["pan", False])
        app.accept("mouse3", self._set_drag_state, ["orbit", True])
        app.accept("mouse3-up", self._set_drag_state, ["orbit", False])
        app.accept("wheel_up", self.zoom, [-self._zoom_step])
        app.accept("wheel_down", self.zoom, [self._zoom_step])
        app.accept("c", self.reset)

        self.reset()

    def _set_key_state(self, key_name: str, pressed: bool) -> None:
        self._keys[key_name] = bool(pressed)

    def _mouse_pos(self) -> tuple[float, float] | None:
        watcher = getattr(self._app, "mouseWatcherNode", None)
        if watcher is None or not watcher.hasMouse():
            return None
        point = watcher.getMouse()
        return (float(point.getX()), float(point.getY()))

    def _set_drag_state(self, action: str, pressed: bool) -> None:
        if pressed:
            self._drag_action = str(action)
            self._last_mouse_pos = self._mouse_pos()
            return
        if self._drag_action == action:
            self._drag_action = None
            self._last_mouse_pos = None

    def _normalize_xy(self, x_value: float, y_value: float) -> tuple[float, float]:
        length = ((float(x_value) * float(x_value)) + (float(y_value) * float(y_value))) ** 0.5
        if length <= 1e-9:
            return (0.0, 0.0)
        return (float(x_value) / length, float(y_value) / length)

    def _ground_plane_basis(self) -> tuple[tuple[float, float], tuple[float, float]]:
        camera_quat = self._app.camera.getQuat(self._app.render)
        right_vec = camera_quat.xform(Vec3(1.0, 0.0, 0.0))
        forward_vec = camera_quat.xform(Vec3(0.0, 1.0, 0.0))
        right_xy = self._normalize_xy(right_vec.getX(), right_vec.getY())
        forward_xy = self._normalize_xy(forward_vec.getX(), forward_vec.getY())
        if right_xy == (0.0, 0.0):
            right_xy = (1.0, 0.0)
        if forward_xy == (0.0, 0.0):
            forward_xy = (0.0, 1.0)
        return right_xy, forward_xy

    def _translate_focus(self, dx: float, dy: float) -> None:
        self._focus_np.setX(self._clamp_focus(self._focus_np.getX() + float(dx)))
        self._focus_np.setY(self._clamp_focus(self._focus_np.getY() + float(dy)))

    def _pan_distance_scale(self) -> float:
        if self._default_distance <= 1e-9:
            return 1.0
        return max(0.1, float(self._distance) / float(self._default_distance))

    def _update_mouse_drag(self) -> None:
        if self._drag_action is None:
            self._last_mouse_pos = None
            return
        current_mouse_pos = self._mouse_pos()
        if current_mouse_pos is None:
            self._last_mouse_pos = None
            return
        if self._last_mouse_pos is None:
            self._last_mouse_pos = current_mouse_pos
            return

        delta_x = float(current_mouse_pos[0]) - float(self._last_mouse_pos[0])
        delta_y = float(current_mouse_pos[1]) - float(self._last_mouse_pos[1])
        self._last_mouse_pos = current_mouse_pos
        if abs(delta_x) <= 1e-9 and abs(delta_y) <= 1e-9:
            return

        right_xy, forward_xy = self._ground_plane_basis()
        pan_scale = self._pan_distance_scale()

        if self._drag_action == "pan":
            self._translate_focus(
                ((-delta_x * self._mouse_pan_scale * pan_scale) * right_xy[0])
                + ((-delta_y * self._mouse_pan_scale * pan_scale) * forward_xy[0]),
                ((-delta_x * self._mouse_pan_scale * pan_scale) * right_xy[1])
                + ((-delta_y * self._mouse_pan_scale * pan_scale) * forward_xy[1]),
            )
            return

        if self._drag_action == "orbit":
            self._yaw_np.setH(self._yaw_np.getH() - (delta_x * self._mouse_orbit_scale))
            next_pitch = self._pitch_np.getP() + (delta_y * self._mouse_pitch_scale)
            self._pitch_np.setP(max(-85.0, min(-15.0, next_pitch)))

    def _clamp_focus(self, value: float) -> float:
        lower = -self._focus_margin
        upper = self._arena_size + self._focus_margin
        return max(lower, min(upper, value))

    def _apply_camera_distance(self) -> None:
        self._app.camera.setPos(0.0, -self._distance, 0.0)

    def reset(self) -> None:
        self._distance = self._default_distance
        self._focus_np.setPos(self._arena_size * 0.5, self._arena_size * 0.5, 0.0)
        self._yaw_np.setH(-45.0)
        self._pitch_np.setP(-55.0)
        self._apply_camera_distance()

    def zoom(self, delta: float) -> None:
        next_distance = self._distance + float(delta)
        min_distance = max(25.0, self._arena_size * 0.18)
        max_distance = max(self._default_distance * 1.6, self._arena_size * 2.0)
        self._distance = max(min_distance, min(max_distance, next_distance))
        self._apply_camera_distance()

    def update(self, dt: float) -> None:
        self._update_mouse_drag()
        right_xy, forward_xy = self._ground_plane_basis()
        pan_distance = self._pan_speed * dt * self._pan_distance_scale()
        if self._keys["a"]:
            self._translate_focus(-(pan_distance * right_xy[0]), -(pan_distance * right_xy[1]))
        if self._keys["d"]:
            self._translate_focus(pan_distance * right_xy[0], pan_distance * right_xy[1])
        if self._keys["s"]:
            self._translate_focus(-(pan_distance * forward_xy[0]), -(pan_distance * forward_xy[1]))
        if self._keys["w"]:
            self._translate_focus(pan_distance * forward_xy[0], pan_distance * forward_xy[1])
        if self._keys["q"]:
            self._yaw_np.setH(self._yaw_np.getH() + (self._orbit_speed * dt))
        if self._keys["e"]:
            self._yaw_np.setH(self._yaw_np.getH() - (self._orbit_speed * dt))
        if self._keys["r"]:
            self._pitch_np.setP(min(-15.0, self._pitch_np.getP() + (self._pitch_speed * dt)))
        if self._keys["f"]:
            self._pitch_np.setP(max(-85.0, self._pitch_np.getP() - (self._pitch_speed * dt)))
