from __future__ import annotations

import math

from direct.showbase.ShowBase import ShowBase
from panda3d.core import Vec3

from viz3d_panda.replay_source import ViewerFrame


RESET_VIEW_KEY_EVENTS = ("`", "~")
DEFAULT_TOPDOWN_YAW_DEGREES = 0.0
DEFAULT_TOPDOWN_PITCH_DEGREES = -89.0
FLEET_VIEW_PITCH_DEGREES = -42.0
FLEET_VIEW_DISTANCE_PADDING = 56.0
FLEET_VIEW_DISTANCE_RADIUS_SCALE = 4.5
MIN_CAMERA_PITCH_DEGREES = -90.0
MAX_CAMERA_PITCH_DEGREES = 90.0


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
        self._tracked_fleet_id: str | None = None
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
        for event_name in RESET_VIEW_KEY_EVENTS:
            app.accept(event_name, self._toggle_tracking_or_reset)

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

    @staticmethod
    def _normalize_xy(x_value: float, y_value: float) -> tuple[float, float]:
        length = math.sqrt((float(x_value) * float(x_value)) + (float(y_value) * float(y_value)))
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
            self._pitch_np.setP(max(MIN_CAMERA_PITCH_DEGREES, min(MAX_CAMERA_PITCH_DEGREES, next_pitch)))

    def _clamp_focus(self, value: float) -> float:
        lower = -self._focus_margin
        upper = self._arena_size + self._focus_margin
        return max(lower, min(upper, value))

    def _apply_camera_distance(self) -> None:
        self._app.camera.setPos(0.0, -self._distance, 0.0)

    def _toggle_tracking_or_reset(self) -> None:
        if self._tracked_fleet_id is not None:
            self._tracked_fleet_id = None
            return
        self.reset()

    @staticmethod
    def _heading_to_camera_yaw(heading_x: float, heading_y: float) -> float:
        normalized_heading = OrbitCameraController._normalize_xy(heading_x, heading_y)
        if normalized_heading == (0.0, 0.0):
            return DEFAULT_TOPDOWN_YAW_DEGREES
        # Match the same Panda3D heading sign convention used by unit rendering so the
        # camera sits behind the fleet and looks along its forward direction, rather
        # than presenting that forward axis as a side-on view.
        return -math.degrees(math.atan2(float(normalized_heading[0]), float(normalized_heading[1])))

    @staticmethod
    def _summarize_fleet_frame(frame: ViewerFrame, fleet_id: str) -> dict[str, float] | None:
        fleet_units = [unit for unit in frame.units if unit.fleet_id == str(fleet_id)]
        if not fleet_units:
            return None

        centroid_x = sum(float(unit.x) for unit in fleet_units) / float(len(fleet_units))
        centroid_y = sum(float(unit.y) for unit in fleet_units) / float(len(fleet_units))
        radius = 0.0
        heading_sum_x = 0.0
        heading_sum_y = 0.0
        for unit in fleet_units:
            dx = float(unit.x) - centroid_x
            dy = float(unit.y) - centroid_y
            radius = max(radius, math.sqrt((dx * dx) + (dy * dy)))
            heading_sum_x += float(unit.heading_x)
            heading_sum_y += float(unit.heading_y)
        heading_x, heading_y = OrbitCameraController._normalize_xy(heading_sum_x, heading_sum_y)
        if heading_x == 0.0 and heading_y == 0.0:
            heading_x, heading_y = (0.0, 1.0)
        return {
            "centroid_x": centroid_x,
            "centroid_y": centroid_y,
            "heading_x": heading_x,
            "heading_y": heading_y,
            "radius": radius,
        }

    def _set_view(
        self,
        *,
        focus_x: float,
        focus_y: float,
        yaw_degrees: float,
        pitch_degrees: float,
        distance: float,
    ) -> None:
        self._distance = float(distance)
        self._focus_np.setPos(self._clamp_focus(float(focus_x)), self._clamp_focus(float(focus_y)), 0.0)
        self._yaw_np.setH(float(yaw_degrees))
        self._pitch_np.setP(float(pitch_degrees))
        self._apply_camera_distance()

    def _set_focus_only(self, *, focus_x: float, focus_y: float) -> None:
        self._focus_np.setPos(self._clamp_focus(float(focus_x)), self._clamp_focus(float(focus_y)), 0.0)

    def reset(self) -> None:
        self._tracked_fleet_id = None
        self._set_view(
            focus_x=self._arena_size * 0.5,
            focus_y=self._arena_size * 0.5,
            yaw_degrees=DEFAULT_TOPDOWN_YAW_DEGREES,
            pitch_degrees=DEFAULT_TOPDOWN_PITCH_DEGREES,
            distance=self._default_distance,
        )

    def _apply_fleet_view(self, frame: ViewerFrame, fleet_id: str) -> dict[str, float] | None:
        summary = self._summarize_fleet_frame(frame, fleet_id)
        if summary is None:
            return None
        min_distance = max(12.5, self._arena_size * 0.09)
        max_distance = max(self._default_distance * 3.2, self._arena_size * 4.0)
        requested_distance = (float(summary["radius"]) * FLEET_VIEW_DISTANCE_RADIUS_SCALE) + FLEET_VIEW_DISTANCE_PADDING
        requested_distance = max(min_distance, min(max_distance, requested_distance))
        self._set_view(
            focus_x=float(summary["centroid_x"]),
            focus_y=float(summary["centroid_y"]),
            yaw_degrees=self._heading_to_camera_yaw(float(summary["heading_x"]), float(summary["heading_y"])),
            pitch_degrees=FLEET_VIEW_PITCH_DEGREES,
            distance=requested_distance,
        )
        return summary

    def start_fleet_tracking(self, frame: ViewerFrame, fleet_id: str) -> bool:
        normalized_fleet_id = str(fleet_id)
        if self._apply_fleet_view(frame, normalized_fleet_id) is None:
            return False
        self._tracked_fleet_id = normalized_fleet_id
        return True

    def sync_tracked_frame(self, frame: ViewerFrame) -> bool:
        tracked_fleet_id = self._tracked_fleet_id
        if tracked_fleet_id is None:
            return False
        summary = self._summarize_fleet_frame(frame, tracked_fleet_id)
        if summary is None:
            return False
        self._set_focus_only(
            focus_x=float(summary["centroid_x"]),
            focus_y=float(summary["centroid_y"]),
        )
        return True

    def zoom(self, delta: float) -> None:
        next_distance = self._distance + float(delta)
        min_distance = max(12.5, self._arena_size * 0.09)
        max_distance = max(self._default_distance * 3.2, self._arena_size * 4.0)
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
            self._pitch_np.setP(min(MAX_CAMERA_PITCH_DEGREES, self._pitch_np.getP() + (self._pitch_speed * dt)))
        if self._keys["f"]:
            self._pitch_np.setP(max(MIN_CAMERA_PITCH_DEGREES, self._pitch_np.getP() - (self._pitch_speed * dt)))
