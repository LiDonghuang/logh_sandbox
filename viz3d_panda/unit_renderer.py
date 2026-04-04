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

FIRE_LINK_MODES = {"disabled", "enabled"}
FIRE_LINK_ALPHA = 0.24
FIRE_LINK_THICKNESS = 1.25
FIRE_LINK_CENTER_OFFSET = 0.5
FIRE_LINK_PULSE_SPACING = 1.00
FIRE_LINK_PULSE_LENGTH = 0.75
FIRE_LINK_BASE_SPEED_PER_SECOND = 0.50
FIRE_LINK_BEAM_ALTERNATION_PERIOD_SECONDS = 1.00
FIRE_LINK_BEAM_SPREAD = 0.20
FIRE_LINK_BEAM_VERTICAL_SPREAD = 0.20
FIRE_LINK_BEAM_COUNT_BY_BUCKET = {
    5: 5,
    4: 4,
    3: 3,
    2: 2,
    1: 1,
}
FIRE_LINK_BEAM_LAYOUTS = {
    1: ((0.0, 0.0),),
    2: ((-1.0, 1.0), (1.0, -1.0)),
    3: ((-1.0, 1.0), (0.0, 0.0), (1.0, -1.0)),
    4: ((-1.0, 1.0), (-1.0, -1.0), (1.0, 1.0), (1.0, -1.0)),
    5: ((-1.0, 1.0), (-1.0, -1.0), (0.0, 0.0), (1.0, 1.0), (1.0, -1.0)),
}

# Unit dual-layer appearance, ordered near -> mid -> far.
TOKEN_NEAR_ALPHA, TOKEN_MID_ALPHA, TOKEN_FAR_ALPHA = (0.02, 0.50, 0.90)
CLUSTER_NEAR_ALPHA, CLUSTER_MID_ALPHA, CLUSTER_FAR_ALPHA = (0.90, 0.50, 0.0)
DUAL_LAYER_NEAR_DISTANCE_RATIO, DUAL_LAYER_MID_DISTANCE_RATIO, DUAL_LAYER_FAR_DISTANCE_RATIO = (0.11, 0.19, 0.28)
DUAL_LAYER_NEAR_DISTANCE_FLOOR, DUAL_LAYER_MID_DISTANCE_FLOOR, DUAL_LAYER_FAR_DISTANCE_FLOOR = (18.0, 42.0, 70.0)

# Unit bucket sizing and inner-cluster composition.
HP_BUCKET_SCALES = {
    5: 1.28,
    4: 1.12,
    3: 0.96,
    2: 0.80,
    1: 0.64,
}
CLUSTER_VISIBLE_COUNT_BY_BUCKET = {
    5: 10,
    4: 8,
    3: 6,
    2: 4,
    1: 2,
}
CLUSTER_VISIBLE_INDICES_BY_BUCKET = {
    5: (0, 1, 2, 3, 4, 5, 6, 7, 8, 9),
    4: (2, 3, 4, 5, 6, 7, 8, 9),
    3: (2, 3, 4, 6, 7, 8),
    2: (2, 3, 4, 7),
    1: (3, 7),
}

# Unit inner-cluster geometry.
CLUSTER_SHIP_COLOR = (0.36, 0.38, 0.42, 1.0)
CLUSTER_SHIP_MODEL_UNIT = 0.040
# length / width / height, with the ship's fore-aft axis running along +Y.
CLUSTER_SHIP_FRONT_BOX_DIMS = (4.0, 0.75, 1.0)
CLUSTER_SHIP_REAR_BOX_DIMS = (2.0, 1.5, 1.5)
CLUSTER_LAYOUT_OFFSETS = (
    (-0.10, 0.418, 0.108),
    (0.10, 0.398, -0.092),
    (-0.24, 0.138, -0.112),
    (0.00, 0.078, 0.138),
    (0.24, 0.138, -0.122),
    (-0.40, -0.182, 0.068),
    (-0.22, -0.282, -0.152),
    (0.00, -0.242, 0.168),
    (0.22, -0.282, -0.102),
    (0.40, -0.182, 0.098),
)
OBJECTIVE_MARKER_HEIGHT = 0.14
OBJECTIVE_MARKER_DOT_RADIUS = 1.45
OBJECTIVE_MARKER_RING_ALPHA = 0.38
OBJECTIVE_MARKER_DOT_ALPHA = 0.95
OBJECTIVE_MARKER_SEGMENTS = 40
FLEET_HALO_HEIGHT = -0.50
FLEET_HALO_PULSE_PERIOD_SECONDS = 5.0
FLEET_HALO_PULSE_MIN = 0.85
FLEET_HALO_PULSE_MAX = 0.97
FLEET_HALO_SEGMENTS = 56
FLEET_HALO_HIDE_FORWARD_Z_THRESHOLD = 0.10
FLEET_HALO_LAYERS = (
    (0.0, 2.9, 0.28),
    (0.7, 6.1, 0.10),
)


def _hex_to_rgba(color: str) -> tuple[float, float, float, float]:
    normalized = str(color).strip().lstrip("#")
    if len(normalized) != 6:
        raise ValueError(f"fleet color must be a 6-digit hex value, got {color!r}.")
    red = int(normalized[0:2], 16) / 255.0
    green = int(normalized[2:4], 16) / 255.0
    blue = int(normalized[4:6], 16) / 255.0
    return (red, green, blue, TOKEN_FAR_ALPHA)


def _brighten_rgb(
    rgba: tuple[float, float, float, float],
    *,
    toward_white: float,
    alpha: float,
) -> tuple[float, float, float, float]:
    lift = max(0.0, min(1.0, float(toward_white)))
    return (
        float(rgba[0]) + ((1.0 - float(rgba[0])) * lift),
        float(rgba[1]) + ((1.0 - float(rgba[1])) * lift),
        float(rgba[2]) + ((1.0 - float(rgba[2])) * lift),
        float(alpha),
    )


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


def _lerp(a_value: float, b_value: float, alpha: float) -> float:
    return ((1.0 - float(alpha)) * float(a_value)) + (float(alpha) * float(b_value))


def _visible_fire_link_beam_indices(beam_count: int, alternation_slot: int) -> tuple[int, ...]:
    if int(beam_count) <= 1:
        return tuple(range(max(1, int(beam_count))))
    phase = int(alternation_slot) % 2
    if int(beam_count) == 2:
        return (0,) if phase == 0 else (1,)
    if int(beam_count) == 3:
        return (0, 1) if phase == 0 else (1, 2)
    if int(beam_count) == 4:
        return (0, 3) if phase == 0 else (1, 2)
    if int(beam_count) >= 5:
        return (0, 2, 4) if phase == 0 else (1, 2, 3)
    return tuple(range(max(1, int(beam_count))))


def _interpolate_heading_xy(
    current_heading: tuple[float, float],
    next_heading: tuple[float, float],
    alpha: float,
) -> tuple[float, float]:
    current_x = float(current_heading[0])
    current_y = float(current_heading[1])
    next_x = float(next_heading[0])
    next_y = float(next_heading[1])
    blended_x = _lerp(current_x, next_x, alpha)
    blended_y = _lerp(current_y, next_y, alpha)
    length = math.sqrt((blended_x * blended_x) + (blended_y * blended_y))
    if length <= 1e-9:
        current_length = math.sqrt((current_x * current_x) + (current_y * current_y))
        if current_length <= 1e-9:
            return (0.0, 1.0)
        return (current_x / current_length, current_y / current_length)
    return (blended_x / length, blended_y / length)


def _build_wedge_template(name: str) -> NodePath:
    vertex_format = GeomVertexFormat.getV3()
    vertex_data = GeomVertexData(name, vertex_format, Geom.UHStatic)
    vertex_writer = GeomVertexWriter(vertex_data, "vertex")

    vertices = (
        (-0.20, 0.8461847389558232, 0.18),
        (0.20, 0.8461847389558232, 0.18),
        (-0.20, 0.8461847389558232, -0.18),
        (0.20, 0.8461847389558232, -0.18),
        (-0.50, -0.5538152610441767, 0.28),
        (0.50, -0.5538152610441767, 0.28),
        (-0.50, -0.5538152610441767, -0.28),
        (0.50, -0.5538152610441767, -0.28),
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


def _build_box_template(name: str, *, half_x: float, half_y: float, half_z: float) -> NodePath:
    vertex_format = GeomVertexFormat.getV3()
    vertex_data = GeomVertexData(name, vertex_format, Geom.UHStatic)
    vertex_writer = GeomVertexWriter(vertex_data, "vertex")

    vertices = (
        (-half_x, half_y, half_z),
        (half_x, half_y, half_z),
        (-half_x, half_y, -half_z),
        (half_x, half_y, -half_z),
        (-half_x, -half_y, half_z),
        (half_x, -half_y, half_z),
        (-half_x, -half_y, -half_z),
        (half_x, -half_y, -half_z),
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


def _build_cluster_ship_template(name: str) -> NodePath:
    model_unit = float(CLUSTER_SHIP_MODEL_UNIT)
    front_half_x = 0.5 * float(CLUSTER_SHIP_FRONT_BOX_DIMS[1]) * model_unit
    front_half_y = 0.5 * float(CLUSTER_SHIP_FRONT_BOX_DIMS[0]) * model_unit
    front_half_z = 0.5 * float(CLUSTER_SHIP_FRONT_BOX_DIMS[2]) * model_unit
    rear_half_x = 0.5 * float(CLUSTER_SHIP_REAR_BOX_DIMS[1]) * model_unit
    rear_half_y = 0.5 * float(CLUSTER_SHIP_REAR_BOX_DIMS[0]) * model_unit
    rear_half_z = 0.5 * float(CLUSTER_SHIP_REAR_BOX_DIMS[2]) * model_unit

    ship_template = NodePath(name)

    rear_box = _build_box_template(
        f"{name}_rear",
        half_x=rear_half_x,
        half_y=rear_half_y,
        half_z=rear_half_z,
    )
    rear_box.reparentTo(ship_template)
    rear_box.setPos(0.0, -front_half_y, 0.0)

    front_box = _build_box_template(
        f"{name}_front",
        half_x=front_half_x,
        half_y=front_half_y,
        half_z=front_half_z,
    )
    front_box.reparentTo(ship_template)
    front_box.setPos(0.0, rear_half_y, rear_half_z - front_half_z)

    return ship_template


class UnitRenderer:
    def __init__(self, parent: NodePath, replay: ReplayBundle, *, fire_link_mode: str = "enabled") -> None:
        self._parent = parent.attachNewNode("unit_renderer")
        self._replay = replay
        self._current_frame: ViewerFrame | None = None
        self._templates: dict[str, NodePath] = {}
        self._unit_nodes: dict[str, NodePath] = {}
        self._token_nodes: dict[str, NodePath] = {}
        self._cluster_nodes: dict[str, NodePath] = {}
        self._cluster_ship_nodes: dict[str, list[NodePath]] = {}
        self._overlay_np = self._parent.attachNewNode("viewer_overlays")
        self._objective_marker_np = self._overlay_np.attachNewNode("viewer_objective_marker")
        self._fleet_halos_np = self._overlay_np.attachNewNode("viewer_fleet_halos")
        self._target_links_np = self._parent.attachNewNode("viewer_fire_links")
        self._fleet_halo_nodes: dict[str, list[NodePath]] = {}
        self._fleet_halo_baselines = self._build_fleet_halo_baselines()
        self._fleet_halo_state: dict[str, dict[str, float]] = {}
        self._fire_link_mode = self._validate_fire_link_mode(fire_link_mode)
        self._fire_link_pulse_phase = 0.0
        self._next_fire_link_frame: ViewerFrame | None = None
        self._fire_link_position_alpha = 0.0
        self._playback_level_index = 0
        self._playback_fps = 2.0
        self._last_fire_link_signature: tuple[int, int, float, int, float] | None = None
        self._dual_layer_near_distance = max(
            DUAL_LAYER_NEAR_DISTANCE_FLOOR,
            float(self._replay.arena_size) * DUAL_LAYER_NEAR_DISTANCE_RATIO,
        )
        self._dual_layer_mid_distance = max(
            self._dual_layer_near_distance,
            max(
                DUAL_LAYER_MID_DISTANCE_FLOOR,
                float(self._replay.arena_size) * DUAL_LAYER_MID_DISTANCE_RATIO,
            ),
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

    def set_fire_link_pulse_phase(self, pulse_phase: float) -> None:
        self._fire_link_pulse_phase = max(0.0, min(1.0, float(pulse_phase)))

    def set_playback_level_index(self, playback_level_index: int) -> None:
        normalized_index = max(0, int(playback_level_index))
        if normalized_index != self._playback_level_index:
            self._playback_level_index = normalized_index
            self._last_fire_link_signature = None

    def set_playback_fps(self, playback_fps: float) -> None:
        normalized_fps = max(1e-6, float(playback_fps))
        if abs(normalized_fps - self._playback_fps) > 1e-9:
            self._playback_fps = normalized_fps
            self._last_fire_link_signature = None

    def refresh_fire_links(
        self,
        frame: ViewerFrame,
        *,
        pulse_phase: float,
        next_frame: ViewerFrame | None = None,
        position_alpha: float = 0.0,
    ) -> None:
        self.set_fire_link_pulse_phase(pulse_phase)
        self._current_frame = frame
        self._next_fire_link_frame = next_frame
        self._fire_link_position_alpha = _clamp01(position_alpha)

    @property
    def fire_link_mode(self) -> str:
        return self._fire_link_mode

    @property
    def fleet_halo_state(self) -> dict[str, dict[str, float]]:
        return {fleet_id: dict(state) for fleet_id, state in self._fleet_halo_state.items()}

    def _get_fleet_halo_nodes(self, fleet_id: str) -> list[NodePath]:
        halo_nodes = self._fleet_halo_nodes.get(fleet_id)
        if halo_nodes is not None:
            return halo_nodes
        halo_nodes = []
        for layer_index, (_radius_offset, thickness, _alpha) in enumerate(FLEET_HALO_LAYERS):
            ring_np = _attach_ring(
                self._fleet_halos_np,
                name=f"fleet_halo_{fleet_id}_{layer_index}",
                center_x=0.0,
                center_y=0.0,
                radius=1.0,
                z=0.0,
                rgba=(1.0, 1.0, 1.0, 1.0),
                thickness=float(thickness),
                segments_count=FLEET_HALO_SEGMENTS,
            )
            ring_np.setBin("transparent", -10)
            ring_np.setDepthWrite(False)
            ring_np.hide()
            halo_nodes.append(ring_np)
        self._fleet_halo_nodes[fleet_id] = halo_nodes
        return halo_nodes

    def _clear_fire_links(self) -> None:
        self._target_links_np.removeNode()
        self._target_links_np = self._parent.attachNewNode("viewer_fire_links")
        self._last_fire_link_signature = None

    def _get_template(self, fleet_id: str) -> NodePath:
        template = self._templates.get(fleet_id)
        if template is not None:
            return template

        rgba = _hex_to_rgba(self._replay.fleet_colors[fleet_id])
        template = NodePath(f"unit_template_{fleet_id}")
        token_np = _build_wedge_template(f"unit_token_{fleet_id}")
        token_np.setName("outer_token")
        token_np.setColor(float(rgba[0]), float(rgba[1]), float(rgba[2]), TOKEN_FAR_ALPHA)
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
        ship_template = _build_cluster_ship_template(f"unit_cluster_ship_{fleet_id}")
        ship_template.setColor(*CLUSTER_SHIP_COLOR)
        ship_template.setTransparency(TransparencyAttrib.MAlpha)
        ship_template.setTwoSided(True)
        ship_template.setDepthWrite(False)
        for ship_index, (offset_x, offset_y, offset_z) in enumerate(CLUSTER_LAYOUT_OFFSETS):
            ship_np = ship_template.copyTo(cluster_np)
            ship_np.setName(f"cluster_ship_{ship_index}")
            ship_np.setPos(float(offset_x), float(offset_y), float(offset_z))
        ship_template.removeNode()

        template.hide()
        template.reparentTo(self._parent)
        self._templates[fleet_id] = template
        return template

    def update_view(self, camera_np: NodePath) -> None:
        camera_pos = camera_np.getPos(self._parent)
        near_distance = float(self._dual_layer_near_distance)
        mid_distance = float(self._dual_layer_mid_distance)
        far_distance = float(self._dual_layer_far_distance)
        min_unit_distance: float | None = None
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
            if min_unit_distance is None or distance < min_unit_distance:
                min_unit_distance = distance
            if distance <= near_distance:
                outer_alpha = TOKEN_NEAR_ALPHA
                cluster_alpha = CLUSTER_NEAR_ALPHA
            elif distance <= mid_distance:
                mid_weight = _smoothstep(near_distance, mid_distance, distance)
                outer_alpha = _lerp(TOKEN_NEAR_ALPHA, TOKEN_MID_ALPHA, mid_weight)
                cluster_alpha = _lerp(CLUSTER_NEAR_ALPHA, CLUSTER_MID_ALPHA, mid_weight)
            elif distance <= far_distance:
                far_weight = _smoothstep(mid_distance, far_distance, distance)
                outer_alpha = _lerp(TOKEN_MID_ALPHA, TOKEN_FAR_ALPHA, far_weight)
                cluster_alpha = _lerp(CLUSTER_MID_ALPHA, CLUSTER_FAR_ALPHA, far_weight)
            else:
                outer_alpha = TOKEN_FAR_ALPHA
                cluster_alpha = CLUSTER_FAR_ALPHA
            token_alpha_scale = 1.0
            if TOKEN_FAR_ALPHA > 1e-9:
                token_alpha_scale = outer_alpha / TOKEN_FAR_ALPHA
            token_np.setColorScale(1.0, 1.0, 1.0, token_alpha_scale)
            if cluster_alpha > 1e-4:
                cluster_np.show()
                cluster_np.setColorScale(1.0, 1.0, 1.0, cluster_alpha)
            else:
                cluster_np.hide()
        if self._current_frame is not None:
            should_show_fire_links = bool(min_unit_distance is not None and min_unit_distance <= far_distance)
            if (
                self._fire_link_mode == "disabled"
                or not self._current_frame.targets
                or not should_show_fire_links
            ):
                if not self._target_links_np.isEmpty() and self._target_links_np.getNumChildren() > 0:
                    self._clear_fire_links()
            else:
                pulse_signature = round(float(self._fire_link_pulse_phase), 2)
                next_tick_signature = -1 if self._next_fire_link_frame is None else int(self._next_fire_link_frame.tick)
                position_signature = (
                    0.0
                    if self._next_fire_link_frame is None
                    else round(float(self._fire_link_position_alpha), 2)
                )
                fire_link_signature = (
                    int(self._current_frame.tick),
                    int(len(self._current_frame.targets)),
                    float(pulse_signature),
                    int(next_tick_signature),
                    float(position_signature),
                )
                if fire_link_signature != self._last_fire_link_signature:
                    self._sync_fire_links(self._current_frame)
                    self._last_fire_link_signature = fire_link_signature
        halo_visible = True
        camera_forward = camera_np.getQuat(self._parent).getForward()
        if abs(float(camera_forward.z)) <= FLEET_HALO_HIDE_FORWARD_Z_THRESHOLD:
            halo_visible = False
        active_halo_ids = set(self._fleet_halo_state.keys())
        for fleet_id, halo_nodes in self._fleet_halo_nodes.items():
            should_show_halo = halo_visible and fleet_id in active_halo_ids
            for halo_np in halo_nodes:
                if should_show_halo:
                    halo_np.show()
                else:
                    halo_np.hide()

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

    def _sync_fleet_halos(
        self,
        frame: ViewerFrame,
        *,
        tick_offset: float = 0.0,
        use_node_positions: bool = False,
    ) -> None:
        self._fleet_halo_state = {}
        fleet_points: dict[str, list[tuple[float, float, float]]] = {}
        for unit in frame.units:
            if float(unit.hit_points) <= 0.0:
                continue
            point_x = float(unit.x)
            point_y = float(unit.y)
            if use_node_positions:
                node_key = f"{unit.fleet_id}:{unit.unit_id}"
                node = self._unit_nodes.get(node_key)
                if node is None:
                    continue
                node_pos = node.getPos()
                point_x = float(node_pos.x)
                point_y = float(node_pos.y)
            fleet_points.setdefault(str(unit.fleet_id), []).append((point_x, point_y, float(unit.hit_points)))
        active_fleet_ids: set[str] = set()
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
            active_fleet_ids.add(fleet_id)
            self._fleet_halo_state[fleet_id] = {
                "centroid_x": float(centroid_x),
                "centroid_y": float(centroid_y),
                "radius": float(halo_radius),
                "alive_total_hp": float(current_total_hp),
                "baseline_radius": float(baseline_radius),
                "baseline_total_hp": float(baseline_total_hp),
            }
            fleet_rgba = _hex_to_rgba(self._replay.fleet_colors[fleet_id])
            playback_seconds = (float(frame.tick) + float(tick_offset)) / max(1e-6, float(self._playback_fps))
            pulse_phase = (2.0 * math.pi * playback_seconds) / FLEET_HALO_PULSE_PERIOD_SECONDS
            pulse_ratio = 0.5 + (0.5 * math.sin(pulse_phase))
            pulse_scale = FLEET_HALO_PULSE_MIN + ((FLEET_HALO_PULSE_MAX - FLEET_HALO_PULSE_MIN) * pulse_ratio)
            halo_nodes = self._get_fleet_halo_nodes(fleet_id)
            for layer_index, (radius_offset, _thickness, alpha) in enumerate(FLEET_HALO_LAYERS):
                halo_np = halo_nodes[layer_index]
                halo_np.setPos(float(centroid_x), float(centroid_y), FLEET_HALO_HEIGHT)
                halo_np.setScale(float(halo_radius) + float(radius_offset))
                halo_np.setColorScale(
                    float(fleet_rgba[0]),
                    float(fleet_rgba[1]),
                    float(fleet_rgba[2]),
                    min(1.0, float(alpha) * pulse_scale),
                )
                halo_np.show()
        stale_fleet_ids = [fleet_id for fleet_id in self._fleet_halo_nodes if fleet_id not in active_fleet_ids]
        for stale_fleet_id in stale_fleet_ids:
            for halo_np in self._fleet_halo_nodes[stale_fleet_id]:
                halo_np.removeNode()
            del self._fleet_halo_nodes[stale_fleet_id]

    def sync_frame(self, frame: ViewerFrame, *, pulse_phase: float = 0.0) -> None:
        self.set_fire_link_pulse_phase(pulse_phase)
        self._current_frame = frame
        self._next_fire_link_frame = None
        self._fire_link_position_alpha = 0.0
        self._last_fire_link_signature = None
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
                ship_nodes: list[NodePath] = []
                for ship_index in range(len(CLUSTER_LAYOUT_OFFSETS)):
                    ship_np = node.find(f"**/cluster_ship_{ship_index}")
                    if ship_np.isEmpty():
                        raise RuntimeError(f"unit cluster ship {ship_index} is missing for {node_key!r}")
                    ship_nodes.append(ship_np)
                self._cluster_ship_nodes[node_key] = ship_nodes
            bucket = _hp_bucket(unit.hit_points, unit.max_hit_points)
            scale = HP_BUCKET_SCALES[bucket]
            self._token_nodes[node_key].setScale(scale)
            visible_indices = set(CLUSTER_VISIBLE_INDICES_BY_BUCKET[bucket][: CLUSTER_VISIBLE_COUNT_BY_BUCKET[bucket]])
            for ship_index, ship_np in enumerate(self._cluster_ship_nodes[node_key]):
                if ship_index in visible_indices:
                    ship_np.show()
                else:
                    ship_np.hide()
            node.setPos(unit.x, unit.y, unit.z)
            node.setH(_heading_to_h(unit.heading_x, unit.heading_y))
            active_keys.add(node_key)

        stale_keys = [key for key in self._unit_nodes if key not in active_keys]
        for stale_key in stale_keys:
            self._unit_nodes[stale_key].removeNode()
            del self._unit_nodes[stale_key]
            self._token_nodes.pop(stale_key, None)
            self._cluster_nodes.pop(stale_key, None)
            self._cluster_ship_nodes.pop(stale_key, None)

        self._sync_fleet_halos(frame)

    def apply_interpolated_transforms(
        self,
        current_frame: ViewerFrame,
        next_frame: ViewerFrame,
        *,
        alpha: float,
    ) -> None:
        interpolation_alpha = _clamp01(alpha)
        if interpolation_alpha <= 1e-9:
            return
        next_units = {
            (str(unit.fleet_id), str(unit.unit_id)): unit
            for unit in next_frame.units
        }
        for unit in current_frame.units:
            node_key = f"{unit.fleet_id}:{unit.unit_id}"
            node = self._unit_nodes.get(node_key)
            if node is None:
                continue
            next_unit = next_units.get((str(unit.fleet_id), str(unit.unit_id)))
            if next_unit is None:
                continue
            bucket = _hp_bucket(unit.hit_points, unit.max_hit_points)
            blended_x = _lerp(unit.x, next_unit.x, interpolation_alpha)
            blended_y = _lerp(unit.y, next_unit.y, interpolation_alpha)
            blended_z = _lerp(unit.z, next_unit.z, interpolation_alpha)
            blended_heading = _interpolate_heading_xy(
                (float(unit.heading_x), float(unit.heading_y)),
                (float(next_unit.heading_x), float(next_unit.heading_y)),
                interpolation_alpha,
            )
            node.setPos(blended_x, blended_y, blended_z)
            node.setH(_heading_to_h(float(blended_heading[0]), float(blended_heading[1])))

    def _sync_fire_links(self, frame: ViewerFrame) -> None:
        self._target_links_np.removeNode()
        self._target_links_np = self._parent.attachNewNode("viewer_fire_links")
        if self._fire_link_mode == "disabled" or not frame.targets:
            return

        segments = LineSegs("viewer_fire_links")
        segments.setThickness(float(FIRE_LINK_THICKNESS))
        point_map = {str(unit.unit_id): unit for unit in frame.units}
        next_point_map: dict[str, object] | None = None
        if self._next_fire_link_frame is not None and self._fire_link_position_alpha > 1e-6:
            next_point_map = {
                str(unit.unit_id): unit
                for unit in self._next_fire_link_frame.units
            }
        pulse_spacing = float(FIRE_LINK_PULSE_SPACING)
        pulse_length = float(FIRE_LINK_PULSE_LENGTH)
        playback_seconds = (float(frame.tick) + float(self._fire_link_pulse_phase)) / max(1e-6, float(self._playback_fps))
        visual_speed_multiplier = math.sqrt(float(self._playback_level_index) + 1.0)
        pulse_shift = (
            (playback_seconds * FIRE_LINK_BASE_SPEED_PER_SECOND * visual_speed_multiplier)
            % pulse_spacing
        )
        alternation_slot = int(math.floor(playback_seconds / FIRE_LINK_BEAM_ALTERNATION_PERIOD_SECONDS))
        for attacker_id, defender_id in frame.targets.items():
            attacker = point_map.get(str(attacker_id))
            defender = point_map.get(str(defender_id))
            if attacker is None or defender is None:
                continue

            attacker_rgba = _brighten_rgb(
                _hex_to_rgba(self._replay.fleet_colors.get(attacker.fleet_id, "#4f8cff")),
                toward_white=0.42,
                alpha=FIRE_LINK_ALPHA,
            )
            attacker_bucket = _hp_bucket(attacker.hit_points, attacker.max_hit_points)
            delta_x = float(defender.x) - float(attacker.x)
            delta_y = float(defender.y) - float(attacker.y)
            distance = math.sqrt((delta_x * delta_x) + (delta_y * delta_y))
            if distance <= (2.0 * FIRE_LINK_CENTER_OFFSET):
                continue

            dir_x = delta_x / distance
            dir_y = delta_y / distance
            lateral_x = -dir_y
            lateral_y = dir_x
            next_attacker = None if next_point_map is None else next_point_map.get(str(attacker_id))
            next_defender = None if next_point_map is None else next_point_map.get(str(defender_id))
            source_base_x = float(attacker.x)
            source_base_y = float(attacker.y)
            source_base_z = float(attacker.z)
            target_base_x = float(defender.x)
            target_base_y = float(defender.y)
            target_base_z = float(defender.z)
            if next_attacker is not None:
                source_base_x = _lerp(float(attacker.x), float(next_attacker.x), self._fire_link_position_alpha)
                source_base_y = _lerp(float(attacker.y), float(next_attacker.y), self._fire_link_position_alpha)
                source_base_z = _lerp(float(attacker.z), float(next_attacker.z), self._fire_link_position_alpha)
            if next_defender is not None:
                target_base_x = _lerp(float(defender.x), float(next_defender.x), self._fire_link_position_alpha)
                target_base_y = _lerp(float(defender.y), float(next_defender.y), self._fire_link_position_alpha)
                target_base_z = _lerp(float(defender.z), float(next_defender.z), self._fire_link_position_alpha)
            source_x = source_base_x + (dir_x * FIRE_LINK_CENTER_OFFSET)
            source_y = source_base_y + (dir_y * FIRE_LINK_CENTER_OFFSET)
            source_z = source_base_z
            target_x = target_base_x - (dir_x * FIRE_LINK_CENTER_OFFSET)
            target_y = target_base_y - (dir_y * FIRE_LINK_CENTER_OFFSET)
            target_z = target_base_z
            link_dx = target_x - source_x
            link_dy = target_y - source_y
            link_dz = target_z - source_z
            link_length = math.sqrt((link_dx * link_dx) + (link_dy * link_dy) + (link_dz * link_dz))
            if link_length <= 1e-9:
                continue
            beam_count = FIRE_LINK_BEAM_COUNT_BY_BUCKET[attacker_bucket]
            attacker_scale = HP_BUCKET_SCALES[attacker_bucket]
            beam_layout = FIRE_LINK_BEAM_LAYOUTS.get(beam_count, FIRE_LINK_BEAM_LAYOUTS[1])
            visible_beam_indices = _visible_fire_link_beam_indices(
                beam_count,
                alternation_slot,
            )
            beam_spread = FIRE_LINK_BEAM_SPREAD * float(attacker_scale)
            beam_vertical_spread = FIRE_LINK_BEAM_VERTICAL_SPREAD * float(attacker_scale)
            segments.setColor(attacker_rgba[0], attacker_rgba[1], attacker_rgba[2], attacker_rgba[3])
            for beam_index in visible_beam_indices:
                lateral_factor, vertical_factor = beam_layout[int(beam_index)]
                lateral_offset = float(lateral_factor) * beam_spread
                vertical_offset = float(vertical_factor) * beam_vertical_spread
                beam_source_x = source_x + (lateral_x * lateral_offset)
                beam_source_y = source_y + (lateral_y * lateral_offset)
                beam_source_z = source_z + vertical_offset
                beam_target_x = target_x + (lateral_x * lateral_offset)
                beam_target_y = target_y + (lateral_y * lateral_offset)
                beam_target_z = target_z + vertical_offset
                beam_link_dz = beam_target_z - beam_source_z
                cursor = float(pulse_shift) - pulse_spacing
                while cursor < link_length:
                    pulse_start = max(0.0, float(cursor))
                    pulse_end = min(link_length, float(cursor) + pulse_length)
                    if pulse_end > pulse_start:
                        start_ratio = pulse_start / link_length
                        end_ratio = pulse_end / link_length
                        segments.moveTo(
                            beam_source_x + (link_dx * start_ratio),
                            beam_source_y + (link_dy * start_ratio),
                            beam_source_z + (beam_link_dz * start_ratio),
                        )
                        segments.drawTo(
                            beam_source_x + (link_dx * end_ratio),
                            beam_source_y + (link_dy * end_ratio),
                            beam_source_z + (beam_link_dz * end_ratio),
                        )
                    cursor += pulse_spacing

        links_np = self._target_links_np.attachNewNode(segments.create())
        links_np.setTransparency(TransparencyAttrib.MAlpha)
