import json
import time

import yaml
from easydict import EasyDict


def now():
    return time.strftime("%Y%m%d%H%M%S", time.localtime())

def get_easyDict_from_filepath(path: str):
    # print(path)
    if path.endswith('.json'):
        with open(path, 'r', encoding="utf-8") as file:
            config_map = json.load(file, strict=False)
            config_easydict = EasyDict(config_map)
            return config_easydict
    if path.endswith('.yaml'):
        file_data = open(path, 'r', encoding="utf-8").read()
        config_map = yaml.load(file_data, Loader=yaml.FullLoader)
        config_easydict = EasyDict(config_map)
        return config_easydict
    return None