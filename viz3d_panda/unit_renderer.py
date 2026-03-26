from __future__ import annotations

import math

from panda3d.core import (
    Geom,
    GeomNode,
    GeomTriangles,
    GeomVertexData,
    GeomVertexFormat,
    GeomVertexWriter,
    LineSegs,
    NodePath,
    TransparencyAttrib,
)

from viz3d_panda.replay_source import ReplayBundle, ViewerFrame

TOKEN_ALPHA = 0.72
FIRE_LINK_MODES = {"minimal", "full"}
FIRE_LINK_MODE_STYLE = {
    "minimal": {
        "alpha": 0.12,
        "thickness": 1.05,
    },
    "full": {
        "alpha": 0.22,
        "thickness": 1.55,
    },
}
FIRE_LINK_BASE_HEIGHT = 1.18
FIRE_LINK_TARGET_HEIGHT = 1.06
FIRE_LINK_SOURCE_OFFSET = 0.92
FIRE_LINK_TARGET_OFFSET = 0.70
HP_BUCKET_SCALES = {
    5: 1.28,
    4: 1.12,
    3: 0.96,
    2: 0.80,
    1: 0.64,
}


def _hex_to_rgba(color: str) -> tuple[float, float, float, float]:
    normalized = str(color).strip().lstrip("#")
    if len(normalized) != 6:
        raise ValueError(f"fleet color must be a 6-digit hex value, got {color!r}.")
    red = int(normalized[0:2], 16) / 255.0
    green = int(normalized[2:4], 16) / 255.0
    blue = int(normalized[4:6], 16) / 255.0
    return (red, green, blue, TOKEN_ALPHA)


def _heading_to_h(heading_x: float, heading_y: float) -> float:
    if heading_x == 0.0 and heading_y == 0.0:
        return 0.0
    # The wedge mesh points along +Y at H=0, while positive Panda3D heading rotates
    # +Y toward -X. Negate here so a resolved (ux, uy) heading maps to the same
    # visible forward direction as the 2D quiver vector.
    return -math.degrees(math.atan2(float(heading_x), float(heading_y)))


def _hp_bucket(hit_points: float, max_hit_points: float) -> int:
    if max_hit_points <= 1e-9:
        return 1
    percent = max(0.0, min(100.0, (float(hit_points) / float(max_hit_points)) * 100.0))
    if percent > 80.0:
        return 5
    if percent > 60.0:
        return 4
    if percent > 40.0:
        return 3
    if percent > 20.0:
        return 2
    return 1


def _build_wedge_template(name: str) -> NodePath:
    vertex_format = GeomVertexFormat.getV3()
    vertex_data = GeomVertexData(name, vertex_format, Geom.UHStatic)
    vertex_writer = GeomVertexWriter(vertex_data, "vertex")

    vertices = (
        (-0.14, 0.84, 0.22),
        (0.14, 0.84, 0.22),
        (-0.14, 0.84, -0.22),
        (0.14, 0.84, -0.22),
        (-0.48, -0.62, 0.32),
        (0.48, -0.62, 0.32),
        (-0.48, -0.62, -0.32),
        (0.48, -0.62, -0.32),
    )
    for x_value, y_value, z_value in vertices:
        vertex_writer.addData3(float(x_value), float(y_value), float(z_value))

    triangles = GeomTriangles(Geom.UHStatic)
    faces = (
        (0, 4, 5),
        (0, 5, 1),
        (2, 3, 7),
        (2, 7, 6),
        (0, 2, 6),
        (0, 6, 4),
        (1, 5, 7),
        (1, 7, 3),
        (4, 6, 7),
        (4, 7, 5),
        (0, 1, 3),
        (0, 3, 2),
    )
    for a_index, b_index, c_index in faces:
        triangles.addVertices(int(a_index), int(b_index), int(c_index))

    geom = Geom(vertex_data)
    geom.addPrimitive(triangles)
    geom_node = GeomNode(name)
    geom_node.addGeom(geom)
    return NodePath(geom_node)


class UnitRenderer:
    def __init__(self, parent: NodePath, replay: ReplayBundle, *, fire_link_mode: str = "minimal") -> None:
        self._parent = parent.attachNewNode("unit_renderer")
        self._replay = replay
        self._templates: dict[str, NodePath] = {}
        self._unit_nodes: dict[str, NodePath] = {}
        self._target_links_np = self._parent.attachNewNode("viewer_fire_links")
        self._fire_link_mode = self._validate_fire_link_mode(fire_link_mode)

    def _validate_fire_link_mode(self, fire_link_mode: str) -> str:
        normalized = str(fire_link_mode).strip().lower()
        if normalized not in FIRE_LINK_MODES:
            allowed = ", ".join(sorted(FIRE_LINK_MODES))
            raise ValueError(f"fire_link_mode must be one of: {allowed}; got {fire_link_mode!r}.")
        return normalized

    def set_fire_link_mode(self, fire_link_mode: str) -> None:
        self._fire_link_mode = self._validate_fire_link_mode(fire_link_mode)

    @property
    def fire_link_mode(self) -> str:
        return self._fire_link_mode

    def _get_template(self, fleet_id: str) -> NodePath:
        template = self._templates.get(fleet_id)
        if template is not None:
            return template

        rgba = _hex_to_rgba(self._replay.fleet_colors[fleet_id])
        template = _build_wedge_template(f"unit_template_{fleet_id}")
        template.setColor(*rgba)
        template.setTransparency(TransparencyAttrib.MAlpha)
        template.setTwoSided(True)
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
            bucket = _hp_bucket(unit.hit_points, unit.max_hit_points)
            scale = HP_BUCKET_SCALES[bucket]
            node.setScale(scale)
            node.setPos(unit.x, unit.y, unit.z + (0.55 * scale))
            node.setH(_heading_to_h(unit.heading_x, unit.heading_y))
            active_keys.add(node_key)

        stale_keys = [key for key in self._unit_nodes if key not in active_keys]
        for stale_key in stale_keys:
            self._unit_nodes[stale_key].removeNode()
            del self._unit_nodes[stale_key]

        self._sync_fire_links(frame)

    def _sync_fire_links(self, frame: ViewerFrame) -> None:
        self._target_links_np.removeNode()
        self._target_links_np = self._parent.attachNewNode("viewer_fire_links")
        if not frame.targets:
            return

        segments = LineSegs("viewer_fire_links")
        style = FIRE_LINK_MODE_STYLE[self._fire_link_mode]
        segments.setThickness(float(style["thickness"]))
        point_map = {str(unit.unit_id): unit for unit in frame.units}
        for attacker_id, defender_id in frame.targets.items():
            attacker = point_map.get(str(attacker_id))
            defender = point_map.get(str(defender_id))
            if attacker is None or defender is None:
                continue

            attacker_rgba = _hex_to_rgba(self._replay.fleet_colors.get(attacker.fleet_id, "#4f8cff"))
            delta_x = float(defender.x) - float(attacker.x)
            delta_y = float(defender.y) - float(attacker.y)
            distance = math.sqrt((delta_x * delta_x) + (delta_y * delta_y))
            if distance <= 1e-9:
                continue

            dir_x = delta_x / distance
            dir_y = delta_y / distance
            attacker_scale = HP_BUCKET_SCALES[_hp_bucket(attacker.hit_points, attacker.max_hit_points)]
            defender_scale = HP_BUCKET_SCALES[_hp_bucket(defender.hit_points, defender.max_hit_points)]
            source_offset = FIRE_LINK_SOURCE_OFFSET * attacker_scale
            target_offset = FIRE_LINK_TARGET_OFFSET * defender_scale
            source_x = float(attacker.x) + (dir_x * source_offset)
            source_y = float(attacker.y) + (dir_y * source_offset)
            source_z = float(attacker.z) + (FIRE_LINK_BASE_HEIGHT * attacker_scale)
            target_x = float(defender.x) - (dir_x * target_offset)
            target_y = float(defender.y) - (dir_y * target_offset)
            target_z = float(defender.z) + (FIRE_LINK_TARGET_HEIGHT * defender_scale)

            segments.setColor(attacker_rgba[0], attacker_rgba[1], attacker_rgba[2], float(style["alpha"]))
            segments.moveTo(source_x, source_y, source_z)
            segments.drawTo(target_x, target_y, target_z)

        links_np = self._target_links_np.attachNewNode(segments.create())
        links_np.setTransparency(TransparencyAttrib.MAlpha)
