import json
from pathlib import Path
from typing import Tuple, List, Dict

import editdistance


class ServerConfig:
    threads_count: int = 15
    max_req_time: int = 100
    server_host: Tuple[str, int]
    (host, port) = '', 8080
    (proxy_pass_host, proxy_pass_port) = '', 8080
    queue_size: int = 5
    supported_protos: List[str] = ["HTTP/1.1", "HTTP/1.0"]
    www_dir: str = "wwwroot"
    log_file: str = "log.txt"
    __config_file: str = "config.json"

    def __new__(cls, *args, **kwargs):
        if not hasattr(cls, 'instance'):
            cls.instance = super(ServerConfig, cls).__new__(cls)
        return cls.instance

    def __init__(self, config_file_name=None):
        if config_file_name:
            self.__config_file = config_file_name
        config_path = Path.cwd() / self.__config_file
        self.__options = (name for name in dir(self) if not name.startswith(
            '_'))
        if config_path.is_file():
            with open(str(config_path)) as config_file:
                config = json.load(config_file)
                self.__load_settings(config)

    def __load_settings(self, config):
        """
        Loads self properties w/ values from config
        :type config: dict
        """
        for key in config.keys():
            if hasattr(self, key):
                setattr(self, key, config[key])
            else:
                guess_option = "failed to find close attributes..."
                guess_distance = -1
                for name in self.__options:
                    curr_distance = editdistance.eval(name, key)
                    if curr_distance < guess_distance or guess_distance == -1:
                        guess_distance = curr_distance
                        guess_option = name
                print(f"{key} option was not found. Maybe you meant "
                      f"{guess_option}?")
