import math
from typing import NamedTuple, Sequence, cast


from shapely import Polygon, get_x, get_y, intersects, coverage_union_all, snap
from pydantic import BaseModel, ConfigDict


def get_position_from_polygon(poly: Polygon) -> "Position":
    return Position(get_x(poly.centroid), 0, get_y(poly.centroid))


def a(n: float) -> "Position":
    return Position(math.sqrt(3) / 2 * n, 0, 0.5 * n)


def b(n: float) -> "Position":
    return Position(math.sqrt(3) / 2 * n, 0, -0.5 * n)


class Position(NamedTuple):
    x: float
    y: float
    z: float

    @property
    def string_dict(self) -> dict[str, str]:
        return {"x": str(self.x), "y": str(self.y), "z": str(self.z)}

    def __add__(self, other: "Position") -> "Position":
        return Position(self.x + other.x, self.y + other.y, self.z + other.z)

    def __radd__(self, other: "Position") -> "Position":
        return self.__add__(other)

    def __sub__(self, other: "Position") -> "Position":
        return Position(self.x - other.x, self.y - other.y, self.z - other.z)

    def __rsub__(self, other: "Position") -> "Position":
        return Position(other.x - self.x, other.y - self.y, other.z - self.z)

    def __mul__(self, other: "Position | float") -> "Position":
        if isinstance(other, Position):
            return Position(self.x * other.x, self.y * other.y, self.z * other.z)
        return Position(self.x * other, self.y * other, self.z * other)

    def __rmul__(self, other: "Position") -> "Position":
        return self.__mul__(other)


class LocationInSector(BaseModel):
    sector: "Sector"
    position: Position

    model_config = ConfigDict(arbitrary_types_allowed=True)


class Connector(BaseModel):
    entry_point: LocationInSector
    exit_point: LocationInSector
    one_way: bool = True


class InterClusterConnector(Connector):
    """Jump gates. These go between clusters, but exist in sectors."""

    one_way: bool = False
    entry_cluster: "Cluster"
    exit_cluster: "Cluster"

    model_config = ConfigDict(arbitrary_types_allowed=True)

    @property
    def id(self) -> str:
        return f"{self.entry_cluster.id}-{self.exit_cluster.id}"

    @property
    def label(self) -> str:
        return f"ClusterGate{self.entry_cluster.id:03}To{self.exit_cluster.id:03}"


class InterSectorConnector(Connector):
    """Accelerators and superhighways."""

    @property
    def id(self) -> str:
        return f"{self.entry_point.sector.id}-{self.exit_point.sector.id}"


class Zone(BaseModel):
    id: int
    sector_id: str  # this should point to the sector's compound id
    # there's a TON of stuff here but i feel like a lot of it is determined by gameplay
    # so I'm just going to include a few things
    # stations: ... not required, should probably only be used for hard-coded stations like wharfs/shipyards/trade centers
    # sh: ... not required, sh stands for `sector_highway`
    # gates: ... not required


class Hex:
    def __init__(self, center: Position, radius: float = 250_000) -> None:
        self.center = center
        self.radius = radius
        self.shape = Polygon(self._make_points())

    def _make_points(self) -> tuple[tuple[float, float], ...]:
        x_offset = self.radius * math.sin(math.pi / 6)
        z_offset = self.radius * math.sin(math.pi / 3)
        left = (self.center.x - self.radius, self.center.z)
        right = (self.center.x + self.radius, self.center.z)
        points = (
            # starting at bottom left point and circling clockwise
            (left[0] + x_offset, left[1] - z_offset),
            left,
            (left[0] + x_offset, left[1] + z_offset),
            (right[0] - x_offset, right[1] + z_offset),
            right,
            (right[0] - x_offset, right[1] - z_offset),
        )
        points = (*points, points[0])
        return points

    def intersects(self, target: "Hex") -> bool:
        return intersects(self.shape, target.shape)

    def __hash__(self) -> int:
        return hash(f"({self.center.x}, {self.center.z})")

    def __eq__(self, value: object) -> bool:
        return self.center == value

    @property
    def neighbor_positions(self) -> list[Position]:
        return [
            self.center + a(self.radius),
            self.center + b(self.radius),
            self.center + a(self.radius) - b(self.radius),
            self.center + b(self.radius) - a(self.radius),
            self.center + b(self.radius) * -1,
            self.center + a(self.radius) * -1,
        ]

    def __repr__(self) -> str:
        return f"({self.center.x}, {self.center.z})"


class Tile:
    def __init__(
        self, id: int, *, name: str | None = None, position: Position, radius: float
    ) -> None:
        self.id = id
        self.name = name

        self.hex = Hex(center=position, radius=radius)

    @property
    def position(self) -> Position:
        return self.hex.center

    def snap_hex_to_targets(self, targets: Sequence["Tile"]) -> None:
        coverage = coverage_union_all([x.hex.shape for x in targets])
        snapped = snap(self.hex.shape, coverage, tolerance=1)
        self.hex = Hex(
            center=get_position_from_polygon(snapped), radius=self.hex.radius
        )


class Sector(Tile):
    # zones: dict[int, Zone] = {}
    # radius: int = 50_000
    # lensflares: ... not required
    # lights: ... not required
    # rendereffects
    # stardust
    # adjacentregions

    def __init__(
        self,
        id: int,
        *,
        name: str | None = None,
        position: Position,
        cluster_id: int,
        radius: float = 250_000,
    ) -> None:
        super().__init__(id, name=name, position=position, radius=radius)

        self.cluster_id = cluster_id

    @property
    def compound_id(self) -> str:
        return f"{self.cluster_id}-{self.id}"

    @property
    def label(self) -> str:
        return f"Cluster_{self.cluster_id:02}_Sector{self.id:03}"


class Cluster(Tile):
    # areas: ... not required
    # regions: ... not required
    # content: ...
    # planets: ... not required
    # suns: ... not required
    # nebulas: ... not required
    # rendereffects: ...
    # lensflares: ...

    def __init__(
        self,
        id: int,
        *,
        name: str | None = None,
        sectors: dict[int, Sector] = {},
        inter_sector_highways: list[InterSectorConnector] = [],
        position: Position,
        radius: float = 250_000,
    ) -> None:
        super().__init__(id, name=name, position=position, radius=radius)

        self.sectors = sectors
        self.inter_sector_highways = inter_sector_highways

    @property
    def label(self) -> str:
        return f"Cluster_{self.id:02}"

    @property
    def sector_count(self) -> int:
        return len(self.sectors.keys())

    @property
    def sector_list(self) -> list[Sector]:
        return list(self.sectors.values())

    def get_sector_siblings(self, target: Sector | None = None) -> list[Sector]:
        sectors_copy = {**self.sectors}
        if target is not None:
            sectors_copy.pop(target.id)  # type: ignore
        return list(sectors_copy.values())

    def wrap_sectors(self) -> Polygon:
        geometries = [x.hex.shape for x in self.sector_list]
        return cast(Polygon, coverage_union_all(geometries))


class Galaxy:
    clusters: dict[int, Cluster] = {}
    highways: list[InterClusterConnector] = []

    def __init__(
        self,
        *,
        clusters: dict[int, Cluster] = {},
        highways: list[InterClusterConnector] = [],
    ) -> None:
        self.clusters = clusters
        self.highways = highways

    @property
    def cluster_count(self) -> int:
        return len(self.clusters.keys())

    @property
    def cluster_list(self) -> list[Cluster]:
        return list(self.clusters.values())

    @property
    def sector_count(self) -> int:
        return sum(x.sector_count for x in self.clusters.values())

    @property
    def sector_list(self) -> list[Sector]:
        return [
            sector for cluster in self.cluster_list for sector in cluster.sector_list
        ]

    def get_cluster_siblings(self, target: Cluster | None = None) -> list[Cluster]:
        clusters_copy = {**self.clusters}
        if target is not None:
            clusters_copy.pop(target.id)
        return list(clusters_copy.values())
