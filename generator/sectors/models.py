from typing import NamedTuple
from pydantic import BaseModel


class Position(NamedTuple):
    x: int
    y: int
    z: int

    # @property
    # def as_string(self) -> str:
    #     return f"{self.x}"


class Zone(BaseModel):
    id: int
    # there's a TON of stuff here but i feel like a lot of it is determined by gameplay
    # so I'm just going to include a few things
    # stations: ... not required, should probably only be used for hard-coded stations like wharfs/shipyards/trade centers
    # sh: ... not required, sh stands for `sector_highway`
    # gates: ... not required


class Sector(BaseModel):
    id: int
    name: str
    zones: dict[int, Zone] = {}
    position: Position
    # lensflares: ... not required
    # lights: ... not required
    # zonehighways: ... not required
    # rendereffects
    # stardust
    # adjacentregions


class Cluster(BaseModel):
    id: int
    name: str
    sectors: dict[int, Sector] = {}
    position: Position
    # areas: ... not required
    # regions: ... not required
    # content: ...
    # sechighways: ... not required
    # planets: ... not required
    # suns: ... not required
    # nebulas: ... not required
    # rendereffects: ...
    # lensflares: ...

    @property
    def sector_count(self) -> int:
        return len(self.sectors.keys())


class Galaxy(BaseModel):
    clusters: dict[int, Cluster] = {}

    @property
    def cluster_count(self) -> int:
        return len(self.clusters.keys())

    @property
    def sector_count(self) -> int:
        return sum(x.sector_count for x in self.clusters.values())
