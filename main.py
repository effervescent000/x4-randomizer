from config.config_maker import read_config
from generator.sectors.generator import SectorGenerator
from generator.sectors.models import Galaxy
from mod_writer.mod_writer import ModWriter


config = read_config()
galaxy = Galaxy()

sector_gen = SectorGenerator(config, galaxy)
sector_gen.generate()

writer = ModWriter(galaxy)
writer.write()
