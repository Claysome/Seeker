# -*- encoding: utf-8 -*-
'''
@File    :   tools.py
@Time    :   2023/03/05 14:19:06
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''

"""Tool Module"""

import uuid
import json
import random
from pathlib import Path
from decimal import Decimal


def get_uuid1():
    """Generate a UUID based on the host ID and current time
    :return s: string UUID1"""
    uid1 = uuid.uuid1()
    s = str(uid1)
    return s


def _get_trader_dir(tmp_name: str):
    """
    Get path where trader is running in
    """
    cwd = Path.cwd()
    tmp_path = cwd.joinpath(tmp_name)

    if tmp_path.exists():
        return cwd, tmp_path
    
    if not tmp_path.exists():
        tmp_path.mkdir()

    return cwd, tmp_path

TRADER_DIR, TEMP_DIR = _get_trader_dir("trader")


def get_file_path(filename: str):
    """
    Get path for temp folder with folder name
    """
    return TEMP_DIR.joinpath(filename)


def get_folder_path(folder_name: str):
    """
    Get path for temp folder with with folder name
    """
    folder_path = TEMP_DIR.joinpath(folder_name)
    if not folder_path.exists():
        folder_path.mkdir()
    return folder_path


def load_json(filename: str):
    """
    Load data from json file in temp path
    """
    filepath = get_file_path(filename)

    if filepath.exists():
        with open(filepath, mode="r", encoding="UTF-8") as f:
            data = json.load(f)
        return data
    else:
        save_json(filename, {})
        return {}


def save_json(filename: str, data: dict):
    """
    Save data into json file in temp path
    """
    filepath = get_file_path(filename)
    with open(filepath, mode="w+", encoding="UTF-8") as f:
        json.dump(
            data,
            f,
            indent=4,
            ensure_ascii=False
        )


def round_to(value: float, target: float) -> float:
    """
    Round price to price tick value
    """
    value = Decimal(str(value))
    target = Decimal(str(target))

    rounded_value = float(int(value / target) * target)
    return rounded_value


def to_symbol(symbol: str, exchange: str="binance"):
    if exchange == "binance":
        return symbol.replace("/", "").replace("-", "").replace("_", "")
    else:
        return str


def random_int_list(start, stop, length):
    start, stop = (int(start), int(stop)) if start <= stop else (int(stop), int(start))
    length = int(abs(length)) if length else 0
    random_list = []
    for i in range(length):
        random_list.append(random.randint(start, stop))
    return random_list


