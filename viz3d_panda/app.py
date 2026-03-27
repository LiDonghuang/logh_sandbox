from __future__ import annotations

import argparse
from typing import Sequence

try:
    from direct.gui.OnscreenText import OnscreenText
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import ClockObject, TextNode, loadPrcFileData
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
    load_viewer_replay,
)
from viz3d_panda.scene_builder import build_scene
from viz3d_panda.unit_renderer import FIRE_LINK_MODES, UnitRenderer


WINDOW_TITLE = "LOGH dev_v2.0 Panda3D Viewer Scaffold"
PLAYBACK_FPS_LEVELS = (4.0, 8.0, 12.0, 18.0, 24.0)
DEFAULT_PLAYBACK_LEVEL_INDEX = 2
FIRE_LINK_MODE_CHOICES = tuple(sorted(FIRE_LINK_MODES))
STEP_HOLD_INITIAL_DELAY_SECONDS = 0.35
STEP_HOLD_REPEAT_INTERVAL_SECONDS = 0.08


def _configure_window(*, width: int, height: int) -> None:
    loadPrcFileData("", f"window-title {WINDOW_TITLE}")
    loadPrcFileData("", f"win-size {int(width)} {int(height)}")


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


def _format_point(values: object, *, dimensions: int) -> str | None:
    if not isinstance(values, (list, tuple)) or len(values) != dimensions:
        return None
    try:
        parts = [f"{float(value):.1f}" for value in values]
    except (TypeError, ValueError):
        return None
    return f"({', '.join(parts)})"


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
        self._held_step_direction = 0
        self._held_step_delay_remaining = 0.0
        self._held_step_repeat_accumulator = 0.0

        self._scene_root = build_scene(self.render, arena_size=self._replay.arena_size)
        self._unit_renderer = UnitRenderer(self._scene_root, self._replay, fire_link_mode=fire_link_mode)
        self._camera_controller = OrbitCameraController(self, arena_size=self._replay.arena_size)

        self._status_text = OnscreenText(
            text="",
            parent=self.a2dTopLeft,
            pos=(0.03, -0.06),
            scale=0.05,
            align=TextNode.ALeft,
            fg=(0.93, 0.95, 0.98, 1.0),
        )
        self._control_text = OnscreenText(
            text=(
                "Space play/pause  N/B step/hold  [/ ] speed gear  V fire-links\n"
                "LDrag pan  RDrag orbit  Wheel zoom  `/~ reset-or-track-off  1/2 track fleet  Esc quit"
            ),
            parent=self.aspect2d,
            pos=(-1.28, -0.95),
            scale=0.042,
            align=TextNode.ALeft,
            fg=(0.72, 0.80, 0.89, 1.0),
        )

        self.accept("space", self.toggle_playback)
        self.accept("n", self._begin_hold_step, [1])
        self.accept("n-up", self._end_hold_step, [1])
        self.accept("b", self._begin_hold_step, [-1])
        self.accept("b-up", self._end_hold_step, [-1])
        self.accept("v", self.cycle_fire_link_mode)
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
        self._refresh_overlay()

    def cycle_fire_link_mode(self) -> None:
        current_index = FIRE_LINK_MODE_CHOICES.index(self._unit_renderer.fire_link_mode)
        next_index = (current_index + 1) % len(FIRE_LINK_MODE_CHOICES)
        self._unit_renderer.set_fire_link_mode(FIRE_LINK_MODE_CHOICES[next_index])
        self.go_to_frame(self._current_frame_index)

    def toggle_playback(self) -> None:
        self._playing = not self._playing
        self._refresh_overlay()

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

    def go_to_frame(self, frame_index: int) -> None:
        self._current_frame_index = max(0, min(int(frame_index), len(self._replay.frames) - 1))
        frame = self._replay.frames[self._current_frame_index]
        self._unit_renderer.sync_frame(frame)
        self._camera_controller.sync_tracked_frame(frame)
        self._unit_renderer.update_view(self.camera)
        self._refresh_overlay()

    def _refresh_overlay(self) -> None:
        frame = self._replay.frames[self._current_frame_index]
        counts_text = _count_units_by_fleet(self._replay, self._current_frame_index)
        playback_label = "playing" if self._playing else "paused"
        max_steps_effective = self._replay.metadata.get("max_steps_effective")
        max_steps_source = self._replay.metadata.get("max_steps_source", "settings")
        vector_display_mode = self._replay.metadata.get("vector_display_mode", "effective")
        settings_vector_display_mode = self._replay.metadata.get("settings_vector_display_mode", vector_display_mode)
        direction_mode_source = self._replay.metadata.get("direction_mode_source", "settings")
        fire_link_mode = self._unit_renderer.fire_link_mode
        if direction_mode_source == "override":
            direction_text = f"dir_mode={vector_display_mode}  settings_dir={settings_vector_display_mode}"
        else:
            direction_text = f"dir_mode={vector_display_mode}"
        status_lines = [
            WINDOW_TITLE,
            f"source={self._replay.source_kind}  frame={self._current_frame_index + 1}/{len(self._replay.frames)}  tick={frame.tick}",
            f"fps={self._playback_fps:.1f}  gear={self._playback_level_index + 1}/{len(PLAYBACK_FPS_LEVELS)}  state={playback_label}",
            f"sim_limit={max_steps_source}:{max_steps_effective}  {direction_text}  fire_links={fire_link_mode}",
        ]
        fixture_readout = self._replay.metadata.get("fixture_readout")
        if isinstance(fixture_readout, dict) and fixture_readout:
            owner = str(fixture_readout.get("source_owner", ""))
            objective_mode = str(fixture_readout.get("objective_mode", ""))
            no_enemy = str(fixture_readout.get("no_enemy_semantics", ""))
            status_lines.append(f"fixture_contract owner={owner}  mode={objective_mode}  no_enemy={no_enemy}")
            anchor_xyz = _format_point(fixture_readout.get("anchor_point_xyz"), dimensions=3)
            if anchor_xyz is not None:
                projected_xy = _format_point(fixture_readout.get("projected_anchor_point_xy"), dimensions=2)
                if projected_xy is None:
                    status_lines.append(f"anchor_xyz={anchor_xyz}")
                else:
                    status_lines.append(f"anchor_xyz={anchor_xyz}  projected_xy={projected_xy}")
        status_lines.append(counts_text)
        self._status_text.setText("\n".join(status_lines))

    def _tick(self, task):
        dt = ClockObject.getGlobalClock().getDt()
        self._camera_controller.update(dt)
        self._unit_renderer.update_view(self.camera)
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
            "2D vector_display_mode; 'realistic' uses realized local trajectory tangent."
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
    _configure_window(width=args.window_width, height=args.window_height)
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
