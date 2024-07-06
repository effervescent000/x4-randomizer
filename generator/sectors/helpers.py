import math
import random

from generator.sectors.models import Cluster, LocationInSector, Position, Sector


def get_default_position() -> Position:
    return Position(0, 0, 0)


def distance_between_points(a: Position, b: Position) -> float:
    return math.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)


def get_random_with_multiplier(
    multiplier: int, upper: int = 9_999, lower: int = -9_999
) -> int:
    return random.randint(lower, upper) * multiplier


def break_compound_id(compound_id: str) -> tuple[int, int]:
    a, b = compound_id.split("-")
    return (int(a), int(b))


def get_relative_bounds(
    limit: int, main_pos: float, target_pos: float
) -> tuple[int, int]:
    if main_pos > target_pos:
        return (0, limit)
    if main_pos < target_pos:
        return (limit * -1, 0)
    bound = round(0.2 * limit)
    return (bound * -1, bound)


def get_position_in_quadrant(x: int, z: int, limit: int) -> Position:
    limit_x = limit if x > 1 else limit * -1
    limit_z = limit if z > 1 else limit * -1
    return Position(
        random.randint(*sorted([x, limit_x])), 0, random.randint(*sorted([z, limit_z]))
    )


def get_direction_for_main(main: Position, partner: Position) -> int:
    if main.x > partner.x:
        return 1
    if main.x < partner.x:
        return -1
    return 0


def get_directional_quadrant_for_main(
    main: Position, partner: Position
) -> tuple[int, int]:
    x = get_direction_for_main(main, partner)
    z = get_direction_for_main(main, partner)
    return x, z


def get_directional_position_from_pair_single(
    main: Position, partner: Position, limit: int
) -> Position:
    min_x, max_x = get_relative_bounds(limit, main.x, partner.x)
    min_z, max_z = get_relative_bounds(limit, main.z, partner.z)
    return Position(random.randint(min_x, max_x), 0, random.randint(min_z, max_z))


def get_directional_position_from_pair_both(
    main: Position, partner: Position, limit: int
) -> tuple[Position, Position]:
    return (
        get_directional_position_from_pair_single(main, partner, limit),
        get_directional_position_from_pair_single(partner, main, limit),
    )


def check_for_connection(a: int, b: int, compound_pairs: list[str]) -> bool:
    for pair in compound_pairs:
        ids = break_compound_id(pair)
        if a in ids and b in ids:
            return True
    return False


def count_connections(target: int, compound_pairs: list[str]) -> int:
    ids = [break_compound_id(pair) for pair in compound_pairs]
    matches = [x for x in ids if target in x]
    return len(matches)


def get_closest_sector_to_target_in_cluster(a: Cluster, b: Cluster) -> Sector:
    if a.sector_count == 1:
        return a.sector_list[0]
    target_loc = get_directional_position_from_pair_single(
        a.position, b.position, 20_000
    )
    sectors_by_distance = sorted(
        a.sector_list, key=lambda sec: distance_between_points(sec.position, target_loc)
    )
    return sectors_by_distance[0]


def get_location_in_sector_from_cluster_single(
    a: Cluster, b: Cluster
) -> LocationInSector:
    sector = get_closest_sector_to_target_in_cluster(a, b)
    quadrant = get_directional_quadrant_for_main(a.position, b.position)
    pos = get_position_in_quadrant(x=quadrant[0], z=quadrant[1], limit=20_000)
    return LocationInSector(sector=sector, position=pos)


def get_location_in_sector_from_cluster_both(
    a: Cluster, b: Cluster
) -> tuple[LocationInSector, LocationInSector]:
    return (
        get_location_in_sector_from_cluster_single(a, b),
        get_location_in_sector_from_cluster_single(b, a),
    )


def convert_km_to_m_galaxy_scale(distance_km: int) -> int:
    # this is here because things on the galactic/cluster scale are very large
    # and need an extra level of multiplier to work. i think? maybe? we'll see
    return distance_km * 100 * 1_000
