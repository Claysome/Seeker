# -*- encoding: utf-8 -*-
'''
@File    :   tools.py
@Time    :   2023/03/05 14:19:06
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''

"""Tool Module"""

import uuid
import time


def get_uuid1():
    """Generate a UUID based on the host ID and current time
    :return s: string UUID1"""
    uid1 = uuid.uuid1()
    s = str(uid1)
    return s
