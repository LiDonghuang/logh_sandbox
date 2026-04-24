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

# =========================================================
# File-level renderer constants
# =========================================================

FIRE_LINK_MODES = {"disabled", "enabled"}
FIRE_LINK_ALPHA = 0.6
FIRE_LINK_THICKNESS = 0.6
FIRE_LINK_CENTER_OFFSET = 0.5
FIRE_LINK_PULSE_SPACING = 0.95
FIRE_LINK_PULSE_LENGTH = 0.05
FIRE_LINK_BASE_SPEED_PER_SECOND = 2.0
FIRE_LINK_BEAM_ALTERNATION_PERIOD_SECONDS = 0.5
FIRE_LINK_BEAM_SPREAD = 0.10
FIRE_LINK_BEAM_VERTICAL_SPREAD = 0.10
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

# Unit dual-layer appearance, ordered level 1 -> level 5.
TOKEN_ALPHA_BY_LEVEL = (0.01, 0.1, 0.4, 0.6, 0.8)
CLUSTER_ALPHA_BY_LEVEL = (0.9, 0.01, 0.0, 0.0, 0.0)
DUAL_LAYER_DISTANCE_BY_LEVEL = (10.0, 50.0, 100.0, 150.0, 200.0)

# Unit bucket sizing and inner-cluster composition.
HP_BUCKET_SCALES = {
    5: 1.28,
    4: 1.12,
    3: 0.96,
    2: 0.80,
    1: 0.64,
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
CLUSTER_SHIP_MODEL_UNIT = 0.025
# length / width / height, with the ship's fore-aft axis running along +Y.
CLUSTER_SHIP_FRONT_BOX_DIMS = (4.0, 0.6, 1.0)
CLUSTER_SHIP_REAR_BOX_DIMS = (2.0, 1.5, 1.5)
CLUSTER_SWAY_AMPLITUDE_X = 0.04
CLUSTER_SWAY_AMPLITUDE_Y = 0.1
CLUSTER_SWAY_AMPLITUDE_Z = 0.06
CLUSTER_SWAY_FREQUENCY = 0.05
CLUSTER_SWAY_CLOCK_SCALE = 1.0
CLUSTER_SWAY_MAX_ENABLED_GEAR_INDEX = 2
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


# =========================================================
# Pure color / geometry helpers
# =========================================================

def _hex_to_rgba(color: str) -> tuple[float, float, float, float]:
    normalized = str(color).strip().lstrip("#")
    if len(normalized) != 6:
        raise ValueError(f"fleet color must be a 6-digit hex value, got {color!r}.")
    red = int(normalized[0:2], 16) / 255.0
    green = int(normalized[2:4], 16) / 255.0
    blue = int(normalized[4:6], 16) / 255.0
    return (red, green, blue, float(TOKEN_ALPHA_BY_LEVEL[-1]))


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


def _cluster_ship_base_offset(ship_index: int) -> tuple[float, float, float]:
    base_offset = CLUSTER_LAYOUT_OFFSETS[int(ship_index)]
    return (float(base_offset[0]), float(base_offset[1]), float(base_offset[2]))


def _cluster_ship_sway_profile(ship_index: int) -> dict[str, float]:
    base_offset = _cluster_ship_base_offset(int(ship_index))
    x_phase = (0.61 * float(ship_index)) + 0.15
    y_phase = (0.83 * float(ship_index)) + 1.35
    z_phase = (0.47 * float(ship_index)) + 2.10
    return {
        "base_x": float(base_offset[0]),
        "base_y": float(base_offset[1]),
        "base_z": float(base_offset[2]),
        "sin_x_phase": math.sin(x_phase),
        "cos_x_phase": math.cos(x_phase),
        "sin_y_phase": math.sin(y_phase),
        "cos_y_phase": math.cos(y_phase),
        "sin_z_phase": math.sin(z_phase),
        "cos_z_phase": math.cos(z_phase),
    }


def _build_cluster_ship_sway_profiles() -> tuple[dict[str, float], ...]:
    return tuple(
        _cluster_ship_sway_profile(ship_index)
        for ship_index in range(len(CLUSTER_LAYOUT_OFFSETS))
    )


# =========================================================
# Viewer-local mesh template builders
# =========================================================

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
    """Maintained viewer-local unit/overlay renderer for replay playback."""

    # -----------------------------------------------------
    # A. renderer bootstrap / public control surface
    # -----------------------------------------------------
    def __init__(self, parent: NodePath, replay: ReplayBundle, *, fire_link_mode: str = "enabled") -> None:
        self._parent = parent.attachNewNode("unit_renderer")
        self._replay = replay
        self._current_frame: ViewerFrame | None = None
        self._templates: dict[str, NodePath] = {}
        self._unit_nodes: dict[str, NodePath] = {}
        self._token_nodes: dict[str, NodePath] = {}
        self._token_scale_state: dict[str, float] = {}
        self._token_alpha_state: dict[str, float] = {}
        self._cluster_nodes: dict[str, NodePath] = {}
        self._cluster_ship_nodes: dict[str, list[NodePath]] = {}
        self._cluster_ship_sway_profiles = _build_cluster_ship_sway_profiles()
        self._cluster_ship_sway_restored: dict[str, bool] = {}
        self._cluster_ship_visible_masks: dict[str, tuple[bool, ...]] = {}
        self._cluster_visibility_state: dict[str, bool] = {}
        self._cluster_alpha_state: dict[str, float] = {}
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
        self._playback_tps = 2.0
        self._playback_active = True
        self._cluster_sway_enabled = False
        self._last_fire_link_signature: tuple[int, int, float, int, float] | None = None
        if len(TOKEN_ALPHA_BY_LEVEL) != len(CLUSTER_ALPHA_BY_LEVEL):
            raise ValueError("TOKEN_ALPHA_BY_LEVEL and CLUSTER_ALPHA_BY_LEVEL must have identical lengths.")
        if len(TOKEN_ALPHA_BY_LEVEL) != len(DUAL_LAYER_DISTANCE_BY_LEVEL):
            raise ValueError("alpha profiles and DUAL_LAYER_DISTANCE_BY_LEVEL must have identical lengths.")
        if len(DUAL_LAYER_DISTANCE_BY_LEVEL) != 5:
            raise ValueError(f"DUAL_LAYER_DISTANCE_BY_LEVEL must define exactly 5 levels; got {len(DUAL_LAYER_DISTANCE_BY_LEVEL)}.")
        self._dual_layer_distances = tuple(float(distance) for distance in DUAL_LAYER_DISTANCE_BY_LEVEL)
        if any(distance <= 0.0 for distance in self._dual_layer_distances):
            raise ValueError(f"DUAL_LAYER_DISTANCE_BY_LEVEL must contain only positive distances; got {self._dual_layer_distances!r}.")
        if any(
            self._dual_layer_distances[index] < self._dual_layer_distances[index - 1]
            for index in range(1, len(self._dual_layer_distances))
        ):
            raise ValueError(f"DUAL_LAYER_DISTANCE_BY_LEVEL must be non-decreasing; got {self._dual_layer_distances!r}.")
        self._sync_objective_marker()

    # -----------------------------------------------------
    # B. viewer overlay / fire-link / halo support
    # -----------------------------------------------------
    def _build_fleet_halo_baselines(self) -> dict[str, tuple[float, float]]:
        if not self._replay.frames:
            return {}
        frame = self._replay.frames[0]
        baselines: dict[str, tuple[float, float]] = {}
        for fleet_id, summary in frame.fleet_body_summary.items():
            if not isinstance(summary, dict):
                continue
            max_radius = float(summary["max_radius"])
            total_hp = float(summary["alive_total_hp"])
            if max_radius > 1e-9 and total_hp > 1e-9:
                baselines[str(fleet_id)] = (float(max_radius), float(total_hp))
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

    def set_playback_tps(self, playback_tps: float) -> None:
        normalized_tps = max(1e-6, float(playback_tps))
        if abs(normalized_tps - self._playback_tps) > 1e-9:
            self._playback_tps = normalized_tps
            self._last_fire_link_signature = None

    def set_playback_active(self, playback_active: bool) -> None:
        self._playback_active = bool(playback_active)

    def set_cluster_sway_enabled(self, cluster_sway_enabled: bool) -> None:
        self._cluster_sway_enabled = bool(cluster_sway_enabled)

    def set_replay(self, replay: ReplayBundle) -> None:
        # App-facing replay swap seam: refresh renderer-owned carriers without
        # exposing renderer-private storage to the viewer host.
        self._replay = replay
        self._fleet_halo_baselines = self._build_fleet_halo_baselines()
        self._fleet_halo_state = {}
        self._current_frame = None
        self._next_fire_link_frame = None
        self._fire_link_position_alpha = 0.0
        self._last_fire_link_signature = None
        self._sync_objective_marker()

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
    def cluster_sway_enabled(self) -> bool:
        return bool(self._cluster_sway_enabled)

    @property
    def fleet_halo_state(self) -> dict[str, dict[str, float]]:
        return {fleet_id: dict(state) for fleet_id, state in self._fleet_halo_state.items()}

    def _current_cluster_sway_seconds(self) -> float:
        if self._current_frame is None:
            return 0.0
        base_seconds = (float(self._current_frame.tick) + float(self._fire_link_pulse_phase)) / max(1e-6, float(self._playback_tps))
        return float(base_seconds) * CLUSTER_SWAY_CLOCK_SCALE

    def _cluster_sway_active(self) -> bool:
        return bool(
            self._cluster_sway_enabled
            and self._playback_active
            and self._playback_level_index <= CLUSTER_SWAY_MAX_ENABLED_GEAR_INDEX
        )

    def _cluster_ship_sway_offsets(
        self,
        sway_profile: dict[str, float],
        *,
        sin_time: float,
        cos_time: float,
    ) -> tuple[float, float, float]:
        x_value = float(sway_profile["base_x"]) + (
            CLUSTER_SWAY_AMPLITUDE_X
            * ((float(sin_time) * float(sway_profile["cos_x_phase"])) + (float(cos_time) * float(sway_profile["sin_x_phase"])))
        )
        y_value = float(sway_profile["base_y"]) + (
            CLUSTER_SWAY_AMPLITUDE_Y
            * ((float(sin_time) * float(sway_profile["cos_y_phase"])) + (float(cos_time) * float(sway_profile["sin_y_phase"])))
        )
        z_value = float(sway_profile["base_z"]) + (
            CLUSTER_SWAY_AMPLITUDE_Z
            * ((float(sin_time) * float(sway_profile["cos_z_phase"])) + (float(cos_time) * float(sway_profile["sin_z_phase"])))
        )
        return (x_value, y_value, z_value)

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
        token_np.setColor(float(rgba[0]), float(rgba[1]), float(rgba[2]), float(TOKEN_ALPHA_BY_LEVEL[-1]))
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
        level_distances = self._dual_layer_distances
        cluster_sway_active = self._cluster_sway_active()
        sway_sin_time = 0.0
        sway_cos_time = 1.0
        if cluster_sway_active:
            sway_time_seconds = self._current_cluster_sway_seconds()
            sway_sin_time = math.sin(2.0 * math.pi * CLUSTER_SWAY_FREQUENCY * sway_time_seconds)
            sway_cos_time = math.cos(2.0 * math.pi * CLUSTER_SWAY_FREQUENCY * sway_time_seconds)
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
            if distance <= level_distances[0]:
                outer_alpha = float(TOKEN_ALPHA_BY_LEVEL[0])
                cluster_alpha = float(CLUSTER_ALPHA_BY_LEVEL[0])
            else:
                outer_alpha = float(TOKEN_ALPHA_BY_LEVEL[-1])
                cluster_alpha = float(CLUSTER_ALPHA_BY_LEVEL[-1])
                for level_index in range(1, len(level_distances)):
                    if distance <= level_distances[level_index]:
                        blend = _smoothstep(level_distances[level_index - 1], level_distances[level_index], distance)
                        outer_alpha = _lerp(
                            float(TOKEN_ALPHA_BY_LEVEL[level_index - 1]),
                            float(TOKEN_ALPHA_BY_LEVEL[level_index]),
                            blend,
                        )
                        cluster_alpha = _lerp(
                            float(CLUSTER_ALPHA_BY_LEVEL[level_index - 1]),
                            float(CLUSTER_ALPHA_BY_LEVEL[level_index]),
                            blend,
                        )
                        break
            token_alpha_scale = 1.0
            if float(TOKEN_ALPHA_BY_LEVEL[-1]) > 1e-9:
                token_alpha_scale = outer_alpha / float(TOKEN_ALPHA_BY_LEVEL[-1])
            last_token_alpha = self._token_alpha_state.get(node_key)
            if last_token_alpha is None or abs(float(last_token_alpha) - float(token_alpha_scale)) > 1e-6:
                token_np.setColorScale(1.0, 1.0, 1.0, token_alpha_scale)
                self._token_alpha_state[node_key] = float(token_alpha_scale)
            if cluster_alpha > 1e-4:
                if not self._cluster_visibility_state.get(node_key, False):
                    cluster_np.show()
                    self._cluster_visibility_state[node_key] = True
                last_cluster_alpha = self._cluster_alpha_state.get(node_key)
                if last_cluster_alpha is None or abs(float(last_cluster_alpha) - float(cluster_alpha)) > 1e-6:
                    cluster_np.setColorScale(1.0, 1.0, 1.0, cluster_alpha)
                    self._cluster_alpha_state[node_key] = float(cluster_alpha)
                ship_nodes = self._cluster_ship_nodes.get(node_key, ())
                ship_sway_profiles = self._cluster_ship_sway_profiles
                if not cluster_sway_active:
                    if self._cluster_ship_sway_restored.get(node_key, True):
                        continue
                    for ship_index, ship_np in enumerate(ship_nodes):
                        if ship_np.isHidden():
                            continue
                        ship_profile = ship_sway_profiles[ship_index]
                        ship_np.setPos(
                            float(ship_profile["base_x"]),
                            float(ship_profile["base_y"]),
                            float(ship_profile["base_z"]),
                        )
                    self._cluster_ship_sway_restored[node_key] = True
                    continue
                self._cluster_ship_sway_restored[node_key] = False
                for ship_index, ship_np in enumerate(ship_nodes):
                    if ship_np.isHidden():
                        continue
                    ship_offset = self._cluster_ship_sway_offsets(
                        ship_sway_profiles[ship_index],
                        sin_time=sway_sin_time,
                        cos_time=sway_cos_time,
                    )
                    ship_np.setPos(float(ship_offset[0]), float(ship_offset[1]), float(ship_offset[2]))
            else:
                if self._cluster_visibility_state.get(node_key, True):
                    cluster_np.hide()
                    self._cluster_visibility_state[node_key] = False
                self._cluster_alpha_state.pop(node_key, None)
        if self._current_frame is not None:
            should_show_fire_links = bool(min_unit_distance is not None and min_unit_distance <= level_distances[-1])
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

    def sync_fleet_halos(
        self,
        frame: ViewerFrame,
        *,
        next_frame: ViewerFrame | None = None,
        position_alpha: float = 0.0,
        tick_offset: float = 0.0,
    ) -> None:
        self._fleet_halo_state = {}
        active_fleet_ids: set[str] = set()
        for fleet_id, summary in frame.fleet_body_summary.items():
            if not isinstance(summary, dict):
                continue
            centroid_x = float(summary["centroid_x"])
            centroid_y = float(summary["centroid_y"])
            current_total_hp = float(summary["alive_total_hp"])
            blend = max(0.0, min(1.0, float(position_alpha)))
            if next_frame is not None and blend > 1e-6:
                next_summary = next_frame.fleet_body_summary.get(str(fleet_id))
                if isinstance(next_summary, dict):
                    centroid_x = ((1.0 - blend) * centroid_x) + (blend * float(next_summary["centroid_x"]))
                    centroid_y = ((1.0 - blend) * centroid_y) + (blend * float(next_summary["centroid_y"]))
                    current_total_hp = ((1.0 - blend) * current_total_hp) + (blend * float(next_summary["alive_total_hp"]))
            if current_total_hp <= 1e-9:
                continue
            baseline = self._fleet_halo_baselines.get(fleet_id)
            if baseline is None:
                baseline_radius = float(summary["max_radius"])
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
            playback_seconds = (float(frame.tick) + float(tick_offset)) / max(1e-6, float(self._playback_tps))
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

    # -----------------------------------------------------
    # C. per-frame unit transforms
    # -----------------------------------------------------
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
                self._token_scale_state.pop(node_key, None)
                self._token_alpha_state.pop(node_key, None)
                self._cluster_nodes[node_key] = cluster_np
                ship_nodes: list[NodePath] = []
                for ship_index in range(len(CLUSTER_LAYOUT_OFFSETS)):
                    ship_np = node.find(f"**/cluster_ship_{ship_index}")
                    if ship_np.isEmpty():
                        raise RuntimeError(f"unit cluster ship {ship_index} is missing for {node_key!r}")
                    ship_nodes.append(ship_np)
                self._cluster_ship_nodes[node_key] = ship_nodes
                self._cluster_ship_sway_restored[node_key] = True
                self._cluster_ship_visible_masks[node_key] = tuple(False for _ in ship_nodes)
                self._cluster_visibility_state.pop(node_key, None)
                self._cluster_alpha_state.pop(node_key, None)
            bucket = _hp_bucket(unit.hit_points, unit.max_hit_points)
            scale = HP_BUCKET_SCALES[bucket]
            last_token_scale = self._token_scale_state.get(node_key)
            if last_token_scale is None or abs(float(last_token_scale) - float(scale)) > 1e-6:
                self._token_nodes[node_key].setScale(scale)
                self._token_scale_state[node_key] = float(scale)
            visible_indices = CLUSTER_VISIBLE_INDICES_BY_BUCKET[bucket]
            visibility_mask_tuple = tuple(
                ship_index in visible_indices
                for ship_index in range(len(self._cluster_ship_nodes[node_key]))
            )
            if visibility_mask_tuple != self._cluster_ship_visible_masks.get(node_key):
                for ship_index, ship_np in enumerate(self._cluster_ship_nodes[node_key]):
                    if visibility_mask_tuple[ship_index]:
                        ship_np.show()
                    else:
                        ship_np.hide()
                self._cluster_ship_visible_masks[node_key] = visibility_mask_tuple
                self._cluster_ship_sway_restored[node_key] = False
            node.setPos(unit.x, unit.y, unit.z)
            node.setH(_heading_to_h(unit.heading_x, unit.heading_y))
            active_keys.add(node_key)

        stale_keys = [key for key in self._unit_nodes if key not in active_keys]
        for stale_key in stale_keys:
            self._unit_nodes[stale_key].removeNode()
            del self._unit_nodes[stale_key]
            self._token_nodes.pop(stale_key, None)
            self._token_scale_state.pop(stale_key, None)
            self._token_alpha_state.pop(stale_key, None)
            self._cluster_nodes.pop(stale_key, None)
            self._cluster_ship_nodes.pop(stale_key, None)
            self._cluster_ship_sway_restored.pop(stale_key, None)
            self._cluster_ship_visible_masks.pop(stale_key, None)
            self._cluster_visibility_state.pop(stale_key, None)
            self._cluster_alpha_state.pop(stale_key, None)

        self.sync_fleet_halos(frame)

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
        playback_seconds = (float(frame.tick) + float(self._fire_link_pulse_phase)) / max(1e-6, float(self._playback_tps))
        pulse_shift = (playback_seconds * FIRE_LINK_BASE_SPEED_PER_SECOND) % pulse_spacing
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
