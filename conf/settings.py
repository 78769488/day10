#!/usr/bin/env python
# -*- coding=utf-8 -*-
# Author: Zhang Renfang
# E-mail: 78769488@qq.com
import os

# 打印到屏幕的日志级别
level_console = 'DEBUG'

# 保存到文件的日志级别
level_files = 'INFO'

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

data_dir = os.path.join(base_dir, 'data')  # 数据文件目录
if not os.path.isdir(data_dir):
    os.makedirs(data_dir)

if __name__ == '__main__':
    print(base_dir)
