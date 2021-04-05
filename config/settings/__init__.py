#! /usr/bin/python -*- coding:utf-8 -*-
import os

RUN_MODE = os.environ['RUN_MODE']

if RUN_MODE is None:
    RUN_MODE = 'test'

RUN_MODE = RUN_MODE.lower()
print("RUN_MODE : {} ".format(RUN_MODE))

if RUN_MODE == 'test':
    os.environ['STAGE'] = 'develop'
    from .base import *

else:
    raise Exception('RUN_MODE is invalid {}. This is critical Exception! '.format(RUN_MODE))

