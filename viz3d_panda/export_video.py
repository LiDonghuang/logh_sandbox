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
    for option_name in ("export_fps", "window_width", "window_height"):
        option_value = getattr(args, option_name)
        if option_value is not None and int(option_value) < 1:
            parser.error(f"--{option_name.replace('_', '-')} must be >= 1.")
    return args


def main(argv: Sequence[str] | None = None) -> None:
    args = _parse_args(argv)
    preset_fps, preset_width, preset_height = EXPORT_PRESET_SETTINGS[str(args.preset)]
    export_fps = int(preset_fps if args.export_fps is None else args.export_fps)
    window_width = int(preset_width if args.window_width is None else args.window_width)
    window_height = int(preset_height if args.window_height is None else args.window_height)
    export_camera_take_video(
        camera_take_path_text=str(args.camera_take),
        output_mp4_path_text=args.output_mp4,
        export_fps=export_fps,
        ffmpeg_exe_path_text=str(args.ffmpeg_exe),
        window_width=window_width,
        window_height=window_height,
        offscreen=True,
    )


if __name__ == "__main__":
    main()
