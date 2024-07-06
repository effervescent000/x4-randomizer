from generator.sectors.models import Position
from testing.shapes import DEFAULT_DISTANCE_NEGATIVE, sector_factory


def test_tile_snapping() -> None:
    target_sectors = [
        sector_factory(
            1,
            position=Position(DEFAULT_DISTANCE_NEGATIVE, 0, DEFAULT_DISTANCE_NEGATIVE),
        )
    ]
    new_sector = sector_factory(id=1000, position=Position(50_000_000, 0, 50_000_000))

    new_sector.snap_hex_to_targets(target_sectors)
    target_points = set(target_sectors[0].hex._make_points())
    adjusted_points = set(new_sector.hex._make_points())

    assert 1 >= len(
        list(target_points & adjusted_points)
    ), "Should share at least one vertex"
    assert (
        len(list(target_points & adjusted_points)) <= 2
    ), "Should share no more than two vertices"
