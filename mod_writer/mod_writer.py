import os
import shutil

from lxml.objectify import Element, deannotate, ObjectifiedElement
from lxml import etree

from generator.sectors.models import Galaxy

ASSETS_ENV_LOC = os.path.join("assets", "environments")
MAPS_LOC = os.path.join("maps", "xu_ep2_universe")

CLUSTERS = "clusters"
COMPONENT = "component"
CONNECTION = "connection"
CONNECTIONS = "connections"
DESTINATION = "destination"
GALAXY = "galaxy"
NAME = "name"
MACRO = "macro"
REF = "ref"


class ModWriter:
    def __init__(self, galaxy: Galaxy) -> None:
        self.output_location = os.path.join(os.getcwd(), "output")
        self.galaxy = galaxy

    def _remove_existing_output(self) -> None:
        shutil.rmtree(self.output_location)
        os.makedirs(self.output_location)
        os.makedirs(os.path.join(self.output_location, ASSETS_ENV_LOC))
        os.makedirs(os.path.join(self.output_location, MAPS_LOC))

    def _write_galaxy_map(self) -> None:
        root = Element("macros")
        galaxy = Element(MACRO, attrib={NAME: "XU_EP2_universe_macro", "class": GALAXY})
        root.append(galaxy)

        galaxy.append(Element(COMPONENT, attrib={REF: "standardgalaxy"}))

        connections = Element(CONNECTIONS)
        galaxy.append(connections)
        for cluster in self.galaxy.cluster_list:
            conn = Element(
                CONNECTION,
                attrib={NAME: f"{cluster.label}_{CONNECTION}", REF: CLUSTERS},
            )
            connections.append(conn)
            macro = Element(
                MACRO, attrib={REF: f"{cluster.label}_{MACRO}", CONNECTION: GALAXY}
            )
            offset = Element("offset")
            position = Element(
                "position",
                attrib={
                    "x": str(cluster.position.x),
                    "y": "0",
                    "z": str(cluster.position.z),
                },
            )
            offset.append(position)

            conn.extend([macro, offset])

        for hw in self.galaxy.highways:
            conn = Element(CONNECTION, attrib={NAME: hw.label, REF: DESTINATION})
            connections.append(conn)

            macro = Element(MACRO, attrib={CONNECTION: DESTINATION})
            conn.append(macro)

        self._write_to_file(root, [MAPS_LOC, "galaxy.xml"])

    def _write_sector_map(self) -> None:
        root = Element("macros")
        for sector in self.galaxy.sector_list:
            sector_macro = Element(
                MACRO, attrib={NAME: f"{sector.label}_{MACRO}", "class": "sector"}
            )
            root.append(sector_macro)

            sector_macro.append(Element(COMPONENT, attrib={REF: "standardsector"}))

            connections = Element(CONNECTIONS)
            sector_macro.append(connections)

            # TODO zones here

        self._write_to_file(root, [MAPS_LOC, "sector.xml"])

    def _write_to_file(self, root: ObjectifiedElement, path: list[str]) -> None:
        deannotate(root)
        xml = etree.tostring(root, pretty_print=True, xml_declaration=True)

        with open(os.path.join(self.output_location, *path), "w") as file:
            file.write(xml.decode("utf-8"))

    def write(self) -> None:
        self._remove_existing_output()
        self._write_galaxy_map()
        self._write_sector_map()
