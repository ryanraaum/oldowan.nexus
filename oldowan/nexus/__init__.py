"""This is the oldowan.nexus package."""


import os

VERSION = open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
               'VERSION')).read().strip()

__all__ = ['nexus',
           'entry2str']

try:
    from oldowan.nexus.nexus import nexus
    from oldowan.nexus.nexus import entry2str
except:
    from nexus import nexus
    from nexus import entry2str
