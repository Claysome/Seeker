# -*- encoding: utf-8 -*-
'''
@File    :   loggingtool.py
@Time    :   2023/03/12 13:30:56
@Author  :   Claysome 
@Contact :   claysomes@outlook.com
'''


import os
import logging
from logging import handlers


def get_logger(file_name, path="logs", level=logging.INFO,
               when='MIDNIGHT', back_count=7, fmt='%(asctime)s-[%(filename)s line:%(lineno)d]-%(levelname)s: %(message)s',
               datefmt='%Y-%m-%d %H:%M:%S'):
    """
    :param file_name: log file name
    :param path: log sub path
    :param level: log level
    :param when: when to split file
    :param back_count: number of log config
    :param fmt: log format
    :param datefmt: date format
    :return:
    """
    current_path = os.getcwd()
    log_path = os.path.join(current_path, path)
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    log_file = os.path.join(log_path, file_name)
    logger = logging.getLogger(log_file)
    logger.propagate = False

    if not logger.handlers:

        format_str = logging.Formatter(fmt, datefmt=datefmt)   # set log format
        logger.setLevel(level)                                 # set log level

        sh = logging.StreamHandler()                           # set log console
        sh.setFormatter(format_str)                            # set log format for console

        th = handlers.TimedRotatingFileHandler(filename=log_file, interval=1, when=when, backupCount=back_count,
                                               encoding='utf-8')
        th.suffix = "%Y-%m-%d.log"                             # set file suffix
        th.setFormatter(format_str)                            # set file format
        logger.addHandler(sh)                                  # add handler to logger
        logger.addHandler(th)

    return logger


utils_log = get_logger("utils.log", "logs")