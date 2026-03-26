from __future__ import annotations

import math

from panda3d.core import LineSegs, NodePath, TransparencyAttrib

from viz3d_panda.replay_source import ReplayBundle, ViewerFrame


def _hex_to_rgba(color: str) -> tuple[float, float, float, float]:
    normalized = str(color).strip().lstrip("#")
    if len(normalized) != 6:
        raise ValueError(f"fleet color must be a 6-digit hex value, got {color!r}.")
    red = int(normalized[0:2], 16) / 255.0
    green = int(normalized[2:4], 16) / 255.0
    blue = int(normalized[4:6], 16) / 255.0
    return (red, green, blue, 1.0)


def _heading_to_h(heading_x: float, heading_y: float) -> float:
    if heading_x == 0.0 and heading_y == 0.0:
        return 0.0
    return math.degrees(math.atan2(float(heading_x), float(heading_y)))


class UnitRenderer:
    def __init__(self, parent: NodePath, replay: ReplayBundle) -> None:
        self._parent = parent.attachNewNode("unit_renderer")
        self._replay = replay
        self._templates: dict[str, NodePath] = {}
        self._unit_nodes: dict[str, NodePath] = {}

    def _get_template(self, fleet_id: str) -> NodePath:
        template = self._templates.get(fleet_id)
        if template is not None:
            return template

        rgba = _hex_to_rgba(self._replay.fleet_colors[fleet_id])
        arrow = LineSegs(f"unit_template_{fleet_id}")
        arrow.setThickness(2.8)
        arrow.setColor(*rgba)
        arrow.moveTo(0.0, -0.2, 0.35)
        arrow.drawTo(0.0, 1.35, 0.35)
        arrow.drawTo(-0.35, 0.95, 0.35)
        arrow.moveTo(0.0, 1.35, 0.35)
        arrow.drawTo(0.35, 0.95, 0.35)
        arrow.moveTo(-0.28, -0.1, 0.35)
        arrow.drawTo(0.28, -0.1, 0.35)

        template = NodePath(arrow.create())
        template.setTransparency(TransparencyAttrib.MAlpha)
        template.setScale(1.35)
        template.hide()
        template.reparentTo(self._parent)
        self._templates[fleet_id] = template
        return template

    def sync_frame(self, frame: ViewerFrame) -> None:
        active_keys: set[str] = set()
        for unit in frame.units:
            node_key = f"{unit.fleet_id}:{unit.unit_id}"
            node = self._unit_nodes.get(node_key)
            if node is None:
                node = self._get_template(unit.fleet_id).copyTo(self._parent)
                node.setName(node_key)
                node.show()
                self._unit_nodes[node_key] = node
            node.setPos(unit.x, unit.y, unit.z)
            node.setH(_heading_to_h(unit.heading_x, unit.heading_y))
            active_keys.add(node_key)

        stale_keys = [key for key in self._unit_nodes if key not in active_keys]
        for stale_key in stale_keys:
            self._unit_nodes[stale_key].removeNode()
            del self._unit_nodes[stale_key]
