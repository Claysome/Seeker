# -*- encoding: utf-8 -*-
'''
@File    :   utility.py
@Time    :   2023/03/12 20:19:15
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''

"""
General utility functions
"""

import sys
import json
import logging
from pathlib import Path
from typing import Callable, Dict, Tuple, Optional
from decimal import Decimal
from math import floor, ceil

import numpy as np
import hashlib

from .object import BarData, TickData
from .constant import Exchange, Interval


log_formatter = logging.Formatter('[%(asctime)s] %(message)s')


def extract_vt_symbo(vt_symbol: str) -> Tuple[str, Exchange]:
    """
    :return: (symbol, exchange)
    """
    symbol, exchange = vt_symbol.split('.')
    return symbol, Exchange(exchange)


def generate_vt_symbol(symbol: str, exchange: Exchange) -> str:
    pass