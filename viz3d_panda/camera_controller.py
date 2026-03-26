from __future__ import annotations

from direct.showbase.ShowBase import ShowBase


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
        app.accept("wheel_up", self.zoom, [-self._zoom_step])
        app.accept("wheel_down", self.zoom, [self._zoom_step])
        app.accept("c", self.reset)

        self.reset()

    def _set_key_state(self, key_name: str, pressed: bool) -> None:
        self._keys[key_name] = bool(pressed)

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
        if self._keys["a"]:
            self._focus_np.setX(self._clamp_focus(self._focus_np.getX() - (self._pan_speed * dt)))
        if self._keys["d"]:
            self._focus_np.setX(self._clamp_focus(self._focus_np.getX() + (self._pan_speed * dt)))
        if self._keys["s"]:
            self._focus_np.setY(self._clamp_focus(self._focus_np.getY() - (self._pan_speed * dt)))
        if self._keys["w"]:
            self._focus_np.setY(self._clamp_focus(self._focus_np.getY() + (self._pan_speed * dt)))
        if self._keys["q"]:
            self._yaw_np.setH(self._yaw_np.getH() + (self._orbit_speed * dt))
        if self._keys["e"]:
            self._yaw_np.setH(self._yaw_np.getH() - (self._orbit_speed * dt))
        if self._keys["r"]:
            self._pitch_np.setP(min(-15.0, self._pitch_np.getP() + (self._pitch_speed * dt)))
        if self._keys["f"]:
            self._pitch_np.setP(max(-85.0, self._pitch_np.getP() - (self._pitch_speed * dt)))
