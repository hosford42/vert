# -*- coding: utf-8 -*-

# Copyright 2017 Aaron M. Hosford
# See LICENSE.txt for licensing information.

from . import stores, graphs

from .stores.base import GraphStore, VertexID, EdgeID, DirectedEdgeID, UndirectedEdgeID, Label
from .stores.dbm import DBMGraphStore
from .stores.memory import MemoryGraphStore
from .graphs import Graph, Vertex, Edge

from .__about__ import __title__, __summary__, __url__, __version__, __status__, __author__, __maintainer__, \
    __credits__, __email__, __license__, __copyright__


__all__ = [
    '__title__',
    '__summary__',
    '__url__',
    '__version__',
    '__status__',
    '__author__',
    '__maintainer__',
    '__credits__',
    '__email__',
    '__license__',
    '__copyright__',
    'stores',
    'graphs',
    'GraphStore',
    'VertexID',
    'EdgeID',
    'DirectedEdgeID',
    'UndirectedEdgeID',
    'Label',
    'DBMGraphStore',
    'MemoryGraphStore',
    'Graph',
    'Vertex',
    'Edge',
]
