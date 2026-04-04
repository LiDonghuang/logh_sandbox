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
MAX_CAMERA_PITCH_DEGREES = 45.0
PAN_TRACK_CANCEL_DRAG_THRESHOLD = 0.035
TRACKED_CAMERA_DEADBAND_FLOOR = 0.12
TRACKED_CAMERA_DEADBAND_RATIO = 0.00045
TRACKED_CAMERA_SNAP_FLOOR = 4.0
TRACKED_CAMERA_SNAP_RATIO = 0.010
TRACKED_CAMERA_BLEND_GEAR1 = 0.16
TRACKED_CAMERA_BLEND_GEAR5 = 0.34


class OrbitCameraController:
    def __init__(self, app: ShowBase, *, arena_size: float) -> None:
        self._app = app
        self._arena_size = float(arena_size)
        self._focus_margin = self._arena_size * 0.25
        self._default_distance = max(90.0, self._arena_size * 1.20)
        self._distance = self._default_distance
        self._zoom_step = max(8.0, self._arena_size * 0.04)
        self._mouse_pan_scale = max(35.0, self._arena_size * 0.70)
        self._mouse_orbit_scale = 140.0
        self._mouse_pitch_scale = 100.0
        self._drag_action: str | None = None
        self._last_mouse_pos: tuple[float, float] | None = None
        self._pan_drag_distance_accumulator = 0.0
        self._tracked_fleet_id: str | None = None
        self._tracked_focus_display_xy: tuple[float, float] | None = None
        self._playback_level_index = 0

        self._focus_np = app.render.attachNewNode("camera_focus")
        self._yaw_np = self._focus_np.attachNewNode("camera_yaw")
        self._pitch_np = self._yaw_np.attachNewNode("camera_pitch")
        app.camera.reparentTo(self._pitch_np)

        app.accept("mouse1", self._set_drag_state, ["pan", True])
        app.accept("mouse1-up", self._set_drag_state, ["pan", False])
        app.accept("mouse3", self._set_drag_state, ["orbit", True])
        app.accept("mouse3-up", self._set_drag_state, ["orbit", False])
        app.accept("wheel_up", self.zoom, [-self._zoom_step])
        app.accept("wheel_down", self.zoom, [self._zoom_step])
        for event_name in RESET_VIEW_KEY_EVENTS:
            app.accept(event_name, self.reset)

        self.reset()

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
            if str(action) == "pan":
                self._pan_drag_distance_accumulator = 0.0
            return
        if self._drag_action == action:
            self._drag_action = None
            self._last_mouse_pos = None
            if str(action) == "pan":
                self._pan_drag_distance_accumulator = 0.0

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
            self._pan_drag_distance_accumulator += math.sqrt((delta_x * delta_x) + (delta_y * delta_y))
            if (
                self._tracked_fleet_id is not None
                and self._pan_drag_distance_accumulator >= PAN_TRACK_CANCEL_DRAG_THRESHOLD
            ):
                self._tracked_fleet_id = None
                self._tracked_focus_display_xy = None
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

    def _tracked_focus_profile(self) -> tuple[float, float, float]:
        gear_max_index = 4.0
        gear_alpha = max(0.0, min(1.0, float(self._playback_level_index) / gear_max_index))
        deadband = max(TRACKED_CAMERA_DEADBAND_FLOOR, self._arena_size * TRACKED_CAMERA_DEADBAND_RATIO)
        deadband *= 1.35 - (0.45 * gear_alpha)
        snap_distance = max(TRACKED_CAMERA_SNAP_FLOOR, self._arena_size * TRACKED_CAMERA_SNAP_RATIO)
        snap_distance *= 0.90 + (0.20 * gear_alpha)
        blend = TRACKED_CAMERA_BLEND_GEAR1 + ((TRACKED_CAMERA_BLEND_GEAR5 - TRACKED_CAMERA_BLEND_GEAR1) * gear_alpha)
        return (float(deadband), float(snap_distance), float(blend))

    def _apply_smoothed_tracked_focus(self, *, target_x: float, target_y: float) -> None:
        previous_focus = self._tracked_focus_display_xy
        if previous_focus is None:
            clamped_x = self._clamp_focus(float(target_x))
            clamped_y = self._clamp_focus(float(target_y))
            self._tracked_focus_display_xy = (clamped_x, clamped_y)
            self._set_focus_only(focus_x=clamped_x, focus_y=clamped_y)
            return
        deadband, snap_distance, blend = self._tracked_focus_profile()
        delta_x = float(target_x) - float(previous_focus[0])
        delta_y = float(target_y) - float(previous_focus[1])
        distance = math.sqrt((delta_x * delta_x) + (delta_y * delta_y))
        if distance <= deadband:
            display_x = float(previous_focus[0])
            display_y = float(previous_focus[1])
        elif distance >= snap_distance:
            display_x = float(target_x)
            display_y = float(target_y)
        else:
            display_x = float(previous_focus[0]) + (blend * delta_x)
            display_y = float(previous_focus[1]) + (blend * delta_y)
        clamped_x = self._clamp_focus(display_x)
        clamped_y = self._clamp_focus(display_y)
        self._tracked_focus_display_xy = (clamped_x, clamped_y)
        self._set_focus_only(focus_x=clamped_x, focus_y=clamped_y)

    def reset(self) -> None:
        self._tracked_fleet_id = None
        self._tracked_focus_display_xy = None
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
        min_distance = max(9.0, self._arena_size * 0.065)
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
        preserve_view = self._drag_action == "orbit"
        summary: dict[str, float] | None = None
        if preserve_view:
            summary = self._summarize_fleet_frame(frame, normalized_fleet_id)
            if summary is None:
                return False
            self._set_focus_only(
                focus_x=float(summary["centroid_x"]),
                focus_y=float(summary["centroid_y"]),
            )
        else:
            summary = self._apply_fleet_view(frame, normalized_fleet_id)
            if summary is None:
                return False
        self._tracked_fleet_id = normalized_fleet_id
        if summary is not None:
            self._tracked_focus_display_xy = (
                self._clamp_focus(float(summary["centroid_x"])),
                self._clamp_focus(float(summary["centroid_y"])),
            )
        return True

    def sync_tracked_frame(self, frame: ViewerFrame, *, smooth: bool = True) -> bool:
        tracked_fleet_id = self._tracked_fleet_id
        if tracked_fleet_id is None:
            return False
        summary = self._summarize_fleet_frame(frame, tracked_fleet_id)
        if summary is None:
            self._tracked_focus_display_xy = None
            return False
        if smooth:
            self._apply_smoothed_tracked_focus(
                target_x=float(summary["centroid_x"]),
                target_y=float(summary["centroid_y"]),
            )
        else:
            self._tracked_focus_display_xy = (
                self._clamp_focus(float(summary["centroid_x"])),
                self._clamp_focus(float(summary["centroid_y"])),
            )
            self._set_focus_only(
                focus_x=float(summary["centroid_x"]),
                focus_y=float(summary["centroid_y"]),
            )
        return True

    def sync_tracked_frames(
        self,
        current_frame: ViewerFrame,
        next_frame: ViewerFrame,
        *,
        alpha: float,
        smooth: bool = True,
    ) -> bool:
        tracked_fleet_id = self._tracked_fleet_id
        if tracked_fleet_id is None:
            return False
        current_summary = self._summarize_fleet_frame(current_frame, tracked_fleet_id)
        if current_summary is None:
            return False
        next_summary = self._summarize_fleet_frame(next_frame, tracked_fleet_id)
        if next_summary is None:
            if smooth:
                self._apply_smoothed_tracked_focus(
                    target_x=float(current_summary["centroid_x"]),
                    target_y=float(current_summary["centroid_y"]),
                )
            else:
                self._tracked_focus_display_xy = (
                    self._clamp_focus(float(current_summary["centroid_x"])),
                    self._clamp_focus(float(current_summary["centroid_y"])),
                )
                self._set_focus_only(
                    focus_x=float(current_summary["centroid_x"]),
                    focus_y=float(current_summary["centroid_y"]),
                )
            return True
        blend = max(0.0, min(1.0, float(alpha)))
        focus_x = ((1.0 - blend) * float(current_summary["centroid_x"])) + (blend * float(next_summary["centroid_x"]))
        focus_y = ((1.0 - blend) * float(current_summary["centroid_y"])) + (blend * float(next_summary["centroid_y"]))
        if smooth:
            self._apply_smoothed_tracked_focus(
                target_x=focus_x,
                target_y=focus_y,
            )
        else:
            self._tracked_focus_display_xy = (
                self._clamp_focus(float(focus_x)),
                self._clamp_focus(float(focus_y)),
            )
            self._set_focus_only(
                focus_x=focus_x,
                focus_y=focus_y,
            )
        return True

    def set_playback_level_index(self, playback_level_index: int) -> None:
        self._playback_level_index = max(0, int(playback_level_index))

    def snapshot_state(self) -> dict[str, float | str | None]:
        return {
            "focus_x": float(self._focus_np.getX()),
            "focus_y": float(self._focus_np.getY()),
            "yaw_deg": float(self._yaw_np.getH()),
            "pitch_deg": float(self._pitch_np.getP()),
            "distance": float(self._distance),
            "tracked_fleet_id": self._tracked_fleet_id,
        }

    def apply_state_snapshot(self, state: dict[str, float | str | None]) -> None:
        tracked_fleet_id = state.get("tracked_fleet_id")
        self._tracked_fleet_id = None if tracked_fleet_id is None else str(tracked_fleet_id)
        self._tracked_focus_display_xy = None
        self._set_view(
            focus_x=float(state["focus_x"]),
            focus_y=float(state["focus_y"]),
            yaw_degrees=float(state["yaw_deg"]),
            pitch_degrees=float(state["pitch_deg"]),
            distance=float(state["distance"]),
        )
        if self._tracked_fleet_id is not None:
            self._tracked_focus_display_xy = (
                self._clamp_focus(float(state["focus_x"])),
                self._clamp_focus(float(state["focus_y"])),
            )

    def zoom(self, delta: float) -> None:
        distance_scale = 1.0
        if self._default_distance > 1e-9:
            distance_scale = max(1.0, min(1.8, float(self._distance) / float(self._default_distance)))
        next_distance = self._distance + (float(delta) * distance_scale)
        min_distance = max(9.0, self._arena_size * 0.065)
        max_distance = max(self._default_distance * 3.2, self._arena_size * 4.0)
        self._distance = max(min_distance, min(max_distance, next_distance))
        self._apply_camera_distance()

    def update(self, dt: float) -> None:
        self._update_mouse_drag()
