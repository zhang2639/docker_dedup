# coding:utf-8 
import os
import logging
import logging.config

import yaml

class NitroConfiguration(object):
    """ Provide configuration to all system components

    Parse yaml configuration file
    """

    def __init__(self, config_file):
        self.load(config_file)

        def ensure_exists(dir_path):
            if not os.path.exists(dir_path):
                os.makedirs(dir_path)

        self.root_dir = self.config["root_dir"]
        self.logs_dir = os.path.join(self.root_dir, 'logs', str(self.peer_id()))
        self.results_dir = os.path.join(self.root_dir, 'results')

        ensure_exists(self.logs_dir)
        ensure_exists(self.results_dir)

        self.setup_logging()
        self.logger = logging.getLogger(__name__)
        self.logger.info("Configurations are initialized")


    def load(self, config_file):
        with open(config_file, 'r') as stream:
            try:
                self.config = yaml.load(stream)
            except yaml.YAMLError as exc:
                raise exc

    def edit_logging_config(self, config):
        new_config = dict(config)
        for handler, prop in config["handlers"].items():  #items 返回可遍历的k v 2元组
            if "filename" in prop:
                filename = config["handlers"][handler]["filename"]
                new_filename = os.path.join(self.logs_dir, filename)
                print new_filename
                new_config["handlers"][handler]["filename"] = new_filename
        return new_config

    def setup_logging(self,
                      default_path='logging.yaml',
                      default_level=logging.INFO,
                      env_key='LOG_CFG'):
        path = os.getenv(env_key, None) or default_path
        if os.path.exists(path):
            with open(path, 'rt') as ymlfile:
                config = yaml.safe_load(ymlfile.read())
            config = self.edit_logging_config(config)
            logging.config.dictConfig(config)
        else:
            logging.basicConfig(level=default_level)


    def peer_id(self):
        return int(self.config["id"])

    def peers(self):
        endpoints = [u.split(":") for u in self.config["peers"]]
        endpoints_tuples = [(u[0], int(u[1])) for u in endpoints]
        return endpoints_tuples

    def nb_sites(self):
        return len(self.config["peers"])

    def concurrent_conn_count(self):
        return self.config["concurrent_conn_count"]

    def peers_affinity(self):
        return self.config.get("peers_affinity", [1] * self.nb_sites())

    def storage_address(self):
        return self.config["storage_address"]

    def storage_backend(self):
        return self.config["storage_backend"]

    def compression_level(self):
        return self.config["compression_level"]

    def storage_method(self):
        return self.config["storage_method"]

    def storage_algorithm(self):
        return self.config["storage_algorithm"]

    def image_type(self):
        return self.config["image_type"]

    def chunk_size(self):
        return int(self.config["chunk_size"])

    def block_size(self):
        return int(self.config["block_size"])

    def chunk_scheduler(self):
        return self.config["chunk_scheduler"]

    def ws_address_bind(self):
        return self.config["ws_address_bind"]

    def ws_address_connect(self):
        return self.config["ws_address_connect"]

    def get_nitro_endpoint(self):
        return self.ws_address_connect()

    def zmq_proxy_to_comm_endpoint(self):
        return self.config["zmq_proxy_to_comm_endpoint"]

    def zmq_comm_to_proxy_endpoint(self):
        return self.config["zmq_comm_to_proxy_endpoint"]

    def output_csv_flename(self):
        return self.config.get("output_csv_flename", "nitro_stats.csv")

    def output_csv_path(self):
        return os.path.join(self.results_dir, self.output_csv_flename())
