import random
from typing import cast


from config.models import Config
from generator.sectors.helpers import (
    break_compound_id,
    check_for_connection,
    convert_km_to_m_galaxy_scale,
    count_connections,
    distance_between_points,
    get_directional_position_from_pair_both,
    get_location_in_sector_from_cluster_both,
)
from generator.sectors.models import (
    Cluster,
    Galaxy,
    Hex,
    InterClusterConnector,
    InterSectorConnector,
    LocationInSector,
    Position,
    Sector,
)

BASE_CHANCE_FOR_MULTIPLE_CLUSTER_CONNECTIONS = 0.75
STANDARD_RADIUS = 250_000


class SectorGenerationException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class SectorGenerator:
    def __init__(self, config: Config, galaxy: Galaxy) -> None:
        self.config = config
        self.galaxy = galaxy
        self.hex_grid: set[Hex] = set()

    def generate(self) -> None:
        """Generate clusters with 1-3 sectors each, until we reach the sector cap."""
        self._generate_hex_grid()
        self._generate_clusters_and_sectors()
        self._generate_cluster_highways()
        self._generate_sector_highways()

    def _generate_hex_grid(self) -> None:
        new_hexes: set[Hex] = {Hex(center=Position(0, 0, 0))}
        # TODO make this number based on the number of sectors in the config
        while len(self.hex_grid) < 200:
            hexes_to_add: set[Hex] = set()
            for hex in new_hexes:
                # for every recently added hex, populate its neighbors.
                # we don't have to worry about dupes since we're using sets
                hexes_to_add.update([Hex(center=x) for x in hex.neighbor_positions])
            self.hex_grid.update(hexes_to_add)
            new_hexes = {*hexes_to_add}

    def _generate_cluster_highways(self) -> None:
        for cluster in self.galaxy.cluster_list:
            # order other clusters by distance and join a few nearby ones
            # that don't already have a connection to the one we're looking at
            siblings = sorted(
                self.galaxy.get_cluster_siblings(cluster),
                key=lambda x: distance_between_points(
                    x.position, cast(Position, cluster.position)
                ),
            )

            for sib in siblings:
                ids = [x.id for x in self.galaxy.highways]
                if not check_for_connection(cluster.id, sib.id, ids):
                    connection_count = count_connections(cluster.id, ids)
                    if connection_count == 0:
                        entry_point, exit_point = (
                            get_location_in_sector_from_cluster_both(cluster, sib)
                        )
                        highway = InterClusterConnector(
                            entry_point=entry_point,
                            exit_point=exit_point,
                            entry_cluster=cluster,
                            exit_cluster=sib,
                        )
                        self.galaxy.highways.append(highway)
                    else:
                        chance = (
                            BASE_CHANCE_FOR_MULTIPLE_CLUSTER_CONNECTIONS
                            / connection_count**2
                        )
                        if random.random() <= chance:
                            entry_point, exit_point = (
                                get_location_in_sector_from_cluster_both(cluster, sib)
                            )
                            highway = InterClusterConnector(
                                entry_point=entry_point,
                                exit_point=exit_point,
                                entry_cluster=cluster,
                                exit_cluster=sib,
                            )
                            self.galaxy.highways.append(highway)

    def _generate_sector_highways(self) -> None:
        # TODO refactor this to use galaxy.sector_list if possible
        for cluster in self.galaxy.clusters.values():
            if len(cluster.sectors) > 1:
                for sector in cluster.sectors.values():
                    # if the target sector has no connections, connect it to one of its siblings
                    if not any(
                        [
                            sector.id in break_compound_id(x.id)
                            for x in cluster.inter_sector_highways
                        ]
                    ):
                        max_gate_distance = convert_km_to_m_galaxy_scale(800)
                        partner = random.choice(cluster.get_sector_siblings(sector))
                        main_gate_pos, partner_gate_pos = (
                            get_directional_position_from_pair_both(
                                sector.position, partner.position, max_gate_distance
                            )
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

    def _get_position_for_sector(self, cluster: Cluster) -> Position:
        # breakpoint()
        if cluster.sector_count == 0:
            while True:
                # breakpoint()
                hex = random.choice(list(self.hex_grid))
                if hex.center not in [
                    sec.hex.center for sec in self.galaxy.sector_list
                ]:
                    return hex.center
        potential_positions: set[Position] = set(
            [pos for sec in cluster.sector_list for pos in sec.hex.neighbor_positions]
        )
        while len(list(potential_positions)) > 0:
            pos = random.choice(list(potential_positions))
            if pos not in [sec.hex.center for sec in self.galaxy.sector_list]:
                # breakpoint()
                return pos
            potential_positions.remove(pos)

        raise SectorGenerationException("No valid hex found for sector")

    def _generate_clusters_and_sectors(self) -> None:
        while self.galaxy.sector_count < self.config.sector_count:
            cluster_id = self.galaxy.cluster_count
            cluster = Cluster(
                id=cluster_id,
            )
            self.galaxy.clusters[cluster_id] = cluster

            max_sectors = random.randint(1, 3)
            for i in range(0, max_sectors):
                sector = Sector(
                    id=i,
                    position=self._get_position_for_sector(cluster),
                    cluster_id=cluster_id,
                )
                cluster.sectors[i] = sector
