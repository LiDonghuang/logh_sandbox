from __future__ import annotations

import random
from pathlib import Path

from panda3d.core import (
    AmbientLight,
    CardMaker,
    DirectionalLight,
    Filename,
    LineSegs,
    NodePath,
    Texture,
    TexturePool,
    TransparencyAttrib,
)


# =========================================================
# Viewer scene assembly helpers
# =========================================================

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SKYBOX_ROOT_DIR = PROJECT_ROOT / "visual" / "skybox"
SKYBOX_VARIANT_IDS = (1, 2, 3, 4, 5)
SKYBOX_HALF_EXTENT_FLOOR = 4000.0
SKYBOX_HALF_EXTENT_RATIO = 20.0

def _attach_lights(root: NodePath) -> None:
    ambient = AmbientLight("viewer_ambient")
    ambient.setColor((0.50, 0.54, 0.60, 1.0))
    ambient_np = root.attachNewNode(ambient)
    root.setLight(ambient_np)

    key = DirectionalLight("viewer_key")
    key.setColor((0.92, 0.95, 1.0, 1.0))
    key_np = root.attachNewNode(key)
    key_np.setHpr(-35.0, -60.0, 0.0)
    root.setLight(key_np)


def _attach_grid(root: NodePath, *, arena_size: float) -> None:
    step = max(20.0, round(arena_size / 10.0))
    segments = LineSegs("viewer_grid")
    segments.setThickness(0.5)
    segments.setColor(0.25, 0.31, 0.38, 0.45)

    x_value = 0.0
    while x_value <= arena_size + 0.01:
        segments.moveTo(x_value, 0.0, 0.0)
        segments.drawTo(x_value, arena_size, 0.0)
        x_value += step

    y_value = 0.0
    while y_value <= arena_size + 0.01:
        segments.moveTo(0.0, y_value, 0.0)
        segments.drawTo(arena_size, y_value, 0.0)
        y_value += step

    segments.setThickness(1.1)
    segments.setColor(0.48, 0.57, 0.66, 0.55)
    segments.moveTo(0.0, 0.0, 0.0)
    segments.drawTo(arena_size, 0.0, 0.0)
    segments.drawTo(arena_size, arena_size, 0.0)
    segments.drawTo(0.0, arena_size, 0.0)
    segments.drawTo(0.0, 0.0, 0.0)

    grid_np = root.attachNewNode(segments.create())
    grid_np.setName("viewer_grid")
    grid_np.setTransparency(TransparencyAttrib.MAlpha)


def _attach_axes(root: NodePath, *, arena_size: float) -> None:
    axis_length = max(25.0, arena_size * 0.15)
    axes = LineSegs("viewer_axes")
    axes.setThickness(3.0)

    axes.setColor(0.94, 0.35, 0.31, 1.0)
    axes.moveTo(0.0, 0.0, 0.1)
    axes.drawTo(axis_length, 0.0, 0.1)

    axes.setColor(0.31, 0.76, 0.49, 1.0)
    axes.moveTo(0.0, 0.0, 0.1)
    axes.drawTo(0.0, axis_length, 0.1)

    axes.setColor(0.37, 0.61, 0.98, 1.0)
    axes.moveTo(0.0, 0.0, 0.1)
    axes.drawTo(0.0, 0.0, axis_length * 0.45)

    axes_np = root.attachNewNode(axes.create())
    axes_np.setName("viewer_axes")


def _resolve_skybox_variant_dir(background_map_seed: int) -> Path:
    resolved_seed = int(background_map_seed)
    selected_variant_id = random.Random(resolved_seed).randrange(1, len(SKYBOX_VARIANT_IDS) + 1)
    skybox_dir = SKYBOX_ROOT_DIR / f"skybox{selected_variant_id}"
    if not skybox_dir.is_dir():
        raise FileNotFoundError(f"selected skybox directory is missing: {skybox_dir}")
    return skybox_dir


def _load_skybox_face_texture(skybox_dir: Path, face_filenames: tuple[str, ...]) -> Texture:
    texture_path: Path | None = None
    for face_filename in face_filenames:
        candidate_path = Path(skybox_dir) / str(face_filename)
        if candidate_path.is_file():
            texture_path = candidate_path
            break
    if texture_path is None:
        raise FileNotFoundError(
            f"skybox face texture is missing in {skybox_dir}; tried {face_filenames!r}."
        )
    texture = TexturePool.loadTexture(Filename.fromOsSpecific(str(texture_path)))
    if texture is None:
        raise RuntimeError(f"failed to load skybox face texture: {texture_path}")
    texture.setWrapU(Texture.WMClamp)
    texture.setWrapV(Texture.WMClamp)
    return texture


def _attach_skybox(root: NodePath, *, arena_size: float, background_map_seed: int) -> NodePath:
    half_extent = max(float(SKYBOX_HALF_EXTENT_FLOOR), float(arena_size) * float(SKYBOX_HALF_EXTENT_RATIO))
    skybox_dir = _resolve_skybox_variant_dir(background_map_seed)
    skybox_np = root.attachNewNode("viewer_skybox")
    skybox_np.setBin("background", 0)
    skybox_np.setDepthWrite(False)
    skybox_np.setDepthTest(False)
    skybox_np.setLightOff()
    skybox_np.setMaterialOff(1)
    skybox_np.setShaderOff(1)

    face_specs = (
        ("skybox_pos_x", ("right.png", "1.png"), (half_extent, 0.0, 0.0)),
        ("skybox_neg_x", ("left.png", "2.png"), (-half_extent, 0.0, 0.0)),
        ("skybox_pos_y", ("forward.png", "front.png", "3.png"), (0.0, half_extent, 0.0)),
        ("skybox_neg_y", ("back.png", "4.png"), (0.0, -half_extent, 0.0)),
        ("skybox_pos_z", ("up.png", "5.png"), (0.0, 0.0, half_extent)),
        ("skybox_neg_z", ("down.png", "6.png"), (0.0, 0.0, -half_extent)),
    )
    for face_name, face_filenames, position_xyz in face_specs:
        card_maker = CardMaker(face_name)
        card_maker.setFrame(-half_extent, half_extent, -half_extent, half_extent)
        face_np = skybox_np.attachNewNode(card_maker.generate())
        face_np.setName(face_name)
        face_np.setPos(*position_xyz)
        face_np.lookAt(0.0, 0.0, 0.0)
        face_np.setTwoSided(True)
        face_np.setTexture(_load_skybox_face_texture(skybox_dir, face_filenames))
    return skybox_np


def build_scene(root: NodePath, *, arena_size: float, background_map_seed: int) -> NodePath:
    """Build the bounded viewer-local scene shell for replay playback."""
    arena_size = float(arena_size)
    scene_root = root.attachNewNode("viewer_scene")
    _attach_skybox(scene_root, arena_size=arena_size, background_map_seed=int(background_map_seed))
    _attach_lights(scene_root)
    _attach_grid(scene_root, arena_size=arena_size)
    _attach_axes(scene_root, arena_size=arena_size)
    return scene_root
