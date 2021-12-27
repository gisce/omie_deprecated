# -*- coding: utf-8 -*-
import os

try:
    __version__ = __import__('pkg_resources') \
        .get_distribution(__name__).version
except Exception as e:
    __version__ = 'unknown'

_ROOT = os.path.abspath(os.path.dirname(__file__))


def get_data(path):
    filename = isinstance(path, (list, tuple)) and path[0] or path
    return os.path.join(_ROOT, 'data', filename)
