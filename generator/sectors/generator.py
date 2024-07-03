import math
import random

from config.models import Config
from generator.sectors.models import Cluster, Galaxy, Position, Sector


def distance_between_points(a: Position, b: Position) -> float:
    return math.sqrt((b.x - a.x) ** 2 + (b.y - a.y) ** 2)


def get_random_with_multiplier(
    multiplier: int, upper: int = 9_999, lower: int = -9_999
) -> int:
    return random.randint(lower, upper) * multiplier


class SectorGenerator:
    def __init__(self, config: Config, galaxy: Galaxy) -> None:
        self.config = config
        self.sector_count = 0
        self.galaxy = galaxy

    def _get_cluster_position(self) -> Position:
        multiplier = 10_000
        y = 0
        x = get_random_with_multiplier(multiplier)
        z = get_random_with_multiplier(multiplier)
        # if cluster count is 0 it means this is the first one (which hasn't been added to the galaxy yet),
        # so we dont have to worry about overlaps
        if self.galaxy.cluster_count == 0:
            return Position(x, y, z)

        siblings = self.galaxy.get_cluster_siblings()
        while True:
            maybe_position = Position(x, y, z)
            if not any(
                [
                    distance_between_points(sib.position, maybe_position) < 50_000
                    for sib in siblings
                ]
            ):
                return maybe_position
            x = get_random_with_multiplier(multiplier)
            z = get_random_with_multiplier(multiplier)

    def _get_sector_position(self, cluster: Cluster) -> Position:
        multiplier = 100
        y = 0
        x = get_random_with_multiplier(multiplier)
        z = get_random_with_multiplier(multiplier)
        if cluster.sector_count == 0:
            return Position(x, y, z)

        siblings = cluster.get_sector_siblings()
        while True:
            maybe_position = Position(x, y, z)
            if not any(
                [
                    distance_between_points(sib.position, maybe_position)
                    for sib in siblings
                ]
            ):
                return maybe_position
            x = get_random_with_multiplier(multiplier)
            z = get_random_with_multiplier(multiplier)

    def generate(self) -> None:
        """Generate clusters with 1-3 sectors each, until we reach the sector cap."""
        while self.sector_count < self.config.sector_count:
            cluster_id = self.galaxy.cluster_count
            cluster = Cluster(
                id=cluster_id,
                position=self._get_cluster_position(),
            )
            self.galaxy.clusters[cluster_id] = cluster

            max_sectors = random.randint(1, 3)
            if max_sectors == 1:
                sector = Sector(id=0, position=Position(0, 0, 0))
                cluster.sectors[0] = sector
                self.sector_count += 1
            else:
                for i in range(1, max_sectors):
                    sector = Sector(
                        id=i,
                        position=self._get_sector_position(cluster),
                    )
                    cluster.sectors[i] = sector
                    self.sector_count += 1
