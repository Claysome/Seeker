# -*- encoding: utf-8 -*-
'''
@File    :   config.py
@Time    :   2023/03/05 14:25:02
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''

"""Config Module"""

import json
from app.utils import tools


class Config:
    """
    Load a json file like `config.json` and parse the content to json object
    """

    def __init__(self):
        self.server_id = None
        self.log = {}
        self.accounts = []
        self.markets = {}
        self.heartbeat = {}
        self.proxy = None

    def loads(self, config_file=None):
        """Load config json file"""
        configs = {}
        if config_file:
            try:
                with open(config_file) as f:
                    data = f.read()
                    configs = json.loads(data)
            except Exception as e:
                print(e)
                exit(0)
            if not configs:
                print("Config file error, please validate your configuration")
                exit(0)
        self._update(configs)

    def _update(self, update_fields=None):
        """Update config fields"""
        self.server_id = update_fields.get('SERVER_ID', tools.get_uuid1())
        self.log = update_fields.get('LOG', {})
        self.accounts = update_fields.get('ACCOUNTS', [])
        self.markets = update_fields.get('MARKETS', {})
        self.heartbeat = update_fields.get('HEARTBEAT', {})
        self.proxy = update_fields.get('PROXY', None)

        for k, v in update_fields.items():
            setattr(self, k, v)



config = Config()
