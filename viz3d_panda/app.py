from __future__ import annotations

import argparse
import json
import math
import subprocess
import time
from pathlib import Path
from typing import Any, Sequence

try:
    from direct.gui.DirectFrame import DirectFrame
    from direct.gui.OnscreenImage import OnscreenImage
    from direct.gui.OnscreenText import OnscreenText
    from direct.showbase.ShowBase import ShowBase
    from panda3d.core import ClockObject, Filename, GraphicsOutput, Point2, Point3, TextNode, Texture, TransparencyAttrib, loadPrcFileData
except ImportError as exc:  # pragma: no cover - import guard for incorrect env usage
    raise SystemExit(
        "Panda3D is not available in the current interpreter. "
        "Use .venv_dev_v2_0\\Scripts\\python.exe -m viz3d_panda.app ..."
    ) from exc

from viz3d_panda.camera_controller import OrbitCameraController
from viz3d_panda import replay_source
from viz3d_panda.replay_source import (
    DEFAULT_FRAME_STRIDE,
    TEST_RUN_BASE_DIR,
    VIEWER_DIRECTION_MODE_CHOICES,
    VIEWER_DIRECTION_MODE_SETTINGS,
    VIEWER_SOURCE_AUTO,
    VIEWER_SOURCE_ACTIVE_BATTLE,
    VIEWER_SOURCE_NEUTRAL_TRANSIT_FIXTURE,
    VIEWER_SOURCE_CHOICES,
    ReplayBundle,
    ViewerFrame,
    rebuild_replay_direction_mode,
    load_viewer_replay,
)
from viz3d_panda.scene_builder import build_scene
from viz3d_panda.unit_renderer import FIRE_LINK_MODES, UnitRenderer


WINDOW_TITLE = "LOGH dev_v2.0 Panda3D Viewer Scaffold"
AVATAR_DIR = Path(__file__).resolve().parents[1] / "visual" / "avatars"
PLAYBACK_FPS_LEVELS = (2.0, 4.0, 6.0, 10.0, 20.0)
DEFAULT_PLAYBACK_LEVEL_INDEX = 2
FIRE_LINK_MODE_CHOICES = tuple(sorted(FIRE_LINK_MODES))
PRIMARY_DIRECTION_MODE_CYCLE = ("movement", "posture")
STEP_HOLD_INITIAL_DELAY_SECONDS = 0.35
STEP_HOLD_REPEAT_INTERVAL_SECONDS = 0.08
LOW_SPEED_SMOOTHING_MAX_FPS = PLAYBACK_FPS_LEVELS[-1]
HUD_BOTTOM_INSET = 0.05
HUD_SIDE_INSET = 0.03
HUD_TEXT_SCALE = 0.038
CAMERA_TAKE_FORMAT = "viz3d_panda_camera_take"
CAMERA_TAKE_FORMAT_VERSION = 1
CAMERA_TAKE_RECORD_KEY = "k"
CAMERA_TAKE_NOTICE_SECONDS = 2.6
CAMERA_TAKE_FLOAT_DIGITS = 6
CAMERA_TAKE_REC_SCALE = 0.050
CAMERA_TAKE_NOTICE_SCALE = 0.032
DEFAULT_CAMERA_TAKE_OUTPUT_PATH = Path("analysis/exports/videos/dev_v2_0_camera_take.json")
DEFAULT_VIDEO_EXPORT_DIR = Path("analysis/exports/videos")
FLEET_AVATAR_HEIGHT = 0.042
FLEET_AVATAR_ASPECT_RATIO = 1.0
FLEET_AVATAR_SCREEN_NUDGE = 0.008
FLEET_AVATAR_MIN_SCREEN_OFFSET = 0.050
FLEET_AVATAR_MAX_SCREEN_OFFSET = 0.082
FLEET_AVATAR_BORDER_PAD = 0.0045
FLEET_AVATAR_MATTE_PAD = 0.002
FLEET_AVATAR_HIGHLIGHT_PAD = 0.009
FLEET_AVATAR_HIGHLIGHT_ALPHA = 0.48
FLEET_AVATAR_MATTE_COLOR = (0.02, 0.03, 0.05, 0.82)
FLEET_AVATAR_BORDER_ALPHA = 1.0
FLEET_AVATAR_PAIR_ENTER_DISTANCE_X = 0.24
FLEET_AVATAR_PAIR_ENTER_DISTANCE_Z = 0.16
FLEET_AVATAR_PAIR_EXIT_DISTANCE_X = 0.30
FLEET_AVATAR_PAIR_EXIT_DISTANCE_Z = 0.20
FLEET_AVATAR_PAIR_SEPARATION_X = 0.12
# 头像区块 (avatar block): fixed corner portrait + bar + labels.
CORNER_AVATAR_HEIGHT = 0.105
CORNER_AVATAR_ASPECT_RATIO = 4.0 / 5.0
CORNER_AVATAR_BORDER_PAD = 0.006
CORNER_AVATAR_INSET_X = 0.12
CORNER_AVATAR_INSET_Z = 0.20
CORNER_AVATAR_ALIGNMENT_OVERSHOOT = 0.010
CORNER_AVATAR_NAME_OFFSET = 0.046
CORNER_AVATAR_TEXT_GAP = 0.008
CORNER_AVATAR_BAR_OFFSET = 0.024
CORNER_AVATAR_BAR_WIDTH = CORNER_AVATAR_HEIGHT * CORNER_AVATAR_ASPECT_RATIO * 4.0
CORNER_AVATAR_BAR_HEIGHT = 0.016
CORNER_AVATAR_TEXT_SCALE = 0.034
CORNER_AVATAR_NAME_SCALE = 0.034
CORNER_AVATAR_BAR_BG = (0.10, 0.14, 0.18, 0.92)
CORNER_AVATAR_BAR_FILL = (0.0, 1.0, 0.0, 0.98)
CORNER_AVATAR_TEXT_COLOR = (0.92, 0.95, 0.98, 1.0)
CJK_FONT_CANDIDATES = (
    Path("C:/Windows/Fonts/simhei.ttf"),
    Path("C:/Windows/Fonts/msyh.ttc"),
    Path("C:/Windows/Fonts/NotoSansSC-VF.ttf"),
    Path("C:/Windows/Fonts/simsun.ttc"),
)


def _resolve_avatar_image_path(avatar_id: object, *, preferred_size: str | None = None) -> Path | None:
    stem = str(avatar_id).strip() if avatar_id is not None else ""
    if not stem:
        return None
    suffixes = (".png", ".jpg", ".jpeg", ".webp", ".bmp")
    candidate_names: list[str] = []
    if "." in stem:
        candidate_names.append(stem)
    else:
        candidate_stems = [stem]
        if stem.startswith("avatar_") and not stem.endswith(("_m", "_s")):
            if preferred_size in {"m", "s"}:
                candidate_stems = [f"{stem}_{preferred_size}", stem]
            else:
                candidate_stems = [stem]
        for candidate_stem in candidate_stems:
            candidate_names.extend([f"{candidate_stem}{suffix}" for suffix in suffixes])
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


def _alive_counts(frame: ViewerFrame) -> dict[str, int]:
    counts: dict[str, int] = {}
    for unit in frame.units:
        if float(unit.hit_points) <= 0.0:
            continue
        counts[unit.fleet_id] = counts.get(unit.fleet_id, 0) + 1
    return counts


def _format_launch_matchup(replay: ReplayBundle) -> str:
    first_frame = replay.frames[0]
    counts = _alive_counts(first_frame)
    parts = []
    for fleet_id in sorted(counts):
        label = replay.fleet_labels.get(fleet_id, fleet_id)
        parts.append(f"{label} ({counts[fleet_id]})")
    return " vs ".join(parts) if parts else "no fleets"


def _format_launch_result(replay: ReplayBundle) -> str:
    last_frame = replay.frames[-1]
    alive_counts = _alive_counts(last_frame)
    last_tick = int(last_frame.tick)
    if len(alive_counts) == 1:
        fleet_id = next(iter(alive_counts))
        label = replay.fleet_labels.get(fleet_id, fleet_id)
        return f"end tick={last_tick}, {label} ({alive_counts[fleet_id]} alive)"
    if len(alive_counts) >= 2:
        ranked = sorted(alive_counts.items(), key=lambda item: (-int(item[1]), str(item[0])))
        top_fleet_id, top_alive = ranked[0]
        second_alive = int(ranked[1][1])
        if int(top_alive) > second_alive:
            label = replay.fleet_labels.get(top_fleet_id, top_fleet_id)
            return f"end tick={last_tick}, {label} win ({top_alive} alive)"
        parts = []
        for fleet_id, alive in ranked:
            label = replay.fleet_labels.get(fleet_id, fleet_id)
            parts.append(f"{label} {alive} alive")
        return f"end tick={last_tick}, {' / '.join(parts)}"
    return f"end tick={last_tick}, no surviving units"


def _preview_launch_setup(requested_source: str) -> tuple[str, str]:
    settings = replay_source.settings_api.load_layered_test_run_settings(TEST_RUN_BASE_DIR)
    resolved_source = replay_source._resolve_viewer_source(settings, str(requested_source))
    if resolved_source == VIEWER_SOURCE_NEUTRAL_TRANSIT_FIXTURE:
        prepared = replay_source.scenario.prepare_neutral_transit_fixture(TEST_RUN_BASE_DIR, settings_override=settings)
        fleet_data = prepared["fleet_data"]
        labels = {
            "A": replay_source.scenario.resolve_display_name(fleet_data, "EN") or "A",
        }
    elif resolved_source == VIEWER_SOURCE_ACTIVE_BATTLE:
        prepared = replay_source.scenario.prepare_active_scenario(TEST_RUN_BASE_DIR, settings_override=settings)
        labels = {
            "A": replay_source.scenario.resolve_display_name(prepared["fleet_a_data"], "EN") or "A",
            "B": replay_source.scenario.resolve_display_name(prepared["fleet_b_data"], "EN") or "B",
        }
    else:
        raise ValueError(f"unsupported viewer source preview: {resolved_source!r}")
    state = prepared["initial_state"]
    counts: dict[str, int] = {}
    for unit in state.units.values():
        fleet_id = str(unit.fleet_id)
        counts[fleet_id] = counts.get(fleet_id, 0) + 1
    matchup_parts = []
    for fleet_id in sorted(counts):
        matchup_parts.append(f"{labels.get(fleet_id, fleet_id)} ({counts[fleet_id]})")
    matchup_text = " vs ".join(matchup_parts) if matchup_parts else "no fleets"
    map_text = f"map: {float(state.arena_size):.0f} x {float(state.arena_size):.0f} x 1"
    return matchup_text, map_text


def _resolve_playback_level_index(playback_fps: float) -> int:
    requested = float(playback_fps)
    for index, level in enumerate(PLAYBACK_FPS_LEVELS):
        if abs(requested - float(level)) <= 1e-9:
            return index
    supported_values = ", ".join(f"{level:.0f}" if float(level).is_integer() else f"{level}" for level in PLAYBACK_FPS_LEVELS)
    raise ValueError(
        f"playback-fps must be one of the fixed viewer speed levels: {supported_values}; got {playback_fps}."
    )


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


def _resolve_cjk_font_path() -> Path | None:
    for path in CJK_FONT_CANDIDATES:
        if path.exists():
            return path
    return None


def _initial_total_hp_by_fleet(frame: ViewerFrame) -> dict[str, float]:
    totals: dict[str, float] = {}
    for unit in frame.units:
        fleet_id = str(unit.fleet_id)
        totals[fleet_id] = totals.get(fleet_id, 0.0) + max(0.0, float(unit.hit_points))
    return totals


def _resolve_output_path(path_text: str) -> Path:
    candidate = Path(str(path_text))
    if candidate.suffix.lower() not in {".json", ".mp4"}:
        raise ValueError(f"unsupported output path suffix for {candidate!s}; expected .json or .mp4")
    if candidate.is_absolute():
        return candidate
    return (Path.cwd() / candidate).resolve()


def _resolve_default_camera_take_output_path() -> Path:
    return (Path.cwd() / DEFAULT_CAMERA_TAKE_OUTPUT_PATH).resolve()


def _resolve_default_video_export_path(*, take_path: Path) -> Path:
    return ((Path.cwd() / DEFAULT_VIDEO_EXPORT_DIR).resolve() / f"{take_path.stem}.mp4").resolve()


def _round_take_float(value: float) -> float:
    return round(float(value), CAMERA_TAKE_FLOAT_DIGITS)


def _resolve_explicit_ffmpeg_exe(path_text: str) -> str:
    candidate = Path(str(path_text))
    resolved = candidate if candidate.is_absolute() else (Path.cwd() / candidate).resolve()
    if not resolved.exists():
        raise FileNotFoundError(f"ffmpeg executable not found: {resolved}")
    if not resolved.is_file():
        raise ValueError(f"--ffmpeg-exe must point to a file, got {resolved}.")
    return str(resolved)


def _resolved_viewer_source_for_replay(replay: ReplayBundle) -> str:
    if replay.source_kind == "test_run_neutral_transit_fixture":
        return VIEWER_SOURCE_NEUTRAL_TRANSIT_FIXTURE
    if replay.source_kind == "test_run_active_surface":
        return VIEWER_SOURCE_ACTIVE_BATTLE
    raise ValueError(f"unsupported replay source kind for camera take export: {replay.source_kind!r}.")


def _build_camera_take_context(
    replay: ReplayBundle,
    *,
    playback_fps: float,
    fire_link_mode: str,
    window_width: int,
    window_height: int,
) -> dict[str, Any]:
    direction_mode = str(replay.metadata.get("vector_display_mode", "effective")).strip().lower()
    if direction_mode not in VIEWER_DIRECTION_MODE_CHOICES:
        allowed = ", ".join(VIEWER_DIRECTION_MODE_CHOICES)
        raise ValueError(
            f"camera take export requires a viewer direction mode in {{{allowed}}}; "
            f"got {replay.metadata.get('vector_display_mode')!r}."
        )
    return {
        "source": _resolved_viewer_source_for_replay(replay),
        "max_steps": int(replay.metadata.get("max_steps_effective", -1)),
        "frame_stride": int(replay.metadata.get("frame_stride", DEFAULT_FRAME_STRIDE)),
        "direction_mode": direction_mode,
        "playback_fps": float(playback_fps),
        "fire_link_mode": str(fire_link_mode),
        "window_width": int(window_width),
        "window_height": int(window_height),
    }


def _validate_camera_take_payload(payload: Any, *, source_path: Path) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError(f"camera take file must contain a JSON object: {source_path}")
    if payload.get("format") != CAMERA_TAKE_FORMAT:
        raise ValueError(
            f"camera take format mismatch in {source_path}; expected {CAMERA_TAKE_FORMAT!r}, got {payload.get('format')!r}."
        )
    if int(payload.get("format_version", -1)) != CAMERA_TAKE_FORMAT_VERSION:
        raise ValueError(
            f"camera take format_version must be {CAMERA_TAKE_FORMAT_VERSION}, got {payload.get('format_version')!r}."
        )
    replay_request = payload.get("replay_request")
    if not isinstance(replay_request, dict):
        raise ValueError(f"camera take replay_request must be an object: {source_path}")
    required_replay_fields = (
        "source",
        "max_steps",
        "frame_stride",
        "direction_mode",
        "playback_fps",
        "fire_link_mode",
        "window_width",
        "window_height",
    )
    for field_name in required_replay_fields:
        if field_name not in replay_request:
            raise ValueError(f"camera take replay_request is missing {field_name!r}: {source_path}")
    samples = payload.get("samples")
    if not isinstance(samples, list) or not samples:
        raise ValueError(f"camera take samples must be a non-empty array: {source_path}")
    previous_elapsed = -1.0
    for sample_index, sample in enumerate(samples):
        if not isinstance(sample, dict):
            raise ValueError(f"camera take sample {sample_index} must be an object: {source_path}")
        for field_name in ("elapsed_s", "frame_index", "tick", "position_alpha", "pulse_phase", "camera", "viewer"):
            if field_name not in sample:
                raise ValueError(f"camera take sample {sample_index} is missing {field_name!r}: {source_path}")
        camera_state = sample.get("camera")
        viewer_state = sample.get("viewer")
        if not isinstance(camera_state, dict):
            raise ValueError(f"camera take sample {sample_index} camera state must be an object: {source_path}")
        if not isinstance(viewer_state, dict):
            raise ValueError(f"camera take sample {sample_index} viewer state must be an object: {source_path}")
        for field_name in ("focus_x", "focus_y", "yaw_deg", "pitch_deg", "distance", "tracked_fleet_id"):
            if field_name not in camera_state:
                raise ValueError(
                    f"camera take sample {sample_index} camera state is missing {field_name!r}: {source_path}"
                )
        for field_name in (
            "playing",
            "smoothing_enabled",
            "avatars_enabled",
            "hud_enabled",
            "fire_link_mode",
            "playback_level_index",
            "playback_fps",
        ):
            if field_name not in viewer_state:
                raise ValueError(
                    f"camera take sample {sample_index} viewer state is missing {field_name!r}: {source_path}"
                )
        elapsed = float(sample.get("elapsed_s", -1.0))
        if elapsed < previous_elapsed - 1e-9:
            raise ValueError(f"camera take sample times must be non-decreasing: {source_path}")
        previous_elapsed = elapsed
    return payload


def _load_camera_take_payload(path_text: str) -> tuple[Path, dict[str, Any]]:
    take_path = _resolve_output_path(str(path_text))
    if take_path.suffix.lower() != ".json":
        raise ValueError(f"--export-camera-take must point to a .json file, got {take_path}.")
    if not take_path.exists():
        raise FileNotFoundError(f"camera take file not found: {take_path}")
    try:
        payload = json.loads(take_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"camera take file is not valid JSON: {take_path}") from exc
    return take_path, _validate_camera_take_payload(payload, source_path=take_path)


def _trim_invalid_terminal_camera_take_samples(
    samples: Sequence[dict[str, Any]],
    *,
    replay_frame_count: int,
) -> list[dict[str, Any]]:
    if replay_frame_count < 1:
        raise ValueError("camera take export requires replay_frame_count >= 1.")
    trimmed_samples = list(samples)
    invalid_terminal_count = 0
    last_frame_index = replay_frame_count - 1
    while trimmed_samples:
        tail_sample = trimmed_samples[-1]
        tail_frame_index = int(tail_sample["frame_index"])
        tail_position_alpha = float(tail_sample["position_alpha"])
        if tail_frame_index != last_frame_index or tail_position_alpha <= 1e-6:
            break
        trimmed_samples.pop()
        invalid_terminal_count += 1
    if not trimmed_samples:
        raise ValueError(
            "camera take export cannot proceed because every trailing sample requested interpolation past the final replay frame."
        )
    if invalid_terminal_count > 0:
        print(
            "[CAMERA TAKE EXPORT] dropped "
            f"{invalid_terminal_count} trailing sample(s) that requested interpolation past the final replay frame"
        )
    return trimmed_samples


class FleetViewerApp(ShowBase):
    def __init__(
        self,
        replay: ReplayBundle,
        *,
        playback_fps: float,
        fire_link_mode: str,
        camera_take_output_path: Path | None = None,
        camera_take_context: dict[str, Any] | None = None,
    ) -> None:
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
        self._current_display_position_alpha = 0.0
        self._current_display_pulse_phase = 0.0
        self._camera_take_output_path = camera_take_output_path
        self._camera_take_context = dict(camera_take_context or {})
        self._camera_take_recording = False
        self._camera_take_started_at = 0.0
        self._camera_take_samples: list[dict[str, Any]] = []
        self._camera_take_last_signature: tuple[Any, ...] | None = None
        self._camera_take_notice_message = ""
        self._camera_take_notice_seconds_remaining = 0.0

        self._scene_root = build_scene(self.render, arena_size=self._replay.arena_size)
        self._unit_renderer = UnitRenderer(self._scene_root, self._replay, fire_link_mode=fire_link_mode)
        self._unit_renderer.set_playback_level_index(self._playback_level_index)
        self._unit_renderer.set_playback_fps(self._playback_fps)
        self._camera_controller = OrbitCameraController(self, arena_size=self._replay.arena_size)
        self._camera_controller.set_playback_level_index(self._playback_level_index)
        self._direction_mode_replay_cache: dict[str, ReplayBundle] = {}
        current_direction_mode = str(self._replay.metadata.get("vector_display_mode", "posture")).strip().lower()
        self._direction_mode_replay_cache[current_direction_mode] = self._replay
        for cached_mode in PRIMARY_DIRECTION_MODE_CYCLE:
            if cached_mode in self._direction_mode_replay_cache:
                continue
            self._direction_mode_replay_cache[cached_mode] = rebuild_replay_direction_mode(
                self._replay,
                direction_mode=cached_mode,
                direction_mode_source="viewer_prebuilt_cache",
            )
        self._fleet_avatar_nodes: dict[str, dict[str, object]] = {}
        self._corner_avatar_nodes: dict[str, dict[str, object]] = {}
        self._fleet_avatar_pair_layout_active = False
        self._fleet_avatar_world_lift = max(8.0, float(self._replay.arena_size) * 0.03)
        self._fleet_initial_total_hp = _initial_total_hp_by_fleet(self._replay.frames[0])
        self._ui_font = None
        cjk_font_path = _resolve_cjk_font_path()
        if cjk_font_path is not None:
            self._ui_font = self.loader.loadFont(Filename.fromOsSpecific(str(cjk_font_path)).getFullpath())

        self._status_text = OnscreenText(
            text="",
            parent=self.a2dBottomLeft,
            pos=(HUD_SIDE_INSET, HUD_BOTTOM_INSET),
            scale=HUD_TEXT_SCALE,
            align=TextNode.ALeft,
            fg=(0.72, 0.80, 0.89, 1.0),
        )
        self._control_text = OnscreenText(
            text="",
            parent=self.a2dBottomRight,
            pos=(-HUD_SIDE_INSET, HUD_BOTTOM_INSET),
            scale=HUD_TEXT_SCALE,
            align=TextNode.ARight,
            fg=(0.72, 0.80, 0.89, 1.0),
        )
        self._camera_take_indicator_text = OnscreenText(
            text="",
            parent=self.a2dTopLeft,
            pos=(HUD_SIDE_INSET, -HUD_BOTTOM_INSET),
            scale=CAMERA_TAKE_REC_SCALE,
            align=TextNode.ALeft,
            fg=(0.95, 0.20, 0.20, 1.0),
        )
        self._camera_take_notice_text = OnscreenText(
            text="",
            parent=self.a2dTopLeft,
            pos=(HUD_SIDE_INSET, -(HUD_BOTTOM_INSET + 0.07)),
            scale=CAMERA_TAKE_NOTICE_SCALE,
            align=TextNode.ALeft,
            fg=(0.97, 0.93, 0.82, 1.0),
        )
        self._build_avatar_overlays()
        self._refresh_camera_take_overlay()

        self.accept("space", self.toggle_playback)
        self.accept("n", self._begin_hold_step, [1])
        self.accept("n-up", self._end_hold_step, [1])
        self.accept("b", self._begin_hold_step, [-1])
        self.accept("b-up", self._end_hold_step, [-1])
        self.accept("v", self.cycle_fire_link_mode)
        self.accept("d", self.cycle_direction_mode)
        self.accept("m", self.toggle_smoothing)
        self.accept("p", self.toggle_avatars)
        self.accept("tab", self.toggle_hud)
        self.accept("]", self._adjust_playback_speed, [1])
        self.accept("[", self._adjust_playback_speed, [-1])
        self.accept("1", self._focus_fleet_camera, ["A"])
        self.accept("2", self._focus_fleet_camera, ["B"])
        self.accept(CAMERA_TAKE_RECORD_KEY, self.toggle_camera_take_recording)
        self.accept("home", self._jump_to_boundary_frame, [0])
        self.accept("end", self._jump_to_boundary_frame, [len(self._replay.frames) - 1])
        self.accept("escape", self._request_exit)

        self.go_to_frame(0)
        self.taskMgr.add(self._tick, "fleet_viewer_tick")

    def _set_display_timing(self, *, position_alpha: float, pulse_phase: float) -> None:
        self._current_display_position_alpha = max(0.0, min(1.0, float(position_alpha)))
        self._current_display_pulse_phase = max(0.0, min(1.0, float(pulse_phase)))

    def _viewer_state_snapshot(self) -> dict[str, Any]:
        return {
            "playing": bool(self._playing),
            "smoothing_enabled": bool(self._smoothing_enabled),
            "avatars_enabled": bool(self._avatars_enabled),
            "hud_enabled": bool(self._hud_enabled),
            "fire_link_mode": str(self._unit_renderer.fire_link_mode),
            "playback_level_index": int(self._playback_level_index),
            "playback_fps": _round_take_float(self._playback_fps),
        }

    def _apply_viewer_state_snapshot(self, state: dict[str, Any]) -> None:
        self._playing = bool(state["playing"])
        self._smoothing_enabled = bool(state["smoothing_enabled"])
        self._avatars_enabled = bool(state["avatars_enabled"])
        self._hud_enabled = bool(state["hud_enabled"])
        self._playback_level_index = max(0, int(state["playback_level_index"]))
        self._playback_fps = float(state["playback_fps"])
        self._unit_renderer.set_fire_link_mode(str(state["fire_link_mode"]))
        self._unit_renderer.set_playback_level_index(self._playback_level_index)
        self._unit_renderer.set_playback_fps(self._playback_fps)
        self._camera_controller.set_playback_level_index(self._playback_level_index)
        if self._hud_enabled:
            self._status_text.show()
            self._control_text.show()
        else:
            self._status_text.hide()
            self._control_text.hide()

    def _set_camera_take_notice(self, message: str, *, duration_seconds: float = CAMERA_TAKE_NOTICE_SECONDS) -> None:
        self._camera_take_notice_message = str(message).strip()
        self._camera_take_notice_seconds_remaining = max(0.0, float(duration_seconds))
        self._refresh_camera_take_overlay()

    def _refresh_camera_take_overlay(self) -> None:
        self._camera_take_indicator_text.setText("REC" if self._camera_take_recording else "")
        self._camera_take_notice_text.setText(self._camera_take_notice_message)

    def _capture_camera_take_sample(self, *, frame: ViewerFrame, force: bool = False) -> None:
        if not self._camera_take_recording:
            return
        camera_state_raw = self._camera_controller.snapshot_state()
        camera_state = {
            "focus_x": _round_take_float(float(camera_state_raw["focus_x"])),
            "focus_y": _round_take_float(float(camera_state_raw["focus_y"])),
            "yaw_deg": _round_take_float(float(camera_state_raw["yaw_deg"])),
            "pitch_deg": _round_take_float(float(camera_state_raw["pitch_deg"])),
            "distance": _round_take_float(float(camera_state_raw["distance"])),
            "tracked_fleet_id": (
                None
                if camera_state_raw["tracked_fleet_id"] is None
                else str(camera_state_raw["tracked_fleet_id"])
            ),
        }
        viewer_state = self._viewer_state_snapshot()
        sample = {
            "elapsed_s": _round_take_float(max(0.0, time.perf_counter() - self._camera_take_started_at)),
            "frame_index": int(self._current_frame_index),
            "tick": int(frame.tick),
            "position_alpha": _round_take_float(self._current_display_position_alpha),
            "pulse_phase": _round_take_float(self._current_display_pulse_phase),
            "camera": camera_state,
            "viewer": viewer_state,
        }
        signature = (
            int(sample["frame_index"]),
            int(sample["tick"]),
            float(sample["position_alpha"]),
            float(sample["pulse_phase"]),
            float(camera_state["focus_x"]),
            float(camera_state["focus_y"]),
            float(camera_state["yaw_deg"]),
            float(camera_state["pitch_deg"]),
            float(camera_state["distance"]),
            camera_state["tracked_fleet_id"],
            bool(viewer_state["playing"]),
            bool(viewer_state["smoothing_enabled"]),
            bool(viewer_state["avatars_enabled"]),
            bool(viewer_state["hud_enabled"]),
            str(viewer_state["fire_link_mode"]),
            int(viewer_state["playback_level_index"]),
            float(viewer_state["playback_fps"]),
        )
        if not force and signature == self._camera_take_last_signature:
            return
        self._camera_take_last_signature = signature
        self._camera_take_samples.append(sample)

    def _build_camera_take_payload(self) -> dict[str, Any]:
        if not self._camera_take_context:
            raise ValueError("camera take recording requires an explicit replay/export context.")
        if not self._camera_take_samples:
            raise ValueError("camera take recording produced no samples; nothing to save.")
        return {
            "format": CAMERA_TAKE_FORMAT,
            "format_version": CAMERA_TAKE_FORMAT_VERSION,
            "recorded_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "replay_request": dict(self._camera_take_context),
            "replay_summary": {
                "source_kind": str(self._replay.source_kind),
                "frame_count": int(len(self._replay.frames)),
                "first_tick": int(self._replay.frames[0].tick),
                "last_tick": int(self._replay.frames[-1].tick),
            },
            "samples": list(self._camera_take_samples),
        }

    def _start_camera_take_recording(self) -> None:
        if self._camera_take_output_path is None:
            self._set_camera_take_notice("REC unavailable: set --camera-take-output")
            print("[CAMERA TAKE] unavailable: set --camera-take-output to arm recording.")
            return
        self._camera_take_samples = []
        self._camera_take_last_signature = None
        self._camera_take_started_at = time.perf_counter()
        self._camera_take_recording = True
        self._set_camera_take_notice("REC started")
        self._capture_camera_take_sample(frame=self._replay.frames[self._current_frame_index], force=True)
        print(f"[CAMERA TAKE] recording: {self._camera_take_output_path}")

    def _stop_camera_take_recording(self) -> None:
        if not self._camera_take_recording:
            return
        self._capture_camera_take_sample(frame=self._replay.frames[self._current_frame_index], force=True)
        payload = self._build_camera_take_payload()
        output_path = self._camera_take_output_path
        if output_path is None:
            raise ValueError("camera take output path is missing while attempting to save a recording.")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        self._camera_take_recording = False
        self._camera_take_last_signature = None
        duration_seconds = float(payload["samples"][-1]["elapsed_s"])
        self._set_camera_take_notice(
            f"REC saved: {output_path.name} ({len(payload['samples'])} samples)"
        )
        print(
            f"[CAMERA TAKE SAVED] path={output_path} samples={len(payload['samples'])} "
            f"duration_s={duration_seconds:.2f}"
        )

    def toggle_camera_take_recording(self) -> None:
        if self._camera_take_recording:
            self._stop_camera_take_recording()
            return
        self._start_camera_take_recording()

    def _request_exit(self) -> None:
        if self._camera_take_recording:
            print("[CAMERA TAKE] exit requested; saving active recording before shutdown.")
            self._stop_camera_take_recording()
        self.userExit()

    def _render_saved_take_sample(self, sample: dict[str, Any]) -> None:
        frame_index = int(sample["frame_index"])
        if frame_index < 0 or frame_index >= len(self._replay.frames):
            raise ValueError(
                f"camera take sample frame_index {frame_index} is outside replay bounds 0..{len(self._replay.frames) - 1}."
            )
        frame = self._replay.frames[frame_index]
        expected_tick = int(sample["tick"])
        if int(frame.tick) != expected_tick:
            raise ValueError(
                f"camera take sample tick mismatch at frame_index {frame_index}: "
                f"take has {expected_tick}, replay has {int(frame.tick)}."
            )
        viewer_state = sample["viewer"]
        camera_state = sample["camera"]
        position_alpha = max(0.0, min(1.0, float(sample["position_alpha"])))
        pulse_phase = max(0.0, min(1.0, float(sample["pulse_phase"])))
        self._apply_viewer_state_snapshot(viewer_state)
        self._camera_controller.apply_state_snapshot(camera_state)
        self._current_frame_index = frame_index
        if position_alpha > 1e-6 and len(self._replay.frames) > 1:
            if frame_index >= len(self._replay.frames) - 1:
                raise ValueError(
                    "camera take sample requests interpolation past the final replay frame; "
                    f"frame_index={frame_index}, position_alpha={position_alpha}."
                )
            next_frame = self._replay.frames[frame_index + 1]
            self._unit_renderer.sync_frame(frame, pulse_phase=pulse_phase)
            self._unit_renderer.refresh_fire_links(
                frame,
                pulse_phase=pulse_phase,
                next_frame=next_frame,
                position_alpha=position_alpha,
            )
            self._unit_renderer.apply_interpolated_transforms(
                frame,
                next_frame,
                alpha=position_alpha,
            )
            self._unit_renderer._sync_fleet_halos(
                frame,
                tick_offset=position_alpha,
                use_node_positions=True,
            )
            self._unit_renderer.update_view(self.camera)
            self._sync_corner_avatar_cards(frame)
            self._sync_fleet_avatar_overlays()
        else:
            self._render_frame(frame, pulse_phase=pulse_phase)
        self._set_display_timing(position_alpha=position_alpha, pulse_phase=pulse_phase)
        self._refresh_overlay()
        self._refresh_camera_take_overlay()

    def _adjust_playback_speed(self, delta: int) -> None:
        next_index = max(0, min(len(PLAYBACK_FPS_LEVELS) - 1, self._playback_level_index + int(delta)))
        self._playback_level_index = next_index
        self._playback_fps = float(PLAYBACK_FPS_LEVELS[self._playback_level_index])
        self._unit_renderer.set_playback_level_index(self._playback_level_index)
        self._unit_renderer.set_playback_fps(self._playback_fps)
        self._camera_controller.set_playback_level_index(self._playback_level_index)
        self.go_to_frame(self._current_frame_index)

    def cycle_fire_link_mode(self) -> None:
        current_index = FIRE_LINK_MODE_CHOICES.index(self._unit_renderer.fire_link_mode)
        next_index = (current_index + 1) % len(FIRE_LINK_MODE_CHOICES)
        self._unit_renderer.set_fire_link_mode(FIRE_LINK_MODE_CHOICES[next_index])
        self.go_to_frame(self._current_frame_index)

    def cycle_direction_mode(self) -> None:
        current_mode = str(self._replay.metadata.get("vector_display_mode", "posture")).strip().lower()
        if current_mode not in PRIMARY_DIRECTION_MODE_CYCLE:
            next_mode = PRIMARY_DIRECTION_MODE_CYCLE[0]
        else:
            next_index = (PRIMARY_DIRECTION_MODE_CYCLE.index(current_mode) + 1) % len(PRIMARY_DIRECTION_MODE_CYCLE)
            next_mode = PRIMARY_DIRECTION_MODE_CYCLE[next_index]
        current_frame_index = int(self._current_frame_index)
        current_playing = bool(self._playing)
        current_position_alpha = float(self._current_display_position_alpha)
        current_pulse_phase = float(self._current_display_pulse_phase)
        reloaded_replay = self._direction_mode_replay_cache.get(next_mode)
        if reloaded_replay is None:
            raise ValueError(f"direction-mode cache missing required mode {next_mode!r}.")
        self._replay = reloaded_replay
        self._unit_renderer._replay = reloaded_replay
        self._current_frame_index = max(0, min(current_frame_index, len(self._replay.frames) - 1))
        self._playing = current_playing
        self._set_display_timing(position_alpha=current_position_alpha, pulse_phase=current_pulse_phase)
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

    def _jump_to_boundary_frame(self, frame_index: int) -> None:
        self._playing = False
        self._camera_controller.reset()
        self.go_to_frame(frame_index)

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

    def _render_frame(self, frame: ViewerFrame, *, pulse_phase: float = 0.0) -> None:
        self._set_display_timing(position_alpha=0.0, pulse_phase=pulse_phase)
        self._unit_renderer.sync_frame(frame, pulse_phase=float(pulse_phase))
        self._unit_renderer.update_view(self.camera)
        self._sync_corner_avatar_cards(frame)
        self._sync_fleet_avatar_overlays()

    def _build_avatar_overlays(self) -> None:
        raw_avatars = self._replay.metadata.get("fleet_avatars", {})
        if not isinstance(raw_avatars, dict):
            return
        self._build_corner_avatar_portraits(raw_avatars)
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
            avatar_path = _resolve_avatar_image_path(avatar_id, preferred_size="s")
            if avatar_path is None:
                continue
            texture = self.loader.loadTexture(Filename.fromOsSpecific(str(avatar_path)))
            if texture is None:
                continue
            fleet_color = self._replay.fleet_colors.get(str(fleet_id), "#ffffff")
            base_bin = 40 + (int(stack_index) * 10)
            highlight_color = _hex_to_rgba(fleet_color, alpha=FLEET_AVATAR_HIGHLIGHT_ALPHA)
            highlight_bars = {
                "top": DirectFrame(
                    parent=self.aspect2d,
                    frameSize=(-highlight_half_width, highlight_half_width, border_half_height, highlight_half_height),
                    frameColor=highlight_color,
                ),
                "bottom": DirectFrame(
                    parent=self.aspect2d,
                    frameSize=(-highlight_half_width, highlight_half_width, -highlight_half_height, -border_half_height),
                    frameColor=highlight_color,
                ),
                "left": DirectFrame(
                    parent=self.aspect2d,
                    frameSize=(-highlight_half_width, -border_half_width, -border_half_height, border_half_height),
                    frameColor=highlight_color,
                ),
                "right": DirectFrame(
                    parent=self.aspect2d,
                    frameSize=(border_half_width, highlight_half_width, -border_half_height, border_half_height),
                    frameColor=highlight_color,
                ),
            }
            for highlight_bar in highlight_bars.values():
                highlight_bar.setTransparency(TransparencyAttrib.MAlpha)
                highlight_bar.setBin("fixed", base_bin)
                highlight_bar.setDepthTest(False)
                highlight_bar.setDepthWrite(False)
                highlight_bar.hide()
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
                "highlight_top": highlight_bars["top"],
                "highlight_bottom": highlight_bars["bottom"],
                "highlight_left": highlight_bars["left"],
                "highlight_right": highlight_bars["right"],
                "matte": matte,
                "border_top": border_bars["top"],
                "border_bottom": border_bars["bottom"],
                "border_left": border_bars["left"],
                "border_right": border_bars["right"],
                "image": node,
            }

    def _build_corner_avatar_portraits(self, raw_avatars: dict[object, object]) -> None:
        # Fixed corner avatar blocks stay visible regardless of the follow-avatar toggle.
        raw_full_names = self._replay.metadata.get("fleet_full_names", {})
        if not isinstance(raw_full_names, dict):
            raw_full_names = {}
        corner_specs = {
            "A": (self.a2dTopLeft, CORNER_AVATAR_INSET_X, -CORNER_AVATAR_INSET_Z),
            "B": (self.a2dTopRight, -CORNER_AVATAR_INSET_X, -CORNER_AVATAR_INSET_Z),
        }
        portrait_half_height = CORNER_AVATAR_HEIGHT
        portrait_half_width = CORNER_AVATAR_HEIGHT * CORNER_AVATAR_ASPECT_RATIO
        border_half_height = portrait_half_height + CORNER_AVATAR_BORDER_PAD
        border_half_width = portrait_half_width + CORNER_AVATAR_BORDER_PAD
        for fleet_id, (parent, pos_x, pos_z) in corner_specs.items():
            avatar_id = raw_avatars.get(fleet_id)
            if avatar_id is None:
                continue
            avatar_path = _resolve_avatar_image_path(avatar_id, preferred_size="m")
            if avatar_path is None:
                continue
            texture = self.loader.loadTexture(Filename.fromOsSpecific(str(avatar_path)))
            if texture is None:
                continue
            fleet_color = self._replay.fleet_colors.get(str(fleet_id), "#ffffff")
            border_color = _hex_to_rgba(fleet_color, alpha=FLEET_AVATAR_BORDER_ALPHA)
            border_bars = {
                "top": DirectFrame(
                    parent=parent,
                    frameSize=(-border_half_width, border_half_width, portrait_half_height, border_half_height),
                    frameColor=border_color,
                    pos=(pos_x, 0.0, pos_z),
                ),
                "bottom": DirectFrame(
                    parent=parent,
                    frameSize=(-border_half_width, border_half_width, -border_half_height, -portrait_half_height),
                    frameColor=border_color,
                    pos=(pos_x, 0.0, pos_z),
                ),
                "left": DirectFrame(
                    parent=parent,
                    frameSize=(-border_half_width, -portrait_half_width, -portrait_half_height, portrait_half_height),
                    frameColor=border_color,
                    pos=(pos_x, 0.0, pos_z),
                ),
                "right": DirectFrame(
                    parent=parent,
                    frameSize=(portrait_half_width, border_half_width, -portrait_half_height, portrait_half_height),
                    frameColor=border_color,
                    pos=(pos_x, 0.0, pos_z),
                ),
            }
            for border_bar in border_bars.values():
                border_bar.setTransparency(TransparencyAttrib.MAlpha)
                border_bar.setBin("fixed", 75)
                border_bar.setDepthTest(False)
                border_bar.setDepthWrite(False)
            node = OnscreenImage(
                image=texture,
                parent=parent,
                pos=(pos_x, 0.0, pos_z),
                scale=(portrait_half_width, 1.0, portrait_half_height),
            )
            node.setTransparency(TransparencyAttrib.MAlpha)
            node.setBin("fixed", 76)
            node.setDepthTest(False)
            node.setDepthWrite(False)
            text_align = TextNode.ALeft if fleet_id == "A" else TextNode.ARight
            outer_edge_x = (
                pos_x - border_half_width - CORNER_AVATAR_ALIGNMENT_OVERSHOOT
                if fleet_id == "A"
                else pos_x + border_half_width + CORNER_AVATAR_ALIGNMENT_OVERSHOOT
            )
            text_kwargs = {}
            if self._ui_font is not None:
                text_kwargs["font"] = self._ui_font
            size_text = OnscreenText(
                text="Fleet Size: 0",
                parent=parent,
                pos=(
                    outer_edge_x,
                    pos_z + portrait_half_height + CORNER_AVATAR_BAR_OFFSET + (CORNER_AVATAR_BAR_HEIGHT * 0.5) + CORNER_AVATAR_TEXT_GAP,
                ),
                scale=CORNER_AVATAR_TEXT_SCALE,
                align=text_align,
                fg=CORNER_AVATAR_TEXT_COLOR,
                mayChange=True,
                **text_kwargs,
            )
            size_text.setBin("fixed", 77)
            size_text.setDepthTest(False)
            size_text.setDepthWrite(False)
            bar_bg = DirectFrame(
                parent=parent,
                frameSize=(
                    (0.0, CORNER_AVATAR_BAR_WIDTH, -CORNER_AVATAR_BAR_HEIGHT * 0.5, CORNER_AVATAR_BAR_HEIGHT * 0.5)
                    if fleet_id == "A"
                    else (-CORNER_AVATAR_BAR_WIDTH, 0.0, -CORNER_AVATAR_BAR_HEIGHT * 0.5, CORNER_AVATAR_BAR_HEIGHT * 0.5)
                ),
                frameColor=CORNER_AVATAR_BAR_BG,
                pos=(outer_edge_x, 0.0, pos_z + portrait_half_height + CORNER_AVATAR_BAR_OFFSET),
            )
            bar_bg.setTransparency(TransparencyAttrib.MAlpha)
            bar_bg.setBin("fixed", 77)
            bar_bg.setDepthTest(False)
            bar_bg.setDepthWrite(False)
            bar_fill = DirectFrame(
                parent=bar_bg,
                frameSize=(
                    (0.0, CORNER_AVATAR_BAR_WIDTH, -CORNER_AVATAR_BAR_HEIGHT * 0.5, CORNER_AVATAR_BAR_HEIGHT * 0.5)
                    if fleet_id == "A"
                    else (-CORNER_AVATAR_BAR_WIDTH, 0.0, -CORNER_AVATAR_BAR_HEIGHT * 0.5, CORNER_AVATAR_BAR_HEIGHT * 0.5)
                ),
                frameColor=CORNER_AVATAR_BAR_FILL,
            )
            bar_fill.setTransparency(TransparencyAttrib.MAlpha)
            bar_fill.setBin("fixed", 78)
            bar_fill.setDepthTest(False)
            bar_fill.setDepthWrite(False)
            full_name = str(raw_full_names.get(fleet_id, self._replay.fleet_labels.get(fleet_id, fleet_id)))
            name_text = OnscreenText(
                text=full_name,
                parent=parent,
                pos=(outer_edge_x, pos_z - portrait_half_height - CORNER_AVATAR_NAME_OFFSET),
                scale=CORNER_AVATAR_NAME_SCALE,
                align=text_align,
                fg=CORNER_AVATAR_TEXT_COLOR,
                **text_kwargs,
            )
            name_text.setBin("fixed", 77)
            name_text.setDepthTest(False)
            name_text.setDepthWrite(False)
            self._corner_avatar_nodes[str(fleet_id)] = {
                "border_top": border_bars["top"],
                "border_bottom": border_bars["bottom"],
                "border_left": border_bars["left"],
                "border_right": border_bars["right"],
                "image": node,
                "size_text": size_text,
                "hp_bar_bg": bar_bg,
                "hp_bar_fill": bar_fill,
                "name_text": name_text,
            }

    def _sync_corner_avatar_cards(self, frame: ViewerFrame) -> None:
        fleet_hp: dict[str, float] = {}
        for unit in frame.units:
            fleet_id = str(unit.fleet_id)
            fleet_hp[fleet_id] = fleet_hp.get(fleet_id, 0.0) + max(0.0, float(unit.hit_points))
        for fleet_id, nodes in self._corner_avatar_nodes.items():
            hp_now = float(fleet_hp.get(fleet_id, 0.0))
            hp_initial = float(self._fleet_initial_total_hp.get(fleet_id, 0.0))
            hp_ratio = 0.0 if hp_initial <= 1e-9 else max(0.0, min(1.0, hp_now / hp_initial))
            size_text = nodes.get("size_text")
            if hasattr(size_text, "setText"):
                size_text.setText(f"Fleet Size: {max(0, int(math.ceil(hp_now)))}")
            bar_fill = nodes.get("hp_bar_fill")
            if bar_fill is not None:
                fill_width = CORNER_AVATAR_BAR_WIDTH * hp_ratio
                if fleet_id == "B":
                    left = -fill_width
                    right = 0.0
                else:
                    left = 0.0
                    right = fill_width
                bar_fill["frameSize"] = (left, right, -CORNER_AVATAR_BAR_HEIGHT * 0.5, CORNER_AVATAR_BAR_HEIGHT * 0.5)

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
                for node in nodes.values():
                    node.hide()
                continue
            aspect_ratio = float(self.getAspectRatio())
            target_x = max(-(aspect_ratio - 0.08), min(aspect_ratio - 0.08, float(projected_anchor[0])))
            target_z = max(-0.90, min(0.92, float(projected_anchor[1])))
            target_positions[fleet_id] = (target_x, target_z)
        adjusted_target_positions = self._resolve_avatar_layout_positions(target_positions)
        for fleet_id, nodes in self._fleet_avatar_nodes.items():
            final_position = adjusted_target_positions.get(fleet_id)
            if final_position is None:
                for node in nodes.values():
                    node.hide()
                continue
            display_x, display_z = final_position
            for node in nodes.values():
                node.setPos(display_x, 0.0, display_z)
                node.show()

    def _smoothing_active(self) -> bool:
        return bool(self._smoothing_enabled and self._playing and self._playback_fps <= LOW_SPEED_SMOOTHING_MAX_FPS and len(self._replay.frames) > 1)

    def _current_and_next_frames(self) -> tuple[ViewerFrame, ViewerFrame]:
        current_frame = self._replay.frames[self._current_frame_index]
        next_index = self._current_frame_index + 1
        if next_index >= len(self._replay.frames):
            next_index = 0
        return (current_frame, self._replay.frames[next_index])

    def go_to_frame(self, frame_index: int) -> None:
        self._current_frame_index = max(0, min(int(frame_index), len(self._replay.frames) - 1))
        frame = self._replay.frames[self._current_frame_index]
        if not self._playing:
            self._camera_controller.sync_tracked_frame(frame, smooth=False)
        self._render_frame(frame, pulse_phase=0.0)
        self._refresh_overlay()

    @staticmethod
    def _compute_hud_block_y(*, text_node: OnscreenText, line_count: int) -> float:
        effective_lines = max(1, int(line_count))
        line_height = 1.0
        panda_text_node = getattr(text_node, "textNode", None)
        if panda_text_node is not None:
            try:
                line_height = float(panda_text_node.getLineHeight())
            except Exception:
                line_height = 1.0
        return float(HUD_BOTTOM_INSET + ((effective_lines - 1) * line_height * HUD_TEXT_SCALE))

    def _align_hud_block_to_bottom(self, text_node: OnscreenText, *, line_count: int, side: str) -> None:
        pos_x = -HUD_SIDE_INSET if str(side).strip().lower() == "right" else HUD_SIDE_INSET
        text_node.setPos(pos_x, self._compute_hud_block_y(text_node=text_node, line_count=line_count))

    def _refresh_overlay(self) -> None:
        if not self._hud_enabled:
            return
        frame = self._replay.frames[self._current_frame_index]
        counts_text = _count_units_by_fleet(self._replay, self._current_frame_index)
        playback_label = "playing" if self._playing else "paused"
        vector_display_mode = self._replay.metadata.get("vector_display_mode", "posture")
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
        fleet_speeds: dict[str, float] = {}
        if self._current_frame_index > 0:
            previous_frame = self._replay.frames[self._current_frame_index - 1]
            previous_fleet_centroids: dict[str, tuple[float, float, int]] = {}
            for unit in previous_frame.units:
                sum_x, sum_y, count = previous_fleet_centroids.get(unit.fleet_id, (0.0, 0.0, 0))
                previous_fleet_centroids[unit.fleet_id] = (
                    float(sum_x) + float(unit.x),
                    float(sum_y) + float(unit.y),
                    int(count) + 1,
                )
            for fleet_id in sorted(fleet_centroids):
                current_sum_x, current_sum_y, current_count = fleet_centroids[fleet_id]
                previous_entry = previous_fleet_centroids.get(fleet_id)
                if current_count <= 0 or previous_entry is None or int(previous_entry[2]) <= 0:
                    fleet_speeds[fleet_id] = 0.0
                    continue
                current_centroid_x = float(current_sum_x) / float(current_count)
                current_centroid_y = float(current_sum_y) / float(current_count)
                previous_centroid_x = float(previous_entry[0]) / float(previous_entry[2])
                previous_centroid_y = float(previous_entry[1]) / float(previous_entry[2])
                delta_x = current_centroid_x - previous_centroid_x
                delta_y = current_centroid_y - previous_centroid_y
                fleet_speeds[fleet_id] = math.sqrt((delta_x * delta_x) + (delta_y * delta_y))
        runtime_debug_frames = self._replay.metadata.get("runtime_debug_frames")
        runtime_debug = {}
        if (
            isinstance(runtime_debug_frames, (list, tuple))
            and 0 <= self._current_frame_index < len(runtime_debug_frames)
            and isinstance(runtime_debug_frames[self._current_frame_index], dict)
        ):
            runtime_debug = runtime_debug_frames[self._current_frame_index]
        focus_indicators = runtime_debug.get("focus_indicators", {}) if isinstance(runtime_debug, dict) else {}
        kinetics_parts = []
        fire_eff_parts = []
        for fleet_id in sorted(fleet_centroids):
            hold_value = float("nan")
            fire_eff_value = float("nan")
            if isinstance(focus_indicators, dict):
                row = focus_indicators.get(str(fleet_id), {})
                if isinstance(row, dict):
                    hold_value = float(row.get("hold_weight", float("nan")))
                    fire_eff_value = float(row.get("fire_eff", float("nan")))
            hold_text = f"{hold_value:.2f}" if math.isfinite(hold_value) else "--"
            fire_eff_text = f"{fire_eff_value:.2f}" if math.isfinite(fire_eff_value) else "--"
            kinetics_parts.append(
                f"{fleet_id}: v={fleet_speeds.get(fleet_id, 0.0):.2f} h={hold_text}"
            )
            fire_eff_parts.append(f"{fleet_id}: e={fire_eff_text}")
        status_lines.append(
            f"Kinetics: {' | '.join(kinetics_parts)}" if kinetics_parts else "Kinetics: n/a"
        )
        status_lines.append(
            f"FireEff: {' | '.join(fire_eff_parts)}" if fire_eff_parts else "FireEff: n/a"
        )
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
        if isinstance(focus_indicators, dict) and focus_indicators:
            for fleet_id in sorted(focus_indicators):
                row = focus_indicators.get(fleet_id, {})
                if not isinstance(row, dict):
                    continue
                if any(
                    math.isfinite(float(row.get(key, float("nan"))))
                    for key in (
                        "centroid_distance",
                        "front_strip_gap",
                    )
                ):
                    status_lines.append(
                        "focus "
                        f"{fleet_id}@:"
                        f" strip_gap={float(row.get('front_strip_gap', float('nan'))):.2f}"
                    )
                if any(
                    math.isfinite(float(row.get(key, float("nan"))))
                    for key in (
                        "engagement_geometry_active",
                        "front_reorientation_weight",
                        "front_axis_delta_deg",
                    )
                ):
                    status_lines.append(
                        "focus "
                        f"{fleet_id}+: "
                        f"eng_act={float(row.get('engagement_geometry_active', float('nan'))):.2f}  "
                        f"front_rw={float(row.get('front_reorientation_weight', float('nan'))):.2f}  "
                        f"fire_da={float(row.get('front_axis_delta_deg', float('nan'))):.0f}\u00b0"
                    )
        self._status_text.setText("\n".join(status_lines))
        self._align_hud_block_to_bottom(self._status_text, line_count=len(status_lines), side="left")
        control_lines = [
            "Space play/pause  N/B step/hold  K rec",
            "[/ ] speed gear  V fire-links  D dir_mode  M smooth",
            "P follow avatars  Tab HUD  LDrag pan  RDrag orbit",
            "Wheel zoom  Home/End reset+jump  `/~ reset  1/2 track fleet  Esc quit",
        ]
        self._control_text.setText("\n".join(control_lines))
        self._align_hud_block_to_bottom(self._control_text, line_count=len(control_lines), side="right")

    def _tick(self, task):
        dt = ClockObject.getGlobalClock().getDt()
        if self._camera_take_notice_seconds_remaining > 0.0:
            self._camera_take_notice_seconds_remaining = max(0.0, self._camera_take_notice_seconds_remaining - dt)
            if self._camera_take_notice_seconds_remaining <= 1e-9:
                self._camera_take_notice_message = ""
                self._refresh_camera_take_overlay()
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
            current_frame = self._replay.frames[self._current_frame_index]
            if self._smoothing_active():
                smoothing_alpha = self._accumulator / frame_period
                if smoothing_alpha > 1e-6:
                    current_frame, next_frame = self._current_and_next_frames()
                    self._camera_controller.sync_tracked_frames(
                        current_frame,
                        next_frame,
                        alpha=smoothing_alpha,
                        smooth=False,
                    )
                    self._unit_renderer.apply_interpolated_transforms(
                        current_frame,
                        next_frame,
                        alpha=smoothing_alpha,
                    )
                    self._unit_renderer._sync_fleet_halos(
                        current_frame,
                        tick_offset=smoothing_alpha,
                        use_node_positions=True,
                    )
                    if self._unit_renderer.fire_link_mode == "enabled":
                        self._unit_renderer.refresh_fire_links(
                            current_frame,
                            pulse_phase=smoothing_alpha,
                            next_frame=next_frame,
                            position_alpha=smoothing_alpha,
                        )
                    self._set_display_timing(
                        position_alpha=smoothing_alpha,
                        pulse_phase=smoothing_alpha if self._unit_renderer.fire_link_mode == "enabled" else 0.0,
                    )
                    self._unit_renderer.update_view(self.camera)
                    self._sync_corner_avatar_cards(current_frame)
                    self._sync_fleet_avatar_overlays()
                    self._capture_camera_take_sample(frame=current_frame)
                    return task.cont
            elif self._unit_renderer.fire_link_mode == "enabled":
                self._camera_controller.sync_tracked_frame(current_frame, smooth=True)
                self._unit_renderer.refresh_fire_links(
                    current_frame,
                    pulse_phase=(self._accumulator / frame_period) if frame_period > 1e-9 else 0.0,
                )
                self._set_display_timing(
                    position_alpha=0.0,
                    pulse_phase=(self._accumulator / frame_period) if frame_period > 1e-9 else 0.0,
                )
            else:
                self._camera_controller.sync_tracked_frame(current_frame, smooth=True)
                self._set_display_timing(position_alpha=0.0, pulse_phase=0.0)
        else:
            current_frame = self._replay.frames[self._current_frame_index]
            self._set_display_timing(position_alpha=0.0, pulse_phase=0.0)
        self._unit_renderer.update_view(self.camera)
        self._sync_corner_avatar_cards(current_frame)
        self._sync_fleet_avatar_overlays()
        self._capture_camera_take_sample(frame=current_frame)
        return task.cont


def _configure_window(*, title: str, width: int, height: int, offscreen: bool = False) -> None:
    loadPrcFileData("", "notify-level-display error")
    loadPrcFileData("", "notify-level-windisplay error")
    if offscreen:
        loadPrcFileData("", "window-type offscreen")
    loadPrcFileData("", f"window-title {title}")
    loadPrcFileData("", f"win-size {int(width)} {int(height)}")


def export_camera_take_video(
    *,
    camera_take_path_text: str,
    output_mp4_path_text: str | None,
    export_fps: int,
    ffmpeg_exe_path_text: str,
    window_width: int,
    window_height: int,
    offscreen: bool,
) -> None:
    take_path, take_payload = _load_camera_take_payload(str(camera_take_path_text))
    replay_request = dict(take_payload["replay_request"])
    if output_mp4_path_text is None:
        output_path = _resolve_default_video_export_path(take_path=take_path)
    else:
        output_path = _resolve_output_path(str(output_mp4_path_text))
        if output_path.suffix.lower() != ".mp4":
            raise ValueError(f"output mp4 path must point to a .mp4 file, got {output_path}.")
    ffmpeg_path = _resolve_explicit_ffmpeg_exe(str(ffmpeg_exe_path_text))
    export_fps = int(export_fps)
    if export_fps < 1:
        raise ValueError(f"export_fps must be >= 1, got {export_fps}.")
    if int(window_width) < 1 or int(window_height) < 1:
        raise ValueError(f"export window size must be positive, got {window_width}x{window_height}.")

    _configure_window(
        title=f"{WINDOW_TITLE} Export",
        width=int(window_width),
        height=int(window_height),
        offscreen=bool(offscreen),
    )
    print(f"[CAMERA TAKE EXPORT] source={take_path}")
    replay = load_viewer_replay(
        source=str(replay_request["source"]),
        max_steps=int(replay_request["max_steps"]),
        frame_stride=int(replay_request["frame_stride"]),
        direction_mode=str(replay_request["direction_mode"]),
    )
    replay_summary = take_payload.get("replay_summary", {})
    if isinstance(replay_summary, dict):
        expected_frame_count = int(replay_summary.get("frame_count", len(replay.frames)))
        expected_first_tick = int(replay_summary.get("first_tick", replay.frames[0].tick))
        expected_last_tick = int(replay_summary.get("last_tick", replay.frames[-1].tick))
        if len(replay.frames) != expected_frame_count:
            raise ValueError(
                f"camera take replay frame_count mismatch: take expects {expected_frame_count}, replay produced {len(replay.frames)}."
            )
        if int(replay.frames[0].tick) != expected_first_tick or int(replay.frames[-1].tick) != expected_last_tick:
            raise ValueError(
                "camera take replay boundary ticks do not match the saved take; "
                f"expected first/last={expected_first_tick}/{expected_last_tick}, "
                f"got {int(replay.frames[0].tick)}/{int(replay.frames[-1].tick)}."
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    app = FleetViewerApp(
        replay,
        playback_fps=float(replay_request["playback_fps"]),
        fire_link_mode=str(replay_request["fire_link_mode"]),
    )
    app.taskMgr.remove("fleet_viewer_tick")
    app._camera_take_indicator_text.hide()
    app._camera_take_notice_text.hide()
    render_texture = Texture()
    render_texture.setKeepRamImage(True)
    app.win.addRenderTexture(render_texture, GraphicsOutput.RTMCopyRam)

    samples = _trim_invalid_terminal_camera_take_samples(
        take_payload["samples"],
        replay_frame_count=len(replay.frames),
    )
    total_duration_seconds = float(samples[-1]["elapsed_s"])
    total_output_frames = max(1, int(math.ceil(total_duration_seconds * float(export_fps))) + 1)
    ffmpeg_process = subprocess.Popen(
        [
            ffmpeg_path,
            "-y",
            "-hide_banner",
            "-loglevel",
            "error",
            "-nostats",
            "-f",
            "rawvideo",
            "-pixel_format",
            "rgb24",
            "-video_size",
            f"{int(window_width)}x{int(window_height)}",
            "-framerate",
            str(export_fps),
            "-i",
            "-",
            "-vf",
            "vflip",
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            str(output_path),
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        bufsize=0,
    )
    print(f"[CAMERA TAKE EXPORT] output={output_path} fps={export_fps} frames={total_output_frames}")
    try:
        sample_cursor = 0
        next_progress_percent = 10
        for output_frame_index in range(total_output_frames):
            target_time = float(output_frame_index) / float(export_fps)
            while (
                sample_cursor + 1 < len(samples)
                and float(samples[sample_cursor + 1]["elapsed_s"]) <= (target_time + 1e-9)
            ):
                sample_cursor += 1
            sample = samples[sample_cursor]
            app._render_saved_take_sample(sample)
            app.graphicsEngine.renderFrame()
            if not render_texture.hasRamImage():
                raise RuntimeError(
                    f"Panda3D render texture has no RAM image for export frame {output_frame_index}."
                )
            if int(render_texture.getXSize()) != int(window_width) or int(render_texture.getYSize()) != int(window_height):
                raise RuntimeError(
                    "Panda3D render texture size does not match requested export size; "
                    f"requested={int(window_width)}x{int(window_height)}, "
                    f"actual={int(render_texture.getXSize())}x{int(render_texture.getYSize())}."
                )
            frame_bytes = bytes(render_texture.getRamImageAs("RGB"))
            expected_frame_bytes = int(window_width) * int(window_height) * 3
            if len(frame_bytes) != expected_frame_bytes:
                raise RuntimeError(
                    f"Panda3D render texture returned {len(frame_bytes)} bytes for export frame {output_frame_index}; "
                    f"expected {expected_frame_bytes}."
                )
            ffmpeg_return_code = ffmpeg_process.poll()
            if ffmpeg_return_code is not None:
                ffmpeg_stderr_text = ""
                if ffmpeg_process.stderr is not None:
                    ffmpeg_stderr_text = ffmpeg_process.stderr.read().decode("utf-8", errors="replace").strip()
                raise RuntimeError(
                    f"ffmpeg exited early with code {ffmpeg_return_code}. stderr={ffmpeg_stderr_text!r}."
                )
            if ffmpeg_process.stdin is None:
                raise RuntimeError("ffmpeg stdin is unavailable during camera take export.")
            written_byte_count = ffmpeg_process.stdin.write(frame_bytes)
            if written_byte_count != len(frame_bytes):
                raise RuntimeError(
                    f"ffmpeg stdin wrote {written_byte_count} bytes for export frame {output_frame_index}; "
                    f"expected {len(frame_bytes)}."
                )
            completed_percent = int(((output_frame_index + 1) * 100) / total_output_frames)
            while completed_percent >= next_progress_percent and next_progress_percent <= 100:
                print(f"[CAMERA TAKE EXPORT] progress={next_progress_percent}%")
                next_progress_percent += 10
        if ffmpeg_process.stdin is not None:
            ffmpeg_process.stdin.close()
        ffmpeg_return_code = ffmpeg_process.wait()
        ffmpeg_stderr_text = ""
        if ffmpeg_process.stderr is not None:
            ffmpeg_stderr_text = ffmpeg_process.stderr.read().decode("utf-8", errors="replace").strip()
        if ffmpeg_return_code != 0:
            raise RuntimeError(
                f"ffmpeg failed with exit code {ffmpeg_return_code}. stderr={ffmpeg_stderr_text!r}."
            )
    except Exception:
        if ffmpeg_process.stdin is not None:
            try:
                ffmpeg_process.stdin.close()
            except Exception:
                pass
        if ffmpeg_process.poll() is None:
            ffmpeg_process.terminate()
            try:
                ffmpeg_process.wait(timeout=10.0)
            except subprocess.TimeoutExpired:
                ffmpeg_process.kill()
                ffmpeg_process.wait()
        try:
            app.destroy()
        except Exception:
            pass
        raise
    try:
        app.destroy()
    except Exception:
        pass
    print(f"[CAMERA TAKE EXPORT COMPLETE] {output_path}")


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=WINDOW_TITLE)
    parser.add_argument(
        "--source",
        choices=VIEWER_SOURCE_CHOICES,
        default=VIEWER_SOURCE_AUTO,
        help=(
            "Viewer replay source. 'auto' follows the current layered fixture.active_mode when it is "
            "neutral; otherwise it uses the active battle path."
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
        default="posture",
        help=(
            "Viewer-local direction readout mode. Default is 'posture'; 'settings' preserves "
            "the current layered 2D vector_display_mode; 'movement' shows smoothed travel "
            "direction and 'posture' shows a bounded maneuver-posture read."
        ),
    )
    parser.add_argument(
        "--playback-fps",
        type=float,
        default=PLAYBACK_FPS_LEVELS[DEFAULT_PLAYBACK_LEVEL_INDEX],
        help="Fixed playback speed level. Supported values: 2, 4, 6, 10, 20.",
    )
    parser.add_argument("--window-width", type=int, default=1440)
    parser.add_argument("--window-height", type=int, default=900)
    parser.add_argument(
        "--fire-link-mode",
        choices=FIRE_LINK_MODE_CHOICES,
        default="enabled",
        help="Viewer-local fire-link display mode. Only 'enabled' and 'disabled' are supported.",
    )
    parser.add_argument(
        "--camera-take-output",
        type=str,
        default=None,
        help="Arm K-key camera-take recording and save the take as a JSON file when recording stops.",
    )
    args = parser.parse_args(argv)
    return args


def main(argv: Sequence[str] | None = None) -> None:
    args = _parse_args(argv)

    if args.camera_take_output is None:
        camera_take_output_path = _resolve_default_camera_take_output_path()
    else:
        camera_take_output_path = _resolve_output_path(str(args.camera_take_output))
        if camera_take_output_path.suffix.lower() != ".json":
            raise ValueError(f"--camera-take-output must point to a .json file, got {camera_take_output_path}.")

    _configure_window(
        title=WINDOW_TITLE,
        width=int(args.window_width),
        height=int(args.window_height),
    )
    matchup_text, map_text = _preview_launch_setup(str(args.source))
    print(matchup_text)
    print(map_text)
    run_started_at = time.perf_counter()
    print("[RUN START]")
    replay = load_viewer_replay(
        source=str(args.source),
        max_steps=args.steps,
        frame_stride=int(args.frame_stride),
        direction_mode=str(args.direction_mode),
    )
    run_elapsed = time.perf_counter() - run_started_at
    print(_format_launch_result(replay))
    print(f"[RUN COMPLETE] time={run_elapsed:.1f}s")
    camera_take_context = None
    if camera_take_output_path is not None:
        camera_take_context = _build_camera_take_context(
            replay,
            playback_fps=float(args.playback_fps),
            fire_link_mode=str(args.fire_link_mode),
            window_width=int(args.window_width),
            window_height=int(args.window_height),
        )
        print(f"[CAMERA TAKE ARMED] key={CAMERA_TAKE_RECORD_KEY.upper()} output={camera_take_output_path}")
    animation_started_at = time.perf_counter()
    app = FleetViewerApp(
        replay,
        playback_fps=float(args.playback_fps),
        fire_link_mode=str(args.fire_link_mode),
        camera_take_output_path=camera_take_output_path,
        camera_take_context=camera_take_context,
    )
    animation_elapsed = time.perf_counter() - animation_started_at
    print(f"[ANIMATION INITIALIZED] time={animation_elapsed:.1f}s")
    app.run()


if __name__ == "__main__":
    main()
