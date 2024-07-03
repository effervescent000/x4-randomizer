from generator.sectors.models import Cluster, Position, Sector


def sector_factory(
    id: int, name: str | None = None, position: Position | None = None
) -> Sector:
    return Sector(id=id, name=name, position=position or Position(0, 0, 0))


def cluster_factory(
    id=id,
    name: str | None = None,
    position: Position | None = None,
    sectors: dict[int, Sector] | None = None,
) -> Cluster:
    return Cluster(
        id=id, name=name, position=position or Position(0, 0, 0), sectors=sectors or {}
    )
