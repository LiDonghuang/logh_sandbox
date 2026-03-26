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
from viz3d_panda.replay_source import DEFAULT_FRAME_STRIDE, ReplayBundle, load_active_battle_replay
from viz3d_panda.scene_builder import build_scene
from viz3d_panda.unit_renderer import FIRE_LINK_MODES, UnitRenderer


WINDOW_TITLE = "LOGH dev_v2.0 Panda3D Viewer Scaffold"
PLAYBACK_FPS_LEVELS = (4.0, 8.0, 12.0, 18.0, 24.0)
DEFAULT_PLAYBACK_LEVEL_INDEX = 2
FIRE_LINK_MODE_CHOICES = tuple(sorted(FIRE_LINK_MODES))


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
                "Space play/pause  N/B step  [/ ] speed gear  V fire-links\n"
                "LDrag pan  RDrag orbit  Wheel zoom  C reset  Esc quit"
            ),
            parent=self.aspect2d,
            pos=(-1.28, -0.95),
            scale=0.042,
            align=TextNode.ALeft,
            fg=(0.72, 0.80, 0.89, 1.0),
        )

        self.accept("space", self.toggle_playback)
        self.accept("n", self.step_forward)
        self.accept("b", self.step_backward)
        self.accept("v", self.cycle_fire_link_mode)
        self.accept("]", self._adjust_playback_speed, [1])
        self.accept("[", self._adjust_playback_speed, [-1])
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

    def step_forward(self) -> None:
        self._playing = False
        self.go_to_frame(min(self._current_frame_index + 1, len(self._replay.frames) - 1))

    def step_backward(self) -> None:
        self._playing = False
        self.go_to_frame(max(self._current_frame_index - 1, 0))

    def go_to_frame(self, frame_index: int) -> None:
        self._current_frame_index = max(0, min(int(frame_index), len(self._replay.frames) - 1))
        frame = self._replay.frames[self._current_frame_index]
        self._unit_renderer.sync_frame(frame)
        self._refresh_overlay()

    def _refresh_overlay(self) -> None:
        frame = self._replay.frames[self._current_frame_index]
        counts_text = _count_units_by_fleet(self._replay, self._current_frame_index)
        playback_label = "playing" if self._playing else "paused"
        max_steps_effective = self._replay.metadata.get("max_steps_effective")
        max_steps_source = self._replay.metadata.get("max_steps_source", "settings")
        vector_display_mode = self._replay.metadata.get("vector_display_mode", "effective")
        fire_link_mode = self._unit_renderer.fire_link_mode
        self._status_text.setText(
            f"{WINDOW_TITLE}\n"
            f"source={self._replay.source_kind}  frame={self._current_frame_index + 1}/{len(self._replay.frames)}  tick={frame.tick}\n"
            f"fps={self._playback_fps:.1f}  gear={self._playback_level_index + 1}/{len(PLAYBACK_FPS_LEVELS)}  state={playback_label}\n"
            f"sim_limit={max_steps_source}:{max_steps_effective}  dir_mode={vector_display_mode}  fire_links={fire_link_mode}\n"
            f"{counts_text}"
        )

    def _tick(self, task):
        dt = ClockObject.getGlobalClock().getDt()
        self._camera_controller.update(dt)
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
        "--steps",
        type=int,
        default=None,
        help="Override simulation max_time_steps. When omitted, layered 2D settings semantics are preserved.",
    )
    parser.add_argument("--frame-stride", type=int, default=DEFAULT_FRAME_STRIDE)
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
    replay = load_active_battle_replay(
        max_steps=args.steps,
        frame_stride=int(args.frame_stride),
    )
    app = FleetViewerApp(
        replay,
        playback_fps=float(args.playback_fps),
        fire_link_mode=str(args.fire_link_mode),
    )
    app.run()


if __name__ == "__main__":
    main()
