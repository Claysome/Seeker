# -*- encoding: utf-8 -*-
'''
@File    :   error.py
@Time    :   2023/03/05 20:57:41
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''

"""Error Module"""


class Error:
    def __init__(self, msg):
        self.msg = msg

    @property
    def msg(self):
        return self._msg
    
    def __str__(self):
        return str(self._msg)
    
    def __repr__(self) -> str:
        return str(self)