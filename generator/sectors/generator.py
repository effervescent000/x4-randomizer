import random

from config.models import Config
from generator.sectors.models import Cluster, Galaxy, Position, Sector


class SectorGenerator:
    def __init__(self, config: Config, galaxy: Galaxy) -> None:
        self.config = config
        self.sector_count = 0
        self.galaxy = galaxy

    def _get_safe_position(self) -> Position:
        # TODO for now we are just returning random numbers, but eventually
        # we'll want to ensure no overlaps
        y = 0
        x = random.randint(-9_999, 9_999) * 10_000
        z = random.randint(-9_999, 9_999) * 10_000
        return Position(x, y, z)

    def generate(self) -> None:
        """Generate clusters with 1-3 sectors each, until we reach the sector cap."""
        while self.sector_count < self.config.sector_count:
            cluster_id = self.galaxy.cluster_count
            cluster = Cluster(
                id=cluster_id,
                name="Testing",
                position=self._get_safe_position(),
            )
            self.galaxy.clusters[cluster_id] = cluster
            for i in range(0, random.randint(1, 3)):
                sector = Sector(
                    id=i, name="Testing", position=self._get_safe_position()
                )
                cluster.sectors[i] = sector
                self.sector_count += 1
