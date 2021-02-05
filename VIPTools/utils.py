# -*- coding: utf-8 -*-
'''
@Time          : 21/01/30
@Author        : Freder Chen
@File          : utils.py
'''

import os


def mkdir(dir_):
    '''
    make folder if it's not exists

    dir_: folder path
    '''
    if dir_ is not None and isinstance(dir_, str) and len(dir_) > 0 and not os.path.exists(dir_):
        os.makedirs(dir_)
