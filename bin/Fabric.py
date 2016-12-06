#!/usr/bin/env python
# -*- coding=utf-8 -*-
# Author: Zhang Renfang
# E-mail: 78769488@qq.com

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import main
from core.MyLogging import logger

if __name__ == '__main__':
    logger.info("Start Fabric...")
    main.main()
    logger.info("Fabric stop...")

