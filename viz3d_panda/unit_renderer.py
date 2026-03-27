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
TOKEN_ALPHA = 0.80
TOKEN_NEAR_ALPHA = 0.03
CLUSTER_NEAR_ALPHA = 0.92
DUAL_LAYER_NEAR_DISTANCE_RATIO = 0.11
DUAL_LAYER_FAR_DISTANCE_RATIO = 0.28
DUAL_LAYER_NEAR_DISTANCE_FLOOR = 18.0
DUAL_LAYER_FAR_DISTANCE_FLOOR = 70.0
CLUSTER_SHIP_COLOR = (0.36, 0.38, 0.42, 1.0)
CLUSTER_LAYOUT_OFFSETS = (
    (-0.10, 0.36, 0.12),
    (0.10, 0.34, -0.08),
    (-0.24, 0.08, -0.10),
    (0.00, 0.02, 0.15),
    (0.24, 0.08, -0.11),
    (-0.40, -0.24, 0.08),
    (-0.22, -0.34, -0.14),
    (0.00, -0.30, 0.18),
    (0.22, -0.34, -0.09),
    (0.40, -0.24, 0.11),
)
OBJECTIVE_MARKER_HEIGHT = 0.14
OBJECTIVE_MARKER_DOT_RADIUS = 1.45
OBJECTIVE_MARKER_RING_ALPHA = 0.38
OBJECTIVE_MARKER_DOT_ALPHA = 0.95
OBJECTIVE_MARKER_SEGMENTS = 40
FLEET_HALO_HEIGHT = 0.12
FLEET_HALO_PULSE_RATE = 0.085
FLEET_HALO_PULSE_MIN = 0.72
FLEET_HALO_PULSE_MAX = 1.00
FLEET_HALO_SEGMENTS = 56
FLEET_HALO_LAYERS = (
    (1.00, 3.8, 0.50),
    (1.05, 7.0, 0.30),
    (1.10, 10.0, 0.15),
)


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


def _attach_ring(
    parent: NodePath,
    *,
    name: str,
    center_x: float,
    center_y: float,
    radius: float,
    z: float,
    rgba: tuple[float, float, float, float],
    thickness: float,
    segments_count: int,
) -> NodePath:
    if float(radius) <= 1e-9:
        raise ValueError(f"{name} radius must be > 0, got {radius}.")
    if int(segments_count) < 3:
        raise ValueError(f"{name} segments_count must be >= 3, got {segments_count}.")
    segments = LineSegs(name)
    segments.setThickness(float(thickness))
    segments.setColor(float(rgba[0]), float(rgba[1]), float(rgba[2]), float(rgba[3]))
    total_segments = int(segments_count)
    for index in range(total_segments + 1):
        angle = (2.0 * math.pi * float(index)) / float(total_segments)
        x_value = float(center_x) + (float(radius) * math.cos(angle))
        y_value = float(center_y) + (float(radius) * math.sin(angle))
        if index == 0:
            segments.moveTo(x_value, y_value, float(z))
        else:
            segments.drawTo(x_value, y_value, float(z))
    ring_np = parent.attachNewNode(segments.create())
    ring_np.setName(name)
    ring_np.setTransparency(TransparencyAttrib.MAlpha)
    return ring_np


def _clamp01(value: float) -> float:
    return min(1.0, max(0.0, float(value)))


def _smoothstep(edge0: float, edge1: float, value: float) -> float:
    if float(edge1) <= float(edge0):
        return 1.0 if float(value) >= float(edge1) else 0.0
    t = _clamp01((float(value) - float(edge0)) / (float(edge1) - float(edge0)))
    return t * t * (3.0 - (2.0 * t))


def _build_wedge_template(name: str) -> NodePath:
    vertex_format = GeomVertexFormat.getV3()
    vertex_data = GeomVertexData(name, vertex_format, Geom.UHStatic)
    vertex_writer = GeomVertexWriter(vertex_data, "vertex")

    vertices = (
        (-0.20, 0.82, 0.18),
        (0.20, 0.82, 0.18),
        (-0.20, 0.82, -0.18),
        (0.20, 0.82, -0.18),
        (-0.50, -0.58, 0.28),
        (0.50, -0.58, 0.28),
        (-0.50, -0.58, -0.28),
        (0.50, -0.58, -0.28),
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


def _build_cuboid_template(name: str, *, half_width: float, half_length: float, half_height: float) -> NodePath:
    vertex_format = GeomVertexFormat.getV3()
    vertex_data = GeomVertexData(name, vertex_format, Geom.UHStatic)
    vertex_writer = GeomVertexWriter(vertex_data, "vertex")

    vertices = (
        (-half_width, half_length, half_height),
        (half_width, half_length, half_height),
        (-half_width, half_length, -half_height),
        (half_width, half_length, -half_height),
        (-half_width, -half_length, half_height),
        (half_width, -half_length, half_height),
        (-half_width, -half_length, -half_height),
        (half_width, -half_length, -half_height),
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
        self._token_nodes: dict[str, NodePath] = {}
        self._cluster_nodes: dict[str, NodePath] = {}
        self._overlay_np = self._parent.attachNewNode("viewer_overlays")
        self._objective_marker_np = self._overlay_np.attachNewNode("viewer_objective_marker")
        self._fleet_halos_np = self._overlay_np.attachNewNode("viewer_fleet_halos")
        self._target_links_np = self._parent.attachNewNode("viewer_fire_links")
        self._fleet_halo_baselines = self._build_fleet_halo_baselines()
        self._fleet_halo_state: dict[str, dict[str, float]] = {}
        self._fire_link_mode = self._validate_fire_link_mode(fire_link_mode)
        self._dual_layer_near_distance = max(
            DUAL_LAYER_NEAR_DISTANCE_FLOOR,
            float(self._replay.arena_size) * DUAL_LAYER_NEAR_DISTANCE_RATIO,
        )
        self._dual_layer_far_distance = max(
            DUAL_LAYER_FAR_DISTANCE_FLOOR,
            float(self._replay.arena_size) * DUAL_LAYER_FAR_DISTANCE_RATIO,
        )
        self._sync_objective_marker()

    def _build_fleet_halo_baselines(self) -> dict[str, tuple[float, float]]:
        if not self._replay.frames:
            return {}
        frame = self._replay.frames[0]
        fleet_points: dict[str, list[tuple[float, float, float]]] = {}
        for unit in frame.units:
            if float(unit.hit_points) <= 0.0:
                continue
            fleet_points.setdefault(str(unit.fleet_id), []).append((float(unit.x), float(unit.y), float(unit.hit_points)))
        baselines: dict[str, tuple[float, float]] = {}
        for fleet_id, points in fleet_points.items():
            if not points:
                continue
            centroid_x = sum(point[0] for point in points) / float(len(points))
            centroid_y = sum(point[1] for point in points) / float(len(points))
            max_radius = max(
                math.sqrt(((point[0] - centroid_x) * (point[0] - centroid_x)) + ((point[1] - centroid_y) * (point[1] - centroid_y)))
                for point in points
            )
            total_hp = sum(point[2] for point in points)
            if max_radius > 1e-9 and total_hp > 1e-9:
                baselines[fleet_id] = (float(max_radius), float(total_hp))
        return baselines

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

    @property
    def fleet_halo_state(self) -> dict[str, dict[str, float]]:
        return {fleet_id: dict(state) for fleet_id, state in self._fleet_halo_state.items()}

    def _get_template(self, fleet_id: str) -> NodePath:
        template = self._templates.get(fleet_id)
        if template is not None:
            return template

        rgba = _hex_to_rgba(self._replay.fleet_colors[fleet_id])
        template = NodePath(f"unit_template_{fleet_id}")
        token_np = _build_wedge_template(f"unit_token_{fleet_id}")
        token_np.setName("outer_token")
        token_np.setColor(float(rgba[0]), float(rgba[1]), float(rgba[2]), TOKEN_ALPHA)
        token_np.setTransparency(TransparencyAttrib.MAlpha)
        token_np.setTwoSided(True)
        token_np.setBin("transparent", 0)
        token_np.setDepthWrite(False)
        token_np.reparentTo(template)

        cluster_np = template.attachNewNode("inner_cluster")
        cluster_np.setTransparency(TransparencyAttrib.MAlpha)
        cluster_np.setTwoSided(True)
        cluster_np.setBin("transparent", 10)
        cluster_np.setDepthWrite(False)
        cuboid_template = _build_cuboid_template(
            f"unit_cluster_ship_{fleet_id}",
            half_width=0.020,
            half_length=0.080,
            half_height=0.020,
        )
        cuboid_template.setColor(*CLUSTER_SHIP_COLOR)
        cuboid_template.setTransparency(TransparencyAttrib.MAlpha)
        cuboid_template.setTwoSided(True)
        cuboid_template.setDepthWrite(False)
        for ship_index, (offset_x, offset_y, offset_z) in enumerate(CLUSTER_LAYOUT_OFFSETS):
            ship_np = cuboid_template.copyTo(cluster_np)
            ship_np.setName(f"cluster_ship_{ship_index}")
            ship_np.setPos(float(offset_x), float(offset_y), float(offset_z))
        cuboid_template.removeNode()

        template.hide()
        template.reparentTo(self._parent)
        self._templates[fleet_id] = template
        return template

    def update_view(self, camera_np: NodePath) -> None:
        camera_pos = camera_np.getPos(self._parent)
        near_distance = float(self._dual_layer_near_distance)
        far_distance = float(self._dual_layer_far_distance)
        for node_key, root_np in self._unit_nodes.items():
            token_np = self._token_nodes.get(node_key)
            cluster_np = self._cluster_nodes.get(node_key)
            if token_np is None or cluster_np is None:
                continue
            node_pos = root_np.getPos()
            dx = float(node_pos.x) - float(camera_pos.x)
            dy = float(node_pos.y) - float(camera_pos.y)
            dz = float(node_pos.z) - float(camera_pos.z)
            distance = math.sqrt((dx * dx) + (dy * dy) + (dz * dz))
            far_weight = _smoothstep(near_distance, far_distance, distance)
            near_weight = 1.0 - far_weight
            outer_alpha = TOKEN_NEAR_ALPHA + ((TOKEN_ALPHA - TOKEN_NEAR_ALPHA) * far_weight)
            cluster_alpha = CLUSTER_NEAR_ALPHA * near_weight
            token_np.setColorScale(1.0, 1.0, 1.0, outer_alpha / TOKEN_ALPHA)
            cluster_np.setColorScale(1.0, 1.0, 1.0, cluster_alpha)

    def _sync_objective_marker(self) -> None:
        self._objective_marker_np.removeNode()
        self._objective_marker_np = self._overlay_np.attachNewNode("viewer_objective_marker")
        fixture_readout = self._replay.metadata.get("fixture_readout")
        if not isinstance(fixture_readout, dict):
            return
        if str(self._replay.source_kind).strip().lower() != "test_run_neutral_transit_fixture":
            return
        if str(fixture_readout.get("objective_mode", "")).strip().lower() != "point_anchor":
            return
        anchor_xyz = fixture_readout.get("anchor_point_xyz")
        if not isinstance(anchor_xyz, (list, tuple)) or len(anchor_xyz) < 3:
            return
        anchor_x = float(anchor_xyz[0])
        anchor_y = float(anchor_xyz[1])
        dot_color = (0.98, 0.20, 0.20, OBJECTIVE_MARKER_DOT_ALPHA)
        ring_color = (0.98, 0.25, 0.25, OBJECTIVE_MARKER_RING_ALPHA)
        _attach_ring(
            self._objective_marker_np,
            name="objective_center_dot",
            center_x=anchor_x,
            center_y=anchor_y,
            radius=OBJECTIVE_MARKER_DOT_RADIUS,
            z=OBJECTIVE_MARKER_HEIGHT,
            rgba=dot_color,
            thickness=4.8,
            segments_count=OBJECTIVE_MARKER_SEGMENTS,
        )
        stop_radius = float(fixture_readout.get("stop_radius", 0.0))
        if stop_radius <= 0.0:
            return
        _attach_ring(
            self._objective_marker_np,
            name="objective_stop_radius",
            center_x=anchor_x,
            center_y=anchor_y,
            radius=stop_radius,
            z=OBJECTIVE_MARKER_HEIGHT,
            rgba=ring_color,
            thickness=2.2,
            segments_count=OBJECTIVE_MARKER_SEGMENTS,
        )

    def _sync_fleet_halos(self, frame: ViewerFrame) -> None:
        self._fleet_halos_np.removeNode()
        self._fleet_halos_np = self._overlay_np.attachNewNode("viewer_fleet_halos")
        self._fleet_halo_state = {}
        fleet_points: dict[str, list[tuple[float, float, float]]] = {}
        for unit in frame.units:
            if float(unit.hit_points) <= 0.0:
                continue
            fleet_points.setdefault(str(unit.fleet_id), []).append((float(unit.x), float(unit.y), float(unit.hit_points)))
        for fleet_id, points in fleet_points.items():
            if not points:
                continue
            centroid_x = sum(point[0] for point in points) / float(len(points))
            centroid_y = sum(point[1] for point in points) / float(len(points))
            current_total_hp = sum(point[2] for point in points)
            baseline = self._fleet_halo_baselines.get(fleet_id)
            if baseline is None:
                baseline_radius = max(
                    math.sqrt(((point[0] - centroid_x) * (point[0] - centroid_x)) + ((point[1] - centroid_y) * (point[1] - centroid_y)))
                    for point in points
                )
                baseline_total_hp = current_total_hp
            else:
                baseline_radius, baseline_total_hp = baseline
            if baseline_radius <= 1e-9 or baseline_total_hp <= 1e-9 or current_total_hp <= 1e-9:
                continue
            halo_radius = float(baseline_radius) * math.sqrt(float(current_total_hp) / float(baseline_total_hp))
            if halo_radius <= 1e-9:
                continue
            self._fleet_halo_state[fleet_id] = {
                "centroid_x": float(centroid_x),
                "centroid_y": float(centroid_y),
                "radius": float(halo_radius),
                "alive_total_hp": float(current_total_hp),
                "baseline_radius": float(baseline_radius),
                "baseline_total_hp": float(baseline_total_hp),
            }
            fleet_rgba = _hex_to_rgba(self._replay.fleet_colors[fleet_id])
            pulse_phase = float(frame.tick) * FLEET_HALO_PULSE_RATE
            pulse_ratio = 0.5 + (0.5 * math.sin(pulse_phase))
            pulse_scale = FLEET_HALO_PULSE_MIN + ((FLEET_HALO_PULSE_MAX - FLEET_HALO_PULSE_MIN) * pulse_ratio)
            for layer_index, (radius_scale, thickness, alpha) in enumerate(FLEET_HALO_LAYERS):
                _attach_ring(
                    self._fleet_halos_np,
                    name=f"fleet_halo_{fleet_id}_{layer_index}",
                    center_x=centroid_x,
                    center_y=centroid_y,
                    radius=halo_radius * float(radius_scale),
                    z=FLEET_HALO_HEIGHT,
                    rgba=(
                        fleet_rgba[0],
                        fleet_rgba[1],
                        fleet_rgba[2],
                        min(1.0, float(alpha) * pulse_scale),
                    ),
                    thickness=float(thickness),
                    segments_count=FLEET_HALO_SEGMENTS,
                )

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
                token_np = node.find("**/outer_token")
                cluster_np = node.find("**/inner_cluster")
                if token_np.isEmpty() or cluster_np.isEmpty():
                    raise RuntimeError(f"dual-layer unit template is missing required children for {node_key!r}")
                self._token_nodes[node_key] = token_np
                self._cluster_nodes[node_key] = cluster_np
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
            self._token_nodes.pop(stale_key, None)
            self._cluster_nodes.pop(stale_key, None)

        self._sync_fire_links(frame)
        self._sync_fleet_halos(frame)

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
