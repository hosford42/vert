# -*- coding: utf-8 -*-

# Copyright 2017 Aaron M. Hosford
# See LICENSE.txt for licensing information.

import collections.abc

from typing import Union, Iterator, Hashable, Any, Optional, MutableMapping

from vert.stores.base import GraphStore, EdgeID, Label, VertexID
from vert.stores.memory import MemoryGraphStore
from vert.stores.dbm import DBMGraphStore


__all__ = [
    'Vertex',
    'Edge',
    'Graph',
]


VertexOrID = Union[VertexID, 'Vertex']
EdgeOrID = Union[EdgeID, 'Edge']


class GraphComponent:

    def __init__(self, graph_store: GraphStore):
        self._graph_store = graph_store

    def _to_vid(self, vertex: VertexOrID) -> VertexID:
        if isinstance(vertex, Vertex):
            if vertex._graph_store is not self._graph_store:
                raise ValueError(vertex)
            return vertex.vid
        else:
            return vertex

    def _to_eid(self, edge: EdgeOrID) -> EdgeID:
        if isinstance(edge, Edge):
            if edge._graph_store is not self._graph_store:
                raise ValueError(edge)
            return edge.eid
        elif isinstance(edge, EdgeID):
            return edge
        else:
            return EdgeID(*edge)


class FullVertexSet(collections.abc.MutableSet, GraphComponent):

    def __contains__(self, vertex: VertexOrID) -> bool:
        vid = self._to_vid(vertex)
        return self._graph_store.has_vertex(vid)

    def __iter__(self) -> Iterator['Vertex']:
        for vid in self._graph_store.iter_vertices():
            yield Vertex(vid, self._graph_store)

    def __len__(self) -> int:
        return self._graph_store.count_vertices()

    def __getitem__(self, vid: VertexID) -> 'Vertex':
        return Vertex(vid, self._graph_store)

    def add(self, vertex: VertexOrID) -> 'Vertex':
        vid = self._to_vid(vertex)
        self._graph_store.add_vertex(vid)
        if isinstance(vertex, Vertex):
            return vertex
        else:
            return Vertex(vid, self._graph_store)

    def remove(self, vertex: VertexOrID) -> None:
        vid = self._to_vid(vertex)
        if not self._graph_store.has_vertex(vid):
            raise KeyError(vid)
        self._graph_store.discard_vertex(vid)

    def discard(self, vertex: VertexOrID) -> None:
        vid = self._to_vid(vertex)
        self._graph_store.discard_vertex(vid)


class FullSourceVertexSet(collections.abc.Set, GraphComponent):

    def __contains__(self, vertex: VertexOrID) -> bool:
        vid = self._to_vid(vertex)
        return self._graph_store.has_sink(vid)

    def __iter__(self) -> Iterator['Vertex']:
        for vid in self._graph_store.iter_sources():
            yield Vertex(vid, self._graph_store)

    def __len__(self) -> int:
        return self._graph_store.count_sources()


class FullSinkVertexSet(collections.abc.Set, GraphComponent):

    def __contains__(self, vertex: VertexOrID) -> bool:
        vid = self._to_vid(vertex)
        return self._graph_store.has_source(vid)

    def __iter__(self) -> Iterator['Vertex']:
        for vid in self._graph_store.iter_sinks():
            yield Vertex(vid, self._graph_store)

    def __len__(self) -> int:
        return self._graph_store.count_sinks()


class FullEdgeSet(collections.abc.MutableSet, GraphComponent):

    @property
    def sources(self):
        return FullSourceVertexSet(self._graph_store)

    @property
    def sinks(self):
        return FullSinkVertexSet(self._graph_store)

    def __contains__(self, edge: EdgeOrID) -> bool:
        eid = self._to_eid(edge)
        return self._graph_store.has_edge(eid)

    def __iter__(self) -> Iterator['Edge']:
        for eid in self._graph_store.iter_edges():
            yield Edge(eid, self._graph_store)

    def __len__(self) -> int:
        return self._graph_store.count_edges()

    def __getitem__(self, eid: EdgeID) -> 'Edge':
        return Edge(eid, self._graph_store)

    def add(self, edge: EdgeOrID) -> 'Edge':
        eid = self._to_eid(edge)
        self._graph_store.add_edge(eid)
        return Edge(eid, self._graph_store)

    def remove(self, edge: EdgeOrID) -> None:
        eid = self._to_eid(edge)
        if not self._graph_store.has_edge(eid):
            raise KeyError(eid)
        self._graph_store.discard_edge(eid)

    def discard(self, edge: EdgeOrID) -> None:
        eid = self._to_eid(edge)
        self._graph_store.discard_edge(eid)


class UniqueVertexSet(collections.abc.Set, GraphComponent):

    def __init__(self, vid, graph_store: GraphStore):
        GraphComponent.__init__(self, graph_store)
        self._vid = vid

    def __contains__(self, vertex: VertexOrID) -> bool:
        vid = self._to_vid(vertex)
        return vid == self._vid

    def __iter__(self) -> Iterator['Vertex']:
        yield Vertex(self._vid, self._graph_store)

    def __len__(self) -> int:
        return 1


class SourceVertexSet(collections.abc.MutableSet, GraphComponent):

    def __init__(self, vid: VertexID, graph_store: GraphStore):
        GraphComponent.__init__(self, graph_store)
        self._vid = vid

    def __contains__(self, vertex: VertexOrID) -> bool:
        vid = self._to_vid(vertex)
        eid = EdgeID(vid, self._vid)
        return self._graph_store.has_edge(eid)

    def __iter__(self) -> Iterator['Vertex']:
        for source in self._graph_store.iter_sources(self._vid):
            yield Vertex(source, self._graph_store)

    def __len__(self) -> int:
        return self._graph_store.count_sources(self._vid)

    def add(self, vertex: VertexOrID) -> 'Vertex':
        vid = self._to_vid(vertex)
        eid = EdgeID(vid, self._vid)
        self._graph_store.add_edge(eid)
        return Vertex(vid, self._graph_store)

    def remove(self, vertex: VertexOrID) -> None:
        vid = self._to_vid(vertex)
        eid = EdgeID(vid, self._vid)
        if not self._graph_store.has_edge(eid):
            raise KeyError(vid)
        self._graph_store.discard_edge(eid)

    def discard(self, vertex: VertexOrID) -> None:
        vid = self._to_vid(vertex)
        eid = EdgeID(vid, self._vid)
        self._graph_store.discard_edge(eid)


class InboundEdgeSet(collections.abc.Set, GraphComponent):

    def __init__(self, vid: VertexID, graph_store: GraphStore):
        GraphComponent.__init__(self, graph_store)
        self._vid = vid

    @property
    def sources(self) -> SourceVertexSet:
        return SourceVertexSet(self._vid, self._graph_store)

    @property
    def sinks(self) -> UniqueVertexSet:
        return UniqueVertexSet(self._vid, self._graph_store)

    def __contains__(self, edge: EdgeOrID) -> bool:
        eid = self._to_eid(edge)
        if self._vid != eid.sink:
            return False
        return self._graph_store.has_edge(eid)

    def __iter__(self) -> Iterator['Edge']:
        for source in self._graph_store.iter_sources(self._vid):
            eid = EdgeID(source, self._vid)
            yield Edge(eid, self._graph_store)

    def __len__(self) -> int:
        return self._graph_store.count_sources(self._vid)

    def __getitem__(self, vertex: VertexOrID) -> 'Edge':
        vid = self._to_vid(vertex)
        eid = Edge(vid, self._vid)
        return Edge(eid, self._graph_store)


class SinkVertexSet(collections.abc.MutableSet, GraphComponent):

    def __init__(self, vid: VertexID, graph_store: GraphStore):
        GraphComponent.__init__(self, graph_store)
        self._vid = vid

    def __contains__(self, vertex: VertexOrID) -> bool:
        vid = self._to_vid(vertex)
        eid = EdgeID(self._vid, vid)
        return self._graph_store.has_edge(eid)

    def __iter__(self) -> Iterator['Vertex']:
        for sink in self._graph_store.iter_sinks(self._vid):
            yield Vertex(sink, self._graph_store)

    def __len__(self) -> int:
        return self._graph_store.count_sinks(self._vid)

    def add(self, vertex: VertexOrID) -> 'Vertex':
        vid = self._to_vid(vertex)
        eid = EdgeID(self._vid, vid)
        self._graph_store.add_edge(eid)
        return Vertex(vid, self._graph_store)

    def remove(self, vertex: VertexOrID) -> None:
        vid = self._to_vid(vertex)
        eid = EdgeID(self._vid, vid)
        if not self._graph_store.has_edge(eid):
            raise KeyError(vid)
        self._graph_store.discard_edge(eid)

    def discard(self, vertex: VertexOrID) -> None:
        vid = self._to_vid(vertex)
        eid = EdgeID(self._vid, vid)
        self._graph_store.discard_edge(eid)


class OutboundEdgeSet(collections.abc.Set, GraphComponent):

    def __init__(self, vid: VertexID, graph_store: GraphStore):
        GraphComponent.__init__(self, graph_store)
        self._vid = vid

    @property
    def sources(self) -> UniqueVertexSet:
        return UniqueVertexSet(self._vid, self._graph_store)

    @property
    def sinks(self):
        return SinkVertexSet(self._vid, self._graph_store)

    def __contains__(self, edge: EdgeOrID) -> bool:
        eid = self._to_eid(edge)
        if self._vid != eid.source:
            return False
        return self._graph_store.has_edge(eid)

    def __iter__(self) -> Iterator['Edge']:
        for sink in self._graph_store.iter_sinks(self._vid):
            eid = EdgeID(self._vid, sink)
            yield Edge(eid, self._graph_store)

    def __len__(self) -> int:
        return self._graph_store.count_sinks(self._vid)

    def __getitem__(self, vertex: VertexOrID) -> 'Edge':
        vid = self._to_vid(vertex)
        eid = EdgeID(self._vid, vid)
        return Edge(eid, self._graph_store)


class VertexLabelSet(collections.abc.MutableSet, GraphComponent):

    def __init__(self, vid: VertexID, graph_store: GraphStore):
        GraphComponent.__init__(self, graph_store)
        self._vid = vid

    def __contains__(self, label: Label) -> bool:
        return self._graph_store.has_vertex_label(self._vid, label)

    def __iter__(self) -> Iterator[Label]:
        return self._graph_store.iter_vertex_labels(self._vid)

    def __len__(self) -> int:
        return self._graph_store.count_vertex_labels(self._vid)

    def add(self, label: Label) -> None:
        self._graph_store.add_vertex_label(self._vid, label)

    def remove(self, label: Label) -> None:
        if not self._graph_store.has_vertex_label(self._vid, label):
            raise KeyError(label)
        self._graph_store.discard_vertex_label(self._vid, label)

    def discard(self, label: Label) -> None:
        self._graph_store.discard_vertex_label(self._vid, label)


class EdgeLabelSet(collections.abc.MutableSet, GraphComponent):

    def __init__(self, eid: EdgeID, graph_store: GraphStore):
        GraphComponent.__init__(self, graph_store)
        self._eid = eid

    def __contains__(self, label: Label) -> bool:
        return self._graph_store.has_edge_label(self._eid, label)

    def __iter__(self) -> Iterator[Label]:
        return self._graph_store.iter_edge_labels(self._eid)

    def __len__(self) -> int:
        return self._graph_store.count_edge_labels(self._eid)

    def add(self, label: Label) -> None:
        self._graph_store.add_edge_label(self._eid, label)

    def remove(self, label: Label) -> None:
        if not self._graph_store.has_edge_label(self._eid, label):
            raise KeyError(label)
        self._graph_store.discard_edge_label(self._eid, label)

    def discard(self, label: Label) -> None:
        self._graph_store.discard_edge_label(self._eid, label)


class VertexDataMap(collections.abc.MutableMapping, GraphComponent):

    def __init__(self, vid: VertexID, graph_store: GraphStore):
        GraphComponent.__init__(self, graph_store)
        self._vid = vid

    def __contains__(self, key: Hashable) -> bool:
        return self._graph_store.has_vertex_data(self._vid, key)

    def __iter__(self) -> Iterator[Hashable]:
        return self._graph_store.iter_vertex_data_keys(self._vid)

    def __len__(self) -> int:
        return self._graph_store.count_vertex_data_keys(self._vid)

    def __getitem__(self, key: Hashable) -> Any:
        if not self._graph_store.has_vertex_data(self._vid, key):
            raise KeyError(key)
        return self._graph_store.get_vertex_data(self._vid, key)

    def __setitem__(self, key: Hashable, value: Any) -> None:
        self._graph_store.set_vertex_data(self._vid, key, value)

    def __delitem__(self, key: Hashable) -> None:
        if not self._graph_store.has_vertex_data(self._vid, key):
            raise KeyError(key)
        self._graph_store.discard_vertex_data(self._vid, key)


class EdgeDataMap(collections.abc.MutableMapping, GraphComponent):

    def __init__(self, eid: EdgeID, graph_store: GraphStore):
        GraphComponent.__init__(self, graph_store)
        self._eid = eid

    def __contains__(self, key: Hashable) -> bool:
        return self._graph_store.has_edge_data(self._eid, key)

    def __iter__(self) -> Iterator[Hashable]:
        return self._graph_store.iter_edge_data_keys(self._eid)

    def __len__(self) -> int:
        return self._graph_store.count_edge_data_keys(self._eid)

    def __getitem__(self, key: Hashable) -> Any:
        if not self._graph_store.has_edge_data(self._eid, key):
            raise KeyError(key)
        return self._graph_store.get_edge_data(self._eid, key)

    def __setitem__(self, key: Hashable, value: Any) -> None:
        self._graph_store.set_edge_data(self._eid, key, value)

    def __delitem__(self, key: Hashable) -> None:
        if not self._graph_store.has_edge_data(self._eid, key):
            raise KeyError(key)
        self._graph_store.discard_edge_data(self._eid, key)


class Vertex(GraphComponent):

    def __init__(self, vid: VertexID, graph_store: GraphStore):
        super().__init__(graph_store)
        self._vid = vid

    def __str__(self):
        return repr(self._vid)

    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self._vid, self._graph_store)

    def __hash__(self):
        return hash(self._vid)

    def __eq__(self, other: 'Vertex'):
        if not isinstance(other, Vertex):
            return NotImplemented
        return self._vid == other._vid and self._graph_store is other._graph_store

    def __ne__(self, other: 'Vertex'):
        if not isinstance(other, Vertex):
            return NotImplemented
        return self._vid != other._vid or self._graph_store is not other._graph_store

    def __bool__(self) -> bool:
        return self._graph_store.has_vertex(self._vid)

    @property
    def vid(self) -> VertexID:
        return self._vid

    @property
    def labels(self) -> VertexLabelSet:
        return VertexLabelSet(self._vid, self._graph_store)

    @property
    def data(self) -> VertexDataMap:
        return VertexDataMap(self._vid, self._graph_store)

    @property
    def exists(self) -> bool:
        return self._graph_store.has_vertex(self._vid)

    @property
    def inbound(self) -> InboundEdgeSet:
        return InboundEdgeSet(self._vid, self._graph_store)

    @property
    def outbound(self) -> OutboundEdgeSet:
        return OutboundEdgeSet(self._vid, self._graph_store)

    @property
    def sources(self):
        return SourceVertexSet(self._vid, self._graph_store)

    @property
    def sinks(self):
        return SinkVertexSet(self._vid, self._graph_store)

    def add(self) -> 'Vertex':
        self._graph_store.add_vertex(self._vid)
        return self

    def remove(self) -> None:
        if not self._graph_store.has_vertex(self._vid):
            raise KeyError(self._vid)
        self._graph_store.discard_vertex(self._vid)

    def discard(self) -> None:
        self._graph_store.discard_vertex(self._vid)


class Edge(GraphComponent):

    def __init__(self, eid: EdgeID, graph_store: GraphStore):
        super().__init__(graph_store)
        if not isinstance(eid, EdgeID):
            eid = EdgeID(*eid)
        self._eid = eid

    def __str__(self):
        return repr(self._eid)

    def __repr__(self):
        return '%s(%r, %r)' % (type(self).__name__, self._eid, self._graph_store)

    def __hash__(self):
        return hash(self._eid)

    def __eq__(self, other: 'Edge'):
        if not isinstance(other, Edge):
            return NotImplemented
        return self._eid == other._eid and self._graph_store is other._graph_store

    def __ne__(self, other: 'Edge'):
        if not isinstance(other, Edge):
            return NotImplemented
        return self._eid != other._eid or self._graph_store is not other._graph_store

    def __bool__(self) -> bool:
        return self._graph_store.has_edge(self._eid)

    @property
    def eid(self) -> EdgeID:
        return self._eid

    @property
    def source(self) -> Vertex:
        return Vertex(self._eid.source, self._graph_store)

    @property
    def sink(self) -> Vertex:
        return Vertex(self._eid.sink, self._graph_store)

    @property
    def labels(self) -> EdgeLabelSet:
        # noinspection PyTypeChecker
        return EdgeLabelSet(self._eid, self._graph_store)

    @property
    def data(self) -> EdgeDataMap:
        # noinspection PyTypeChecker
        return EdgeDataMap(self._eid, self._graph_store)

    @property
    def exists(self) -> bool:
        return self._graph_store.has_edge(self._eid)

    def add(self) -> 'Edge':
        self._graph_store.add_edge(self._eid)
        return self

    def remove(self) -> None:
        if not self._graph_store.has_edge(self._eid):
            raise KeyError(self._eid)
        self._graph_store.discard_edge(self._eid)

    def discard(self) -> None:
        self._graph_store.discard_edge(self._eid)


class Graph:

    def __init__(self, store: Optional[Union[GraphStore, str, MutableMapping[bytes, bytes]]]=None):
        if store is None:
            store = MemoryGraphStore()
        elif not isinstance(store, GraphStore):
            store = DBMGraphStore(store)
        assert isinstance(store, GraphStore)
        self._graph_store = store

    def __del__(self):
        self.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    @property
    def is_open(self):
        return self._graph_store.is_open

    def close(self):
        self._graph_store.close()

    @property
    def vertices(self) -> FullVertexSet:
        return FullVertexSet(self._graph_store)

    @property
    def edges(self) -> FullEdgeSet:
        return FullEdgeSet(self._graph_store)
