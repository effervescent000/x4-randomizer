from typing import NamedTuple

from pydantic import BaseModel


class Position(NamedTuple):
    x: int
    y: int
    z: int

    # @property
    # def as_string(self) -> str:
    #     return f"{self.x}"


class LocationInSector(BaseModel):
    sector: "Sector"
    position: Position


class Connector(BaseModel):
    entry_point: LocationInSector
    exit_point: LocationInSector
    one_way: bool = True


class InterClusterConnector(Connector):
    """Jump gates. These go between clusters, but exist in sectors."""

    one_way: bool = False
    entry_cluster: "Cluster"
    exit_cluster: "Cluster"

    @property
    def id(self) -> str:
        return f"{self.entry_cluster.id}-{self.exit_cluster.id}"


class InterSectorConnector(Connector):
    """Accelerators and superhighways."""

    @property
    def id(self) -> str:
        return f"{self.entry_point.sector.id}-{self.exit_point.sector.id}"


class Zone(BaseModel):
    id: int
    # there's a TON of stuff here but i feel like a lot of it is determined by gameplay
    # so I'm just going to include a few things
    # stations: ... not required, should probably only be used for hard-coded stations like wharfs/shipyards/trade centers
    # sh: ... not required, sh stands for `sector_highway`
    # gates: ... not required


class Sector(BaseModel):
    id: int
    name: str | None = None
    zones: dict[int, Zone] = {}
    position: Position
    # parent: "Cluster" | None = None
    # lensflares: ... not required
    # lights: ... not required
    # zonehighways: ... not required
    # rendereffects
    # stardust
    # adjacentregions


class Cluster(BaseModel):
    id: int
    name: str | None = None
    sectors: dict[int, Sector] = {}
    position: Position
    inter_sector_highways: list[InterSectorConnector] = []
    # areas: ... not required
    # regions: ... not required
    # content: ...
    # planets: ... not required
    # suns: ... not required
    # nebulas: ... not required
    # rendereffects: ...
    # lensflares: ...

    @property
    def sector_count(self) -> int:
        return len(self.sectors.keys())

    @property
    def sector_list(self) -> list[Sector]:
        return list(self.sectors.values())

    def get_sector_siblings(self, target: Sector | None = None) -> list[Sector]:
        sectors_copy = {**self.sectors}
        if target is not None:
            sectors_copy.pop(target.id)
        return list(sectors_copy.values())


class Galaxy(BaseModel):
    clusters: dict[int, Cluster] = {}
    highways: list[InterClusterConnector] = []

    @property
    def cluster_count(self) -> int:
        return len(self.clusters.keys())

    @property
    def sector_count(self) -> int:
        return sum(x.sector_count for x in self.clusters.values())

    def get_cluster_siblings(self, target: Cluster | None = None) -> list[Cluster]:
        clusters_copy = {**self.clusters}
        if target is not None:
            clusters_copy.pop(target.id)
        return list(clusters_copy.values())
