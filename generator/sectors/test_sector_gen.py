import pytest


from config.models import Config
from generator.sectors.generator import SectorGenerator
from generator.sectors.models import Cluster, Galaxy, Position, Sector
from testing.shapes import (
    hex_factory,
)


def test_hex_generation() -> None:
    config = Config(sector_count=75)
    galaxy = Galaxy()
    gen = SectorGenerator(config, galaxy)
    gen._generate_hex_grid()

    radius = 250_000

    assert len(gen.hex_grid) >= 200, "Hex grid should be populated"
    assert all(
        [
            any(
                [
                    hex_factory(
                        hex.center.x + 0,
                        hex.center.z + radius,
                    )
                    in gen.hex_grid,
                    hex_factory(hex.center.x + 0, hex.center.z - radius)
                    in gen.hex_grid,
                ]
            )
            for hex in gen.hex_grid
        ]
    ), "Every hex has at least one adjacent neighbor"


@pytest.mark.parametrize("_execution_number", range(5))
def test_basic_sector_gen(_execution_number: int) -> None:
    """Can we generate a single cluster with 1-3 sectors without problems?"""
    config = Config(sector_count=1)
    galaxy = Galaxy()
    generator = SectorGenerator(config, galaxy)
    generator._generate_hex_grid()
    generator._generate_clusters_and_sectors()
    assert galaxy.cluster_count == 1, "Should only generate a single cluster"
    assert (
        4 > galaxy.sector_count >= 1
    ), "Should generate an appropriate number of sectors"


@pytest.mark.parametrize("_execution_number", range(5))
def test_sector_highway_gen_simple(_execution_number: int) -> None:
    """Generate intra-cluster highways in a basic two-sector system."""
    fake_cluster = Cluster(id=1)
    sectors = {
        1: Sector(
            id=1, position=Position(-20_000, 0, -20_000), cluster_id=fake_cluster.id
        ),
        2: Sector(
            id=2, position=Position(20_000, 0, 20_000), cluster_id=fake_cluster.id
        ),
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


# def test_cluster_highway_gen_simple() -> None:
#     """Generate inter-cluster highways between two clusters, with a single sector each."""
#     config = Config(sector_count=1)
#     clusters = [
#         Cluster(
#             id=1,
#             position=Position(DEFAULT_DISTANCE_NEGATIVE, 0, DEFAULT_DISTANCE_NEGATIVE),
#             sectors={1: sector_factory(id=1)},
#         ),
#         Cluster(
#             id=2,
#             position=Position(DEFAULT_DISTANCE, 0, DEFAULT_DISTANCE),
#             sectors={1: sector_factory(id=1)},
#         ),
#     ]
#     clusters = {x.id: x for x in clusters}
#     galaxy = Galaxy(clusters=clusters)

#     gen = SectorGenerator(config, galaxy=galaxy)
#     gen._generate_cluster_highways()
#     galaxy.highways
#     assert len(galaxy.highways) == 1


# @pytest.mark.parametrize("_execution_number", range(5))
# def test_cluster_highway_gen_multiple_clusters(_execution_number: int) -> None:
#     """Generate highways with a larger group of clusters."""
#     config = Config(sector_count=1)
#     clusters = [
#         Cluster(
#             id=1,
#             position=Position(DEFAULT_DISTANCE_NEGATIVE, 0, DEFAULT_DISTANCE_NEGATIVE),
#             sectors={1: sector_factory(id=1)},
#         ),
#         Cluster(
#             id=2,
#             position=Position(DEFAULT_DISTANCE, 0, DEFAULT_DISTANCE),
#             sectors={1: sector_factory(id=1)},
#         ),
#         Cluster(
#             id=3,
#             position=Position(DEFAULT_DISTANCE, 0, DEFAULT_DISTANCE_NEGATIVE),
#             sectors={1: sector_factory(id=1)},
#         ),
#         Cluster(
#             id=4,
#             position=Position(DEFAULT_DISTANCE_NEGATIVE, 0, DEFAULT_DISTANCE),
#             sectors={1: sector_factory(id=1)},
#         ),
#     ]
#     clusters = {x.id: x for x in clusters}
#     galaxy = Galaxy(clusters=clusters)

#     gen = SectorGenerator(config, galaxy=galaxy)
#     gen._generate_cluster_highways()
#     assert len(galaxy.highways) > 0, "At least one highway is generated"
#     assert len(galaxy.highways) < 8, "Excessive highways aren't generated"
#     ids = [break_compound_id(x.id) for x in galaxy.highways]
#     assert all(
#         [any([i in id for id in ids]) for i in range(1, 5)]
#     ), "All clusters have at least one highway"
