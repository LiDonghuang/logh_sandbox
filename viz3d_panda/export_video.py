from __future__ import annotations

import argparse
from pathlib import Path
from typing import Sequence

from viz3d_panda.app import DEFAULT_CAMERA_TAKE_OUTPUT_PATH, export_camera_take_video


DEFAULT_EXPORT_FFMPEG_EXE = Path(
    ".venv_check/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
)
EXPORT_PRESET_SETTINGS: dict[str, tuple[int, int, int]] = {
    "low": (5, 800, 600),
    "standard": (10, 1024, 768),
    "high": (30, 1920, 1080),
}
DEFAULT_EXPORT_PRESET = "standard"


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="LOGH dev_v2.0 Panda3D camera-take offline export")
    parser.add_argument(
        "--preset",
        choices=tuple(EXPORT_PRESET_SETTINGS.keys()),
        default=DEFAULT_EXPORT_PRESET,
        help="Named offline export preset.",
    )
    parser.add_argument(
        "--camera-take",
        type=str,
        default=str(DEFAULT_CAMERA_TAKE_OUTPUT_PATH),
        help="Camera-take JSON path. Default uses the standard analysis/exports/videos location.",
    )
    parser.add_argument(
        "--output-mp4",
        type=str,
        default=None,
        help="Optional mp4 output path. When omitted, exports to analysis/exports/videos/<take_stem>.mp4.",
    )
    parser.add_argument(
        "--ffmpeg-exe",
        type=str,
        default=str(DEFAULT_EXPORT_FFMPEG_EXE),
        help="Explicit ffmpeg executable path. No fallback is used.",
    )
    parser.add_argument(
        "--export-fps",
        type=int,
        default=None,
        help="Offline export frame rate. When omitted, uses the selected preset.",
    )
    parser.add_argument(
        "--window-width",
        type=int,
        default=None,
        help="Offscreen export width in pixels. When omitted, uses the selected preset.",
    )
    parser.add_argument(
        "--window-height",
        type=int,
        default=None,
        help="Offscreen export height in pixels. When omitted, uses the selected preset.",
    )
    args = parser.parse_args(argv)
    if args.export_fps is not None and int(args.export_fps) < 1:
        parser.error("--export-fps must be >= 1.")
    if args.window_width is not None and int(args.window_width) < 1:
        parser.error("--window-width must be >= 1.")
    if args.window_height is not None and int(args.window_height) < 1:
        parser.error("--window-height must be >= 1.")
    if (
        args.window_width is not None
        and args.window_height is not None
        and (int(args.window_width) < 1 or int(args.window_height) < 1)
    ):
        parser.error("--window-width and --window-height must both be >= 1.")
    return args


def main(argv: Sequence[str] | None = None) -> None:
    args = _parse_args(argv)
    preset_fps, preset_width, preset_height = EXPORT_PRESET_SETTINGS[str(args.preset)]
    export_camera_take_video(
        camera_take_path_text=str(args.camera_take),
        output_mp4_path_text=args.output_mp4,
        export_fps=int(args.export_fps) if args.export_fps is not None else int(preset_fps),
        ffmpeg_exe_path_text=str(args.ffmpeg_exe),
        window_width=int(args.window_width) if args.window_width is not None else int(preset_width),
        window_height=int(args.window_height) if args.window_height is not None else int(preset_height),
        offscreen=True,
    )


if __name__ == "__main__":
    main()
