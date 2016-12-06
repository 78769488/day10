#! /usr/bin/env python
# -*- coding: utf-8 -*-
# __author__ = "Q1mi"

"""
logging配置
"""

import logging.config
import os

from conf import settings

BASE_DIR = settings.base_dir

logfile_path = os.path.join(BASE_DIR, 'logs')
if not logfile_path:
    os.makedirs(logfile_path)

# log文件的全路径
LOGFILE_ALL = os.path.join(logfile_path, 'all.log')
LOGFILE_ERR = os.path.join(logfile_path, 'err.log')

level_console = settings.level_console if settings.level_console else 'DEBUG'
level_files = settings.level_files if settings.level_files else 'INFO'


def init_logger():
    # 定义三种日志格式
    standard_format = '[%(asctime)s]-[%(threadName)s:%(thread)d]-[task_id:%(name)s]-[%(filename)s:%(lineno)d]' \
                      '-[%(levelname)s]: %(message)s'
    # simple_format = '[%(levelname)s][%(asctime)s][%(filename)s:%(lineno)d]: %(message)s'
    simple_format = '[%(asctime)s-%(filename)s] %(message)s'

    # log配置字典
    logging_dic = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': standard_format
            },
            'simple': {
                'format': simple_format
            },
        },
        'filters': {},
        'handlers': {
            'console': {
                'level': level_console,
                'class': 'logging.StreamHandler',  # 打印到屏幕
                'formatter': 'simple'
            },
            'default': {
                'level': level_files,
                'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件
                'filename': LOGFILE_ALL,  # 日志文件
                'maxBytes': 1024*1024*5,  # 日志大小 5M
                'backupCount': 50,
                'formatter': 'standard',
                'encoding': 'utf-8',

            },
            'error': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',  # 保存到文件
                'filename': LOGFILE_ERR,  # 日志文件
                'maxBytes': 1024*1024*5,  # 日志大小 5M
                'backupCount': 50,
                'formatter': 'standard',
                'encoding': 'utf-8',
            },
        },
        # 这里把上面定义的两个handler都加上，即log数据既写入文件又打印到屏幕
        'loggers': {
            '': {
                'handlers': ['default', 'console', 'error'],
                'level': 'DEBUG',
                'propagate': True,
            },
        },
    }
    logging.config.dictConfig(logging_dic)  # 导入上面定义的配置
    return logging.getLogger(__name__)  # 生成一个log实例

logger = init_logger()

if __name__ == '__main__':
    # logger = init_logger()
    mylogger.info('It works!')  # 记录该文件的运行状态
