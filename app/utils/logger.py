# -*- encoding: utf-8 -*-
'''
@File    :   logger.py
@Time    :   2023/03/05 01:57:43
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''

"""Logger Module"""

import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
import traceback
import shutil

INIT = False

def InitLogger(level='DEBUG', path=None, name=None, clear=False, backup_count=0, console=True):
    global INIT
    if INIT: return

    path = path or os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "logs"))
    name = name or "trade.log"
    logger = logging.getLogger()
    logger.setLevel(level)

    if console:
        print("="*60, "Init logger", "="*60)
        handler = logging.StreamHandler()
    else:
        if clear and os.path.isdir(path): shutil.rmtree(path)
        if not os.path.isdir(path): os.makedirs(path)
        logfile = os.path.join(path, name)
        handler = TimedRotatingFileHandler(path + name, when='midnight', backupCount=backup_count)
        print("="*60, "Init logger with", logfile, "="*60)
    
    str_fmt = "%(levelname)s [%(asctime)s] %(message)s"
    handler.setFormatter(str_fmt)
    logger.addHandler(handler)
    INIT = True        


def _log(msg_header, *args, **kwargs):
    _log_msg = msg_header
    for l in args:
        if type(l) is tuple: ps = str(l)
        else:
            try: ps = "%r" % l
            except: ps = str(l)
        if type(l) is str:
            _log_msg += ps[1:-1] + " "
        else:
            _log_msg += ps + " "
    if len(kwargs) > 0:
        _log_msg += str(kwargs)
    return _log_msg


def _log_msg_header(*args, **kwargs):
    """Fetch the message header"""
    cls_name = ""
    func_name = sys._getframe().f_back.f_back.f_code.co_name
    session_id = "-"

    try:
        _caller = kwargs.get('caller', None)
        if _caller:
            if not hasattr(_caller, '__name__'):
                _caller = _caller.__class__
            cls_name = _caller.__name__
            del kwargs['caller']
    except:
        pass
    finally:
        msg_header = "[{session_id}] [{cls_name}.{func_name}]".format(session_id=session_id, cls_name=cls_name, func_name=func_name)
        return msg_header, kwargs


def info(*args, **kwargs):
    func_name, kwargs = _log_msg_header(*args, **kwargs)
    logging.info(_log(func_name, *args, **kwargs))


def debug(*args, **kwargs):
    func_name, kwargs = _log_msg_header(*args, **kwargs)
    logging.debug(_log(func_name, *args, **kwargs))


def warning(*args, **kwargs):
    func_name, kwargs = _log_msg_header(*args, **kwargs)
    logging.warning(_log(func_name, *args, **kwargs))


def error(*args, **kwargs):
    logging.error("*" * 60)
    msg_header, kwargs = _log_msg_header(*args, **kwargs)
    logging.error(_log(msg_header, *args, **kwargs))
    logging.error("*" * 60)


def exception(*args, **kwargs):
    logging.error("*" * 60)
    msg_header, kwargs = _log_msg_header(*args, **kwargs)
    logging.error(_log(msg_header, *args, **kwargs))
    logging.error(traceback.format_exc())
    logging.error("*" * 60)

