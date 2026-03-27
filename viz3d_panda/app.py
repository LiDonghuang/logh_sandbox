from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Sequence

try:
    from direct.gui.DirectFrame import DirectFrame
    from direct.gui.OnscreenImage import OnscreenImage
    from direct.gui.OnscreenText import OnscreenText
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import ClockObject, Filename, Point2, Point3, TextNode, TransparencyAttrib, loadPrcFileData
except ImportError as exc:  # pragma: no cover - import guard for incorrect env usage
    raise SystemExit(
        "Panda3D is not available in the current interpreter. "
        "Use .venv_dev_v2_0\\Scripts\\python.exe -m viz3d_panda.app ..."
    ) from exc

from viz3d_panda.camera_controller import OrbitCameraController
from viz3d_panda.replay_source import (
    DEFAULT_FRAME_STRIDE,
    VIEWER_DIRECTION_MODE_CHOICES,
    VIEWER_DIRECTION_MODE_SETTINGS,
    VIEWER_SOURCE_AUTO,
    VIEWER_SOURCE_CHOICES,
    ReplayBundle,
    ViewerFrame,
    ViewerUnitState,
    load_viewer_replay,
)
from viz3d_panda.scene_builder import build_scene
from viz3d_panda.unit_renderer import FIRE_LINK_MODES, UnitRenderer


WINDOW_TITLE = "LOGH dev_v2.0 Panda3D Viewer Scaffold"
AVATAR_DIR = Path(__file__).resolve().parents[1] / "visual" / "avatars"
PLAYBACK_FPS_LEVELS = (4.0, 8.0, 12.0, 18.0, 24.0)
DEFAULT_PLAYBACK_LEVEL_INDEX = 2
FIRE_LINK_MODE_CHOICES = tuple(sorted(FIRE_LINK_MODES))
STEP_HOLD_INITIAL_DELAY_SECONDS = 0.35
STEP_HOLD_REPEAT_INTERVAL_SECONDS = 0.08
LOW_SPEED_SMOOTHING_MAX_FPS = 12.0
FLEET_AVATAR_HEIGHT = 0.105
FLEET_AVATAR_ASPECT_RATIO = 4.0 / 5.0
FLEET_AVATAR_SCREEN_NUDGE = 0.012
FLEET_AVATAR_MIN_SCREEN_OFFSET = 0.078
FLEET_AVATAR_MAX_SCREEN_OFFSET = 0.128
FLEET_AVATAR_BORDER_PAD = 0.009
FLEET_AVATAR_MATTE_PAD = 0.004
FLEET_AVATAR_HIGHLIGHT_PAD = 0.018
FLEET_AVATAR_HIGHLIGHT_ALPHA = 0.48
FLEET_AVATAR_MATTE_COLOR = (0.02, 0.03, 0.05, 0.82)
FLEET_AVATAR_BORDER_ALPHA = 1.0
FLEET_AVATAR_POSITION_DEADBAND = 0.010
FLEET_AVATAR_SMOOTHING_BLEND = 0.28
FLEET_AVATAR_SNAP_DISTANCE = 0.18
FLEET_AVATAR_PAIR_ENTER_DISTANCE_X = 0.34
FLEET_AVATAR_PAIR_ENTER_DISTANCE_Z = 0.24
FLEET_AVATAR_PAIR_EXIT_DISTANCE_X = 0.42
FLEET_AVATAR_PAIR_EXIT_DISTANCE_Z = 0.30
FLEET_AVATAR_PAIR_SEPARATION_X = 0.20


def _resolve_avatar_image_path(avatar_id: object) -> Path | None:
    stem = str(avatar_id).strip() if avatar_id is not None else ""
    if not stem:
        return None
    suffixes = (".png", ".jpg", ".jpeg", ".webp", ".bmp")
    candidate_names: list[str] = []
    if "." in stem:
        candidate_names.append(stem)
    else:
        if stem.startswith("avatar_"):
            candidate_names.extend([f"avatar_s_{stem[len('avatar_') :]}{suffix}" for suffix in suffixes])
        candidate_names.extend([f"{stem}{suffix}" for suffix in suffixes])
    for name in candidate_names:
        path = AVATAR_DIR / name
        if path.exists():
            return path
    return None


def _count_units_by_fleet(replay: ReplayBundle, frame_index: int) -> str:
    frame = replay.frames[frame_index]
    counts: dict[str, int] = {}
    for unit in frame.units:
        counts[unit.fleet_id] = counts.get(unit.fleet_id, 0) + 1
    parts = []
    for fleet_id, count in sorted(counts.items()):
        label = replay.fleet_labels.get(fleet_id, fleet_id)
        parts.append(f"{label}:{count}")
    return "  ".join(parts)


def _resolve_playback_level_index(playback_fps: float) -> int:
    requested = float(playback_fps)
    for index, level in enumerate(PLAYBACK_FPS_LEVELS):
        if abs(requested - float(level)) <= 1e-9:
            return index
    supported_values = ", ".join(f"{level:.0f}" if float(level).is_integer() else f"{level}" for level in PLAYBACK_FPS_LEVELS)
    raise ValueError(
        f"playback-fps must be one of the fixed viewer speed levels: {supported_values}; got {playback_fps}."
    )


def _normalize_heading(dx: float, dy: float) -> tuple[float, float]:
    norm = math.sqrt((float(dx) * float(dx)) + (float(dy) * float(dy)))
    if norm <= 1e-12:
        return (0.0, 0.0)
    return (float(dx) / norm, float(dy) / norm)


def _interpolate_heading(
    current_heading: tuple[float, float],
    next_heading: tuple[float, float],
    alpha: float,
) -> tuple[float, float]:
    if current_heading == (0.0, 0.0):
        return next_heading
    if next_heading == (0.0, 0.0):
        return current_heading
    dot = (float(current_heading[0]) * float(next_heading[0])) + (float(current_heading[1]) * float(next_heading[1]))
    if dot <= -0.98:
        return next_heading if float(alpha) >= 0.5 else current_heading
    blended = (
        ((1.0 - float(alpha)) * float(current_heading[0])) + (float(alpha) * float(next_heading[0])),
        ((1.0 - float(alpha)) * float(current_heading[1])) + (float(alpha) * float(next_heading[1])),
    )
    normalized = _normalize_heading(blended[0], blended[1])
    return normalized if normalized != (0.0, 0.0) else next_heading


def _hex_to_rgba(value: str, *, alpha: float) -> tuple[float, float, float, float]:
    text = str(value).strip()
    if text.startswith("#"):
        text = text[1:]
    if len(text) != 6:
        return (1.0, 1.0, 1.0, float(alpha))
    try:
        red = int(text[0:2], 16) / 255.0
        green = int(text[2:4], 16) / 255.0
        blue = int(text[4:6], 16) / 255.0
    except ValueError:
        return (1.0, 1.0, 1.0, float(alpha))
    return (red, green, blue, float(alpha))


class FleetViewerApp(ShowBase):
    def __init__(self, replay: ReplayBundle, *, playback_fps: float, fire_link_mode: str) -> None:
        if not replay.frames:
            raise ValueError("ReplayBundle.frames is empty; nothing to render.")
        super().__init__()
        self.disableMouse()
        self.setBackgroundColor(0.03, 0.05, 0.09, 1.0)

        self._replay = replay
        self._playback_level_index = _resolve_playback_level_index(float(playback_fps))
        self._playback_fps = float(PLAYBACK_FPS_LEVELS[self._playback_level_index])
        self._current_frame_index = 0
        self._accumulator = 0.0
        self._playing = True
        self._smoothing_enabled = True
        self._avatars_enabled = True
        self._hud_enabled = True
        self._held_step_direction = 0
        self._held_step_delay_remaining = 0.0
        self._held_step_repeat_accumulator = 0.0

        self._scene_root = build_scene(self.render, arena_size=self._replay.arena_size)
        self._unit_renderer = UnitRenderer(self._scene_root, self._replay, fire_link_mode=fire_link_mode)
        self._camera_controller = OrbitCameraController(self, arena_size=self._replay.arena_size)
        self._fleet_avatar_nodes: dict[str, dict[str, object]] = {}
        self._fleet_avatar_display_positions: dict[str, tuple[float, float]] = {}
        self._fleet_avatar_pair_layout_active = False
        self._fleet_avatar_world_lift = max(8.0, float(self._replay.arena_size) * 0.03)

        self._status_text = OnscreenText(
            text="",
            parent=self.a2dBottomLeft,
            pos=(0.03, 0.21),
            scale=0.042,
            align=TextNode.ALeft,
            fg=(0.72, 0.80, 0.89, 1.0),
        )
        self._control_text = OnscreenText(
            text="",
            parent=self.a2dBottomRight,
            pos=(-0.03, 0.21),
            scale=0.042,
            align=TextNode.ARight,
            fg=(0.72, 0.80, 0.89, 1.0),
        )
        self._build_avatar_overlays()

        self.accept("space", self.toggle_playback)
        self.accept("n", self._begin_hold_step, [1])
        self.accept("n-up", self._end_hold_step, [1])
        self.accept("b", self._begin_hold_step, [-1])
        self.accept("b-up", self._end_hold_step, [-1])
        self.accept("v", self.cycle_fire_link_mode)
        self.accept("m", self.toggle_smoothing)
        self.accept("p", self.toggle_avatars)
        self.accept("tab", self.toggle_hud)
        self.accept("]", self._adjust_playback_speed, [1])
        self.accept("[", self._adjust_playback_speed, [-1])
        self.accept("1", self._focus_fleet_camera, ["A"])
        self.accept("2", self._focus_fleet_camera, ["B"])
        self.accept("home", self.go_to_frame, [0])
        self.accept("end", self.go_to_frame, [len(self._replay.frames) - 1])
        self.accept("escape", self.userExit)

        self.go_to_frame(0)
        self.taskMgr.add(self._tick, "fleet_viewer_tick")

    def _adjust_playback_speed(self, delta: int) -> None:
        next_index = max(0, min(len(PLAYBACK_FPS_LEVELS) - 1, self._playback_level_index + int(delta)))
        self._playback_level_index = next_index
        self._playback_fps = float(PLAYBACK_FPS_LEVELS[self._playback_level_index])
        self.go_to_frame(self._current_frame_index)

    def cycle_fire_link_mode(self) -> None:
        current_index = FIRE_LINK_MODE_CHOICES.index(self._unit_renderer.fire_link_mode)
        next_index = (current_index + 1) % len(FIRE_LINK_MODE_CHOICES)
        self._unit_renderer.set_fire_link_mode(FIRE_LINK_MODE_CHOICES[next_index])
        self.go_to_frame(self._current_frame_index)

    def toggle_playback(self) -> None:
        self._playing = not self._playing
        self.go_to_frame(self._current_frame_index)

    def toggle_smoothing(self) -> None:
        self._smoothing_enabled = not self._smoothing_enabled
        self.go_to_frame(self._current_frame_index)

    def toggle_avatars(self) -> None:
        self._avatars_enabled = not self._avatars_enabled
        self._sync_fleet_avatar_overlays()
        self._refresh_overlay()

    def toggle_hud(self) -> None:
        self._hud_enabled = not self._hud_enabled
        if self._hud_enabled:
            self._status_text.show()
            self._control_text.show()
            self._refresh_overlay()
        else:
            self._status_text.hide()
            self._control_text.hide()

    def _step_by(self, direction: int) -> None:
        self._playing = False
        next_index = self._current_frame_index + int(direction)
        self.go_to_frame(next_index)

    def _begin_hold_step(self, direction: int) -> None:
        normalized_direction = 1 if int(direction) > 0 else -1
        if self._held_step_direction == normalized_direction:
            return
        self._held_step_direction = normalized_direction
        self._held_step_delay_remaining = STEP_HOLD_INITIAL_DELAY_SECONDS
        self._held_step_repeat_accumulator = 0.0
        self._step_by(normalized_direction)

    def _end_hold_step(self, direction: int) -> None:
        normalized_direction = 1 if int(direction) > 0 else -1
        if self._held_step_direction != normalized_direction:
            return
        self._held_step_direction = 0
        self._held_step_delay_remaining = 0.0
        self._held_step_repeat_accumulator = 0.0

    def step_forward(self) -> None:
        self._step_by(1)

    def step_backward(self) -> None:
        self._step_by(-1)

    def _focus_fleet_camera(self, fleet_id: str) -> None:
        frame = self._replay.frames[self._current_frame_index]
        self._camera_controller.start_fleet_tracking(frame, str(fleet_id))

    def _render_frame(self, frame: ViewerFrame) -> None:
        self._unit_renderer.sync_frame(frame)
        self._unit_renderer.update_view(self.camera)
        self._sync_fleet_avatar_overlays()

    def _build_avatar_overlays(self) -> None:
        raw_avatars = self._replay.metadata.get("fleet_avatars", {})
        if not isinstance(raw_avatars, dict):
            return
        # OnscreenImage scale values are already half-extents in aspect2d space
        # because the underlying card spans [-1, +1]. Build border geometry around
        # those true half-extents so all four sides stay outside the portrait.
        avatar_half_height = FLEET_AVATAR_HEIGHT
        avatar_half_width = FLEET_AVATAR_HEIGHT * FLEET_AVATAR_ASPECT_RATIO
        border_half_height = avatar_half_height + FLEET_AVATAR_BORDER_PAD
        border_half_width = avatar_half_width + FLEET_AVATAR_BORDER_PAD
        matte_half_height = avatar_half_height + FLEET_AVATAR_MATTE_PAD
        matte_half_width = avatar_half_width + FLEET_AVATAR_MATTE_PAD
        highlight_half_height = avatar_half_height + FLEET_AVATAR_HIGHLIGHT_PAD
        highlight_half_width = avatar_half_width + FLEET_AVATAR_HIGHLIGHT_PAD
        for stack_index, (fleet_id, avatar_id) in enumerate(sorted(raw_avatars.items(), key=lambda item: str(item[0]))):
            avatar_path = _resolve_avatar_image_path(avatar_id)
            if avatar_path is None:
                continue
            texture = self.loader.loadTexture(Filename.fromOsSpecific(str(avatar_path)))
            if texture is None:
                continue
            fleet_color = self._replay.fleet_colors.get(str(fleet_id), "#ffffff")
            base_bin = 40 + (int(stack_index) * 10)
            highlight = DirectFrame(
                parent=self.aspect2d,
                frameSize=(-highlight_half_width, highlight_half_width, -highlight_half_height, highlight_half_height),
                frameColor=_hex_to_rgba(fleet_color, alpha=FLEET_AVATAR_HIGHLIGHT_ALPHA),
            )
            highlight.setTransparency(TransparencyAttrib.MAlpha)
            highlight.setBin("fixed", base_bin)
            highlight.setDepthTest(False)
            highlight.setDepthWrite(False)
            highlight.hide()
            matte = DirectFrame(
                parent=self.aspect2d,
                frameSize=(-matte_half_width, matte_half_width, -matte_half_height, matte_half_height),
                frameColor=FLEET_AVATAR_MATTE_COLOR,
            )
            matte.setTransparency(TransparencyAttrib.MAlpha)
            matte.setBin("fixed", base_bin + 1)
            matte.setDepthTest(False)
            matte.setDepthWrite(False)
            matte.hide()
            border_color = _hex_to_rgba(fleet_color, alpha=FLEET_AVATAR_BORDER_ALPHA)
            border_bars = {
                "top": DirectFrame(
                    parent=self.aspect2d,
                    frameSize=(-border_half_width, border_half_width, matte_half_height, border_half_height),
                    frameColor=border_color,
                ),
                "bottom": DirectFrame(
                    parent=self.aspect2d,
                    frameSize=(-border_half_width, border_half_width, -border_half_height, -matte_half_height),
                    frameColor=border_color,
                ),
                "left": DirectFrame(
                    parent=self.aspect2d,
                    frameSize=(-border_half_width, -matte_half_width, -matte_half_height, matte_half_height),
                    frameColor=border_color,
                ),
                "right": DirectFrame(
                    parent=self.aspect2d,
                    frameSize=(matte_half_width, border_half_width, -matte_half_height, matte_half_height),
                    frameColor=border_color,
                ),
            }
            for border_bar in border_bars.values():
                border_bar.setTransparency(TransparencyAttrib.MAlpha)
                border_bar.setBin("fixed", base_bin + 3)
                border_bar.setDepthTest(False)
                border_bar.setDepthWrite(False)
                border_bar.hide()
            node = OnscreenImage(
                image=texture,
                parent=self.aspect2d,
                pos=(0.0, 0.0, 0.0),
                scale=(avatar_half_width, 1.0, avatar_half_height),
            )
            node.setTransparency(TransparencyAttrib.MAlpha)
            node.setBin("fixed", base_bin + 2)
            node.setDepthTest(False)
            node.setDepthWrite(False)
            node.hide()
            self._fleet_avatar_nodes[str(fleet_id)] = {
                "highlight": highlight,
                "matte": matte,
                "border_top": border_bars["top"],
                "border_bottom": border_bars["bottom"],
                "border_left": border_bars["left"],
                "border_right": border_bars["right"],
                "image": node,
            }

    def _project_avatar_anchor(self, *, centroid_x: float, centroid_y: float, fleet_radius: float) -> tuple[float, float] | None:
        world_lift = max(self._fleet_avatar_world_lift, float(fleet_radius) * 0.28)
        projected_centroid = self._project_world_to_aspect2d(Point3(float(centroid_x), float(centroid_y), 0.0))
        projected_lifted = self._project_world_to_aspect2d(Point3(float(centroid_x), float(centroid_y), world_lift))
        if projected_centroid is None:
            return None
        raw_offset = FLEET_AVATAR_SCREEN_NUDGE
        if projected_lifted is not None:
            raw_offset += float(projected_lifted[1]) - float(projected_centroid[1])
        clamped_offset = max(FLEET_AVATAR_MIN_SCREEN_OFFSET, min(FLEET_AVATAR_MAX_SCREEN_OFFSET, raw_offset))
        return (float(projected_centroid[0]), float(projected_centroid[1]) + clamped_offset)

    def _project_world_to_aspect2d(self, world_point: Point3) -> tuple[float, float] | None:
        camera_point = self.camera.getRelativePoint(self.render, world_point)
        projected = Point2()
        if not self.camLens.project(camera_point, projected):
            return None
        return (float(projected.x) * float(self.getAspectRatio()), float(projected.y))

    def _resolve_avatar_layout_positions(
        self,
        anchors: dict[str, tuple[float, float]],
    ) -> dict[str, tuple[float, float]]:
        if len(anchors) != 2:
            self._fleet_avatar_pair_layout_active = False
            return dict(anchors)
        fleet_ids = sorted(anchors.keys())
        left_id = fleet_ids[0]
        right_id = fleet_ids[1]
        left_anchor = anchors[left_id]
        right_anchor = anchors[right_id]
        delta_x = float(right_anchor[0]) - float(left_anchor[0])
        delta_z = float(right_anchor[1]) - float(left_anchor[1])
        if self._fleet_avatar_pair_layout_active:
            trigger_x = FLEET_AVATAR_PAIR_EXIT_DISTANCE_X
            trigger_z = FLEET_AVATAR_PAIR_EXIT_DISTANCE_Z
        else:
            trigger_x = FLEET_AVATAR_PAIR_ENTER_DISTANCE_X
            trigger_z = FLEET_AVATAR_PAIR_ENTER_DISTANCE_Z
        if abs(delta_x) >= trigger_x or abs(delta_z) >= trigger_z:
            self._fleet_avatar_pair_layout_active = False
            return {
                left_id: (float(left_anchor[0]), float(left_anchor[1])),
                right_id: (float(right_anchor[0]), float(right_anchor[1])),
            }
        self._fleet_avatar_pair_layout_active = True
        midpoint_x = (float(left_anchor[0]) + float(right_anchor[0])) * 0.5
        midpoint_z = (float(left_anchor[1]) + float(right_anchor[1])) * 0.5
        aspect_ratio = float(self.getAspectRatio())
        max_x = aspect_ratio - 0.08
        min_x = -max_x
        paired_left_x = max(min_x, min(max_x, midpoint_x - (FLEET_AVATAR_PAIR_SEPARATION_X * 0.5)))
        paired_right_x = max(min_x, min(max_x, midpoint_x + (FLEET_AVATAR_PAIR_SEPARATION_X * 0.5)))
        paired_z = max(-0.90, min(0.92, midpoint_z))
        return {
            left_id: (paired_left_x, paired_z),
            right_id: (paired_right_x, paired_z),
        }

    def _sync_fleet_avatar_overlays(self) -> None:
        if not self._avatars_enabled:
            for nodes in self._fleet_avatar_nodes.values():
                for node in nodes.values():
                    node.hide()
            return
        halo_state = self._unit_renderer.fleet_halo_state
        target_positions: dict[str, tuple[float, float]] = {}
        for fleet_id, nodes in self._fleet_avatar_nodes.items():
            state = halo_state.get(fleet_id)
            if not isinstance(state, dict):
                for node in nodes.values():
                    node.hide()
                continue
            projected_anchor = self._project_avatar_anchor(
                centroid_x=float(state["centroid_x"]),
                centroid_y=float(state["centroid_y"]),
                fleet_radius=float(state["radius"]),
            )
            if projected_anchor is None:
                self._fleet_avatar_display_positions.pop(fleet_id, None)
                for node in nodes.values():
                    node.hide()
                continue
            aspect_ratio = float(self.getAspectRatio())
            target_x = max(-(aspect_ratio - 0.08), min(aspect_ratio - 0.08, float(projected_anchor[0])))
            target_z = max(-0.90, min(0.92, float(projected_anchor[1])))
            target_positions[fleet_id] = (target_x, target_z)
        adjusted_target_positions = self._resolve_avatar_layout_positions(target_positions)
        display_positions: dict[str, tuple[float, float]] = {}
        for fleet_id, nodes in self._fleet_avatar_nodes.items():
            target_position = adjusted_target_positions.get(fleet_id)
            if target_position is None:
                self._fleet_avatar_display_positions.pop(fleet_id, None)
                for node in nodes.values():
                    node.hide()
                continue
            target_x, target_z = target_position
            previous_position = self._fleet_avatar_display_positions.get(fleet_id)
            if (not self._playing) or previous_position is None:
                display_x = float(target_x)
                display_z = float(target_z)
            else:
                delta_x = float(target_x) - float(previous_position[0])
                delta_z = float(target_z) - float(previous_position[1])
                distance = math.sqrt((delta_x * delta_x) + (delta_z * delta_z))
                if distance <= FLEET_AVATAR_POSITION_DEADBAND:
                    display_x = float(previous_position[0])
                    display_z = float(previous_position[1])
                elif distance >= FLEET_AVATAR_SNAP_DISTANCE:
                    display_x = float(target_x)
                    display_z = float(target_z)
                else:
                    blend = FLEET_AVATAR_SMOOTHING_BLEND
                    display_x = float(previous_position[0]) + (blend * delta_x)
                    display_z = float(previous_position[1]) + (blend * delta_z)
            display_positions[fleet_id] = (display_x, display_z)
        final_display_positions = self._resolve_avatar_layout_positions(display_positions)
        for fleet_id, nodes in self._fleet_avatar_nodes.items():
            final_position = final_display_positions.get(fleet_id)
            if final_position is None:
                self._fleet_avatar_display_positions.pop(fleet_id, None)
                for node in nodes.values():
                    node.hide()
                continue
            display_x, display_z = final_position
            self._fleet_avatar_display_positions[fleet_id] = (display_x, display_z)
            for node in nodes.values():
                node.setPos(display_x, 0.0, display_z)
                node.show()

    def _smoothing_active(self) -> bool:
        return bool(self._smoothing_enabled and self._playing and self._playback_fps <= LOW_SPEED_SMOOTHING_MAX_FPS and len(self._replay.frames) > 1)

    def _build_smoothed_frame(self, alpha: float) -> ViewerFrame:
        current_frame = self._replay.frames[self._current_frame_index]
        if len(self._replay.frames) <= 1:
            return current_frame
        next_index = self._current_frame_index + 1
        if next_index >= len(self._replay.frames):
            next_index = 0
        next_frame = self._replay.frames[next_index]
        interpolation_alpha = min(1.0, max(0.0, float(alpha)))
        if interpolation_alpha <= 1e-9:
            return current_frame
        next_units = {
            (str(unit.fleet_id), str(unit.unit_id)): unit
            for unit in next_frame.units
        }
        smoothed_units: list[ViewerUnitState] = []
        for unit in current_frame.units:
            next_unit = next_units.get((str(unit.fleet_id), str(unit.unit_id)))
            if next_unit is None:
                smoothed_units.append(unit)
                continue
            blended_heading = _interpolate_heading(
                (float(unit.heading_x), float(unit.heading_y)),
                (float(next_unit.heading_x), float(next_unit.heading_y)),
                interpolation_alpha,
            )
            smoothed_units.append(
                ViewerUnitState(
                    unit_id=str(unit.unit_id),
                    fleet_id=str(unit.fleet_id),
                    x=((1.0 - interpolation_alpha) * float(unit.x)) + (interpolation_alpha * float(next_unit.x)),
                    y=((1.0 - interpolation_alpha) * float(unit.y)) + (interpolation_alpha * float(next_unit.y)),
                    z=((1.0 - interpolation_alpha) * float(unit.z)) + (interpolation_alpha * float(next_unit.z)),
                    heading_x=float(blended_heading[0]),
                    heading_y=float(blended_heading[1]),
                    orientation_x=float(unit.orientation_x),
                    orientation_y=float(unit.orientation_y),
                    velocity_x=float(unit.velocity_x),
                    velocity_y=float(unit.velocity_y),
                    hit_points=float(unit.hit_points),
                    max_hit_points=float(unit.max_hit_points),
                )
            )
        return ViewerFrame(
            tick=int(current_frame.tick),
            units=tuple(smoothed_units),
            targets=dict(current_frame.targets),
        )

    def go_to_frame(self, frame_index: int) -> None:
        self._current_frame_index = max(0, min(int(frame_index), len(self._replay.frames) - 1))
        frame = self._replay.frames[self._current_frame_index]
        self._camera_controller.sync_tracked_frame(frame)
        self._render_frame(frame)
        self._refresh_overlay()

    def _refresh_overlay(self) -> None:
        if not self._hud_enabled:
            return
        frame = self._replay.frames[self._current_frame_index]
        counts_text = _count_units_by_fleet(self._replay, self._current_frame_index)
        playback_label = "playing" if self._playing else "paused"
        vector_display_mode = self._replay.metadata.get("vector_display_mode", "effective")
        fire_link_mode = self._unit_renderer.fire_link_mode
        smoothing_text = "on" if self._smoothing_enabled else "off"
        direction_text = f"dir_mode={vector_display_mode}"
        status_lines = [
            f"{counts_text}  state={playback_label}",
            f"frame={self._current_frame_index + 1}/{len(self._replay.frames)}  fps={self._playback_fps:.1f}  gear={self._playback_level_index + 1}/{len(PLAYBACK_FPS_LEVELS)}",
        ]
        fleet_centroids: dict[str, tuple[float, float, int]] = {}
        for unit in frame.units:
            sum_x, sum_y, count = fleet_centroids.get(unit.fleet_id, (0.0, 0.0, 0))
            fleet_centroids[unit.fleet_id] = (
                float(sum_x) + float(unit.x),
                float(sum_y) + float(unit.y),
                int(count) + 1,
            )
        centroid_parts = []
        for fleet_id in sorted(fleet_centroids):
            sum_x, sum_y, count = fleet_centroids[fleet_id]
            if count <= 0:
                continue
            centroid_parts.append(f"{fleet_id}=({sum_x / count:.1f}, {sum_y / count:.1f})")
        centroid_text = "  ".join(centroid_parts) if centroid_parts else "centroids=n/a"
        status_lines.append(centroid_text)
        status_tail = f"{direction_text}  fire_links={fire_link_mode}  smooth={smoothing_text}"
        fixture_readout = self._replay.metadata.get("fixture_readout")
        if isinstance(fixture_readout, dict) and fixture_readout:
            owner = str(fixture_readout.get("source_owner", ""))
            objective_mode = str(fixture_readout.get("objective_mode", ""))
            no_enemy = str(fixture_readout.get("no_enemy_semantics", ""))
            status_tail = (
                f"{status_tail}  fixture={owner}/{objective_mode}/{no_enemy}"
            )
        status_lines.append(status_tail)
        self._status_text.setText("\n".join(status_lines))
        control_lines = [
            "Space play/pause  N/B step/hold",
            "[/ ] speed gear  V fire-links  M smooth",
            "P portraits  Tab HUD  LDrag pan  RDrag orbit",
            "Wheel zoom  `/~ reset-or-track-off  1/2 track fleet  Esc quit",
        ]
        self._control_text.setText("\n".join(control_lines))

    def _tick(self, task):
        dt = ClockObject.getGlobalClock().getDt()
        self._camera_controller.update(dt)
        if self._held_step_direction != 0 and len(self._replay.frames) > 1:
            if self._held_step_delay_remaining > 0.0:
                self._held_step_delay_remaining = max(0.0, self._held_step_delay_remaining - dt)
            else:
                self._held_step_repeat_accumulator += dt
                while self._held_step_repeat_accumulator >= STEP_HOLD_REPEAT_INTERVAL_SECONDS:
                    self._held_step_repeat_accumulator -= STEP_HOLD_REPEAT_INTERVAL_SECONDS
                    self._step_by(self._held_step_direction)
        if self._playing and len(self._replay.frames) > 1:
            self._accumulator += dt
            frame_period = 1.0 / self._playback_fps
            while self._accumulator >= frame_period:
                self._accumulator -= frame_period
                next_index = self._current_frame_index + 1
                if next_index >= len(self._replay.frames):
                    next_index = 0
                self.go_to_frame(next_index)
            if self._smoothing_active():
                smoothing_alpha = self._accumulator / frame_period
                if smoothing_alpha > 1e-6:
                    smoothed_frame = self._build_smoothed_frame(smoothing_alpha)
                    self._camera_controller.sync_tracked_frame(smoothed_frame)
                    self._render_frame(smoothed_frame)
                    return task.cont
        self._unit_renderer.update_view(self.camera)
        self._sync_fleet_avatar_overlays()
        return task.cont


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=WINDOW_TITLE)
    parser.add_argument(
        "--source",
        choices=VIEWER_SOURCE_CHOICES,
        default=VIEWER_SOURCE_AUTO,
        help=(
            "Viewer replay source. 'auto' follows the current layered fixture.active_mode when it is "
            "neutral_transit_v1; otherwise it uses the active battle path."
        ),
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="Override simulation max_time_steps. When omitted, layered 2D settings semantics are preserved.",
    )
    parser.add_argument("--frame-stride", type=int, default=DEFAULT_FRAME_STRIDE)
    parser.add_argument(
        "--direction-mode",
        choices=VIEWER_DIRECTION_MODE_CHOICES,
        default=VIEWER_DIRECTION_MODE_SETTINGS,
        help=(
            "Viewer-local direction readout mode. 'settings' preserves the current layered "
            "2D vector_display_mode; 'realistic' uses a human-readable short-window travel posture."
        ),
    )
    parser.add_argument(
        "--playback-fps",
        type=float,
        default=PLAYBACK_FPS_LEVELS[DEFAULT_PLAYBACK_LEVEL_INDEX],
        help="Fixed playback speed level. Supported values: 4, 8, 12, 18, 24.",
    )
    parser.add_argument("--window-width", type=int, default=1440)
    parser.add_argument("--window-height", type=int, default=900)
    parser.add_argument(
        "--fire-link-mode",
        choices=FIRE_LINK_MODE_CHOICES,
        default="minimal",
        help="Viewer-local fire-link display mode. Default keeps links subordinate to unit tokens.",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str] | None = None) -> None:
    args = _parse_args(argv)
    loadPrcFileData("", f"window-title {WINDOW_TITLE}")
    loadPrcFileData("", f"win-size {int(args.window_width)} {int(args.window_height)}")
    replay = load_viewer_replay(
        source=str(args.source),
        max_steps=args.steps,
        frame_stride=int(args.frame_stride),
        direction_mode=str(args.direction_mode),
    )
    app = FleetViewerApp(
        replay,
        playback_fps=float(args.playback_fps),
        fire_link_mode=str(args.fire_link_mode),
    )
    app.run()


if __name__ == "__main__":
    main()
