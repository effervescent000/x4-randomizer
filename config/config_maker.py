import yaml
from config.models import Config


def read_config() -> Config:
    with open("config.yml", "r") as file:
        return Config(**yaml.safe_load(file))
