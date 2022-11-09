import json
import yaml


class Config:
    def __init__(self):
        self._raw_config = self._get_config()
        self.chains = self._get_chains()
        self.exporter_port = self._raw_config["exporter_port"]
        self.polling_interval_seconds = self._raw_config["polling_interval_seconds"]
        self.alias = self._raw_config["alias"]

    def _get_config(self):
        with open("./config/config.yml", "r") as stream:
            return yaml.safe_load(stream)

    def _get_chains(self):
        with open("./config/chains.json", "r") as stream:
            return json.load(stream)
