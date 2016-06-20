from __future__ import absolute_import

from .client import TelegrafClient

VERSION = (0, 1, 1)
__version__ = '.'.join(map(str, VERSION))
__all__ = ['TelegrafClient']
