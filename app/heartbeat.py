# -*- encoding: utf-8 -*-
'''
@File    :   heartbeat.py
@Time    :   2023/03/05 01:41:55
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''


import asyncio
from app.utils import logger
from app.utils import tools
from app.config import config

__all__ = {"Heartbeat", }


class Heartbeat:
    """Server heartbeat"""

    def __init__(self):
        self._count = 0
        self._interval = 1
        self._present_interval = config.heartbeat.get("interval", 0)
        self._tasks = {}

    @property
    def count(self):
        return self._count
    
    def ticker(self):
        """Loop run over per ticker"""
        self._count += 1
        if self._present_interval > 0:
            if self._count % self._present_interval == 0:
                logger.info("Heartbeat server, count: %d", self._count, caller=self)
        # call later next ticker
        asyncio.get_event_loop().call_later(self._interval, self.ticker)
        # execute tasks
        for task_id, task in self._tasks.items():
            interval = task['task']
            if self._count % interval != 0: continue
            func = task['func']
            args = task['args']
            kwargs = task['kwargs']
            kwargs['task_id'] = task_id
            kwargs['heartbeat_count'] = self._count
            asyncio.get_event_loop().create_task(func(*args, **kwargs))

    def register(self, func, interval=1, *args, **kwargs):
        """Register task"""
        task_id = tools.get_uuid1()
        t = {
            'func': func,
            'interval': interval,
            'args': args,
            'kwargs': kwargs
        }

        self._tasks[task_id] = t
        return task_id
    
    def unregister(self, task_id):
        """Unregister task"""
        if task_id in self._tasks:
            self._tasks.pop(task_id)



heartbeat = Heartbeat()
        

        


