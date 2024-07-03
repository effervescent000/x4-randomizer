import math
import random
from generator.sectors.models import Position


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


def get_relative_bounds(limit: int, main_pos: int, target_pos: int) -> tuple[int, int]:
    if main_pos > target_pos:
        return (0, limit)
    if main_pos < target_pos:
        return (limit * -1, 0)
    bound = round(0.2 * limit)
    return (bound * -1, bound)


def get_connector_placement_single(
    main: Position, partner: Position, limit: int
) -> Position:
    min_x, max_x = get_relative_bounds(limit, main.x, partner.x)
    min_z, max_z = get_relative_bounds(limit, main.z, partner.z)
    return Position(random.randint(min_x, max_x), 0, random.randint(min_z, max_z))


def get_connector_placement_both(
    main: Position, partner: Position, limit: int
) -> tuple[Position, Position]:
    return (
        get_connector_placement_single(main, partner, limit),
        get_connector_placement_single(partner, main, limit),
    )
