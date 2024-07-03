from typing import cast

import pytest

from config.models import Config
from generator.sectors.generator import SectorGenerator
from generator.sectors.helpers import get_default_position
from generator.sectors.models import Cluster, Galaxy, Position, Sector


@pytest.mark.parametrize("_execution_number", range(5))
def test_basic_sector_gen(_execution_number: int) -> None:
    """Can we generate a single cluster with 1-3 sectors without problems?"""
    config = Config(sector_count=1)
    galaxy = Galaxy()
    generator = SectorGenerator(config, galaxy)
    generator._generate_sectors()
    assert galaxy.cluster_count == 1
    cluster = cast(Cluster, galaxy.clusters.get(0))
    assert cluster.position.y == 0
    assert 100_000_000 > abs(cluster.position.x) > 10_000

    assert 4 > galaxy.sector_count >= 1


@pytest.mark.parametrize("_execution_number", range(5))
def test_sector_highway_gen_simple(_execution_number: int) -> None:
    """Generate intra-cluster highways in a basic two-sector system."""
    fake_cluster = Cluster(id=1, position=get_default_position())
    sectors = {
        1: Sector(id=1, position=Position(-20_000, 0, -20_000), parent=fake_cluster),
        2: Sector(id=1, position=Position(20_000, 0, 20_000), parent=fake_cluster),
    }
    fake_cluster.sectors = sectors
    clusters = {1: fake_cluster}
    config = Config(sector_count=1)

    gen = SectorGenerator(config, galaxy=Galaxy(clusters=clusters))
    gen._generate_sector_highways()
    highways = gen.galaxy.clusters[1].inter_sector_highways
    assert len(highways) == 1
    assert highways[0].entry_point.position.x <= 0
    assert highways[0].entry_point.position.z <= 0
    assert highways[0].exit_point.position.x >= 0
    assert highways[0].exit_point.position.z >= 0
