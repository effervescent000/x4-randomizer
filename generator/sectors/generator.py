import random

from config.models import Config
from generator.sectors.helpers import (
    break_compound_id,
    distance_between_points,
    get_connector_placement_both,
    get_random_with_multiplier,
)
from generator.sectors.models import (
    Cluster,
    Galaxy,
    InterSectorConnector,
    LocationInSector,
    Position,
    Sector,
)


class SectorGenerator:
    def __init__(self, config: Config, galaxy: Galaxy) -> None:
        self.config = config
        self.sector_count = 0
        self.galaxy = galaxy

    def generate(self) -> None:
        """Generate clusters with 1-3 sectors each, until we reach the sector cap."""
        self._generate_sectors()
        # generate jump gates
        self._generate_sector_highways()

    def _generate_sector_highways(self) -> None:
        for cluster in self.galaxy.clusters.values():
            if len(cluster.sectors) > 1:
                for sector in cluster.sectors.values():
                    # if the target cluster has no connections, connect it to one of its siblings
                    if not any(
                        [
                            sector.id in break_compound_id(x.id)
                            for x in cluster.inter_sector_highways
                        ]
                    ):
                        max_gate_distance = 800_000
                        partner = random.choice(cluster.get_sector_siblings(sector))
                        main_gate_pos, partner_gate_pos = get_connector_placement_both(
                            sector.position, partner.position, max_gate_distance
                        )
                        highway = InterSectorConnector(
                            entry_point=LocationInSector(
                                sector=sector, position=main_gate_pos
                            ),
                            exit_point=LocationInSector(
                                sector=partner, position=partner_gate_pos
                            ),
                        )
                        cluster.inter_sector_highways.append(highway)

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

    def _generate_sectors(self) -> None:
        while self.sector_count < self.config.sector_count:
            cluster_id = self.galaxy.cluster_count
            cluster = Cluster(
                id=cluster_id,
                position=self._get_cluster_position(),
            )
            self.galaxy.clusters[cluster_id] = cluster

            max_sectors = random.randint(1, 3)
            if max_sectors == 1:
                sector = Sector(id=0, position=Position(0, 0, 0), parent=cluster)
                cluster.sectors[0] = sector
                self.sector_count += 1
            else:
                for i in range(1, max_sectors):
                    sector = Sector(
                        id=i,
                        position=self._get_sector_position(cluster),
                        parent=cluster,
                    )
                    cluster.sectors[i] = sector
                    self.sector_count += 1
