import math
from typing import NamedTuple

# from matplotlib.patches import RegularPolygon
from shapely import Polygon, intersects
from pydantic import BaseModel, ConfigDict


class Position(NamedTuple):
    x: float
    y: float
    z: float

    @property
    def string_dict(self) -> dict[str, str]:
        return {"x": str(self.x), "y": str(self.y), "z": str(self.z)}


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


class Sector:
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
        self.id = id
        self.name = name
        self.cluster_id = cluster_id

        self.hex = Hex(center=position, radius=radius)

    @property
    def compound_id(self) -> str:
        return f"{self.cluster_id}-{self.id}"

    @property
    def label(self) -> str:
        return f"Cluster_{self.cluster_id:02}_Sector{self.id:03}"

    @property
    def position(self) -> Position:
        return self.hex.center


class Cluster:
    # position: Position
    # radius: int = 50_000
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
        self.id = id
        self.name = name
        self.sectors = sectors
        self.inter_sector_highways = inter_sector_highways

        self.hex = Hex(center=position, radius=radius)

    @property
    def label(self) -> str:
        return f"Cluster_{self.id:02}"

    @property
    def sector_count(self) -> int:
        return len(self.sectors.keys())

    @property
    def sector_list(self) -> list[Sector]:
        return list(self.sectors.values())

    @property
    def position(self) -> Position:
        return self.hex.center

    def get_sector_siblings(self, target: Sector | None = None) -> list[Sector]:
        sectors_copy = {**self.sectors}
        if target is not None:
            sectors_copy.pop(target.id)
        return list(sectors_copy.values())


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
