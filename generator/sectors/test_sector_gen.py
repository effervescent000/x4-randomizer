from typing import cast
from config.models import Config
from generator.sectors.generator import SectorGenerator
from generator.sectors.models import Cluster, Galaxy


def test_basic_sector_gen() -> None:
    """Can we generate a single cluster with 1-3 sectors without problems?"""
    config = Config(sector_count=1)
    galaxy = Galaxy()
    generator = SectorGenerator(config, galaxy)
    generator.generate()
    assert galaxy.cluster_count == 1
    cluster = cast(Cluster, galaxy.clusters.get(0))
    assert cluster.position.y == 0
    assert 100_000_000 > abs(cluster.position.x) > 10_000

    assert 4 > galaxy.sector_count >= 1
