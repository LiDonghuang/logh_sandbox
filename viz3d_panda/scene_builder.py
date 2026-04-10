from __future__ import annotations

from panda3d.core import AmbientLight, DirectionalLight, LineSegs, NodePath, TransparencyAttrib


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


def build_scene(root: NodePath, *, arena_size: float) -> NodePath:
    arena_size = float(arena_size)
    scene_root = root.attachNewNode("viewer_scene")
    _attach_lights(scene_root)
    _attach_grid(scene_root, arena_size=arena_size)
    _attach_axes(scene_root, arena_size=arena_size)
    return scene_root
