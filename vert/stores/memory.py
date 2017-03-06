# -*- coding: utf-8 -*-

# Copyright 2017 Aaron M. Hosford
# See LICENSE.txt for licensing information.

from typing import Hashable, Any, Optional, Iterator


import vert.stores.base as base


__all__ = [
    'MemoryGraphStore',
]


class MemoryGraphStore(base.GraphStore):
    """
    A Python-only, non-persistent graph store designed for sparse graphs.
    """

    def __init__(self):
        self._forward = {}
        self._backward = {}
        self._dual = {}
        self._vertex_labels = {}
        self._edge_labels = {}
        self._vertex_data = {}
        self._edge_data = {}
        self._edge_count = 0

    def count_vertices(self) -> int:
        return len(self._forward)

    def count_edges(self) -> int:
        return self._edge_count

    def iter_vertices(self) -> Iterator[base.VertexID]:
        return iter(self._forward)

    def iter_edges(self) -> Iterator[base.EdgeID]:
        for source, sinks in self._forward.items():
            for sink in sinks:
                yield base.DirectedEdgeID(source, sink)

        # We have to guarantee that each edge is only yielded once, which is a bit more complicated when edges
        # are undirected. We do that by imposing an artificial order on the IDs (since IDs are not required to be
        # ordered). I know repr is slow, but it's better than building a set to avoid duplicates.
        for left, rights in self._dual.items():
            if left in rights:
                yield base.UndirectedEdgeID(left, left)
            left_repr = repr(left)
            for right in rights:
                if left != right and left_repr < repr(right):
                    yield base.UndirectedEdgeID(left, right)

    def has_source(self, sink: base.VertexID) -> bool:
        return bool(self._backward.get(sink, ()))

    def has_sink(self, source: base.VertexID) -> bool:
        return bool(self._forward.get(source, ()))

    def iter_sources(self, sink: Optional[base.VertexID] = None) -> Iterator[base.VertexID]:
        if sink is None:
            for vid, sinks in self._forward.items():
                if sinks:
                    yield vid
        else:
            yield from self._backward.get(sink, ())

    def iter_sinks(self, source: Optional[base.VertexID] = None) -> Iterator[base.VertexID]:
        if source is None:
            for vid, sources in self._backward.items():
                if sources:
                    yield vid
        else:
            yield from self._forward.get(source, ())

    def count_sources(self, sink: Optional[base.VertexID] = None) -> int:
        if sink is None:
            return int(sum(bool(sinks) for sinks in self._forward.values()))
        else:
            return len(self._backward.get(sink, ()))

    def count_sinks(self, source: Optional[base.VertexID] = None) -> int:
        if source is None:
            return int(sum(bool(sources) for sources in self._backward.values()))
        else:
            return len(self._forward.get(source, ()))

    def has_vertex(self, vid: base.VertexID) -> bool:
        return vid in self._forward

    def has_edge(self, eid: base.EdgeID) -> bool:
        if isinstance(eid, base.DirectedEdgeID):
            return eid.sink in self._forward.get(eid.source, ())
        else:
            assert isinstance(eid, base.UndirectedEdgeID)
            v1, v2 = eid.vertices
            return v2 in self._dual.get(v1, ())

    def add_vertex(self, vid: base.VertexID) -> None:
        if vid not in self._forward:
            self._forward[vid] = set()
            self._backward[vid] = set()
            self._dual[vid] = set()

    def add_edge(self, eid: base.EdgeID) -> None:
        if isinstance(eid, base.DirectedEdgeID):
            if eid.sink in self._forward.get(eid.source, ()):
                return
            self.add_vertex(eid.source)
            self.add_vertex(eid.sink)
            self._forward[eid.source].add(eid.sink)
            self._backward[eid.sink].add(eid.source)
            self._edge_count += 1
        else:
            assert isinstance(eid, base.UndirectedEdgeID)
            v1, v2 = eid.vertices
            if v2 in self._dual.get(v1, ()):
                return
            self.add_vertex(v1)
            self.add_vertex(v2)
            self._dual[v1].add(v2)
            self._dual[v2].add(v1)

    def discard_vertex(self, vid: base.VertexID) -> bool:
        if vid not in self._forward:
            return False

        # Remove labels and data
        if vid in self._vertex_labels:
            del self._vertex_labels[vid]
        if vid in self._vertex_data:
            del self._vertex_data[vid]

        # Remove all incident edges.
        for sink in self._forward[vid]:
            self.discard_edge(base.DirectedEdgeID(vid, sink), ignore=vid)
        for source in self._backward[vid]:
            self.discard_edge(base.DirectedEdgeID(source, vid), ignore=vid)
        for other in self._dual[vid]:
            self.discard_edge(base.UndirectedEdgeID(vid, other), ignore=vid)

        # Remove the vertex itself
        del self._forward[vid]
        del self._backward[vid]
        del self._dual[vid]

        return True

    def discard_edge(self, eid: base.EdgeID, ignore: Optional[base.VertexID] = None) -> bool:
        if not self.has_edge(eid):
            return False

        # Remove labels and data.
        if eid in self._edge_labels:
            del self._edge_labels[eid]
        if eid in self._edge_data:
            del self._edge_data[eid]

        # Remove the edge itself
        if isinstance(eid, base.DirectedEdgeID):
            if eid.source != ignore:
                self._forward[eid.source].discard(eid.sink)
            if eid.sink != ignore:
                self._backward[eid.sink].discard(eid.source)
        else:
            assert isinstance(eid, base.UndirectedEdgeID)
            v1, v2 = eid.vertices
            if v1 != ignore:
                self._dual[v1].discard(v2)
            if v1 != v2 and v2 != ignore:
                self._dual[v2].discard(v1)

        # Decrement the counter
        self._edge_count -= 1

        return True

    def add_vertex_label(self, vid: base.VertexID, label: base.Label) -> None:
        self.add_vertex(vid)
        if vid in self._vertex_labels:
            self._vertex_labels[vid].add(label)
        else:
            self._vertex_labels[vid] = {label}

    def has_vertex_label(self, vid: base.VertexID, label: base.Label) -> bool:
        return label in self._vertex_labels.get(vid, ())

    def discard_vertex_label(self, vid: base.VertexID, label: base.Label) -> bool:
        labels = self._vertex_labels.get(vid, None)
        if labels is None:
            return False
        if label in labels:
            labels.discard(label)
            if not labels:
                del self._vertex_labels[vid]
            return True
        return False

    def iter_vertex_labels(self, vid: base.VertexID) -> Iterator[base.Label]:
        return iter(self._vertex_labels.get(vid, ()))

    def count_vertex_labels(self, vid: base.VertexID) -> int:
        return len(self._vertex_labels.get(vid, ()))

    def add_edge_label(self, eid: base.EdgeID, label: base.Label) -> None:
        self.add_edge(eid)
        if eid in self._edge_labels:
            self._edge_labels[eid].add(label)
        else:
            self._edge_labels[eid] = {label}

    def has_edge_label(self, eid: base.EdgeID, label: base.Label) -> bool:
        return label in self._edge_labels.get(eid, ())

    def discard_edge_label(self, eid: base.EdgeID, label: base.Label) -> bool:
        labels = self._edge_labels.get(eid, None)
        if labels is None:
            return False
        if label in labels:
            labels.discard(label)
            if not labels:
                del self._edge_labels[eid]
            return True
        return False

    def iter_edge_labels(self, eid: base.EdgeID) -> Iterator[base.Label]:
        return iter(self._edge_labels.get(eid, ()))

    def count_edge_labels(self, eid: base.EdgeID) -> int:
        return len(self._edge_labels.get(eid, ()))

    def get_vertex_data(self, vid: base.VertexID, key: Hashable) -> Any:
        if vid in self._vertex_data:
            return self._vertex_data[vid].get(key, None)
        return None

    def set_vertex_data(self, vid: base.VertexID, key: Hashable, value: Any) -> None:
        self.add_vertex(vid)
        if vid in self._vertex_data:
            data = self._vertex_data[vid]
        else:
            data = {}
            self._vertex_data[vid] = data
        data[key] = value

    def has_vertex_data(self, vid: base.VertexID, key: Hashable) -> bool:
        return key in self._vertex_data.get(vid, ())

    def discard_vertex_data(self, vid: base.VertexID, key: Hashable) -> bool:
        data = self._vertex_data.get(vid, None)
        if data is None:
            return False
        if key in data:
            del data[key]
            if not data:
                del self._vertex_data[vid]
            return True
        return False

    def iter_vertex_data_keys(self, vid: base.VertexID) -> Iterator[Hashable]:
        return iter(self._vertex_data.get(vid, ()))

    def count_vertex_data_keys(self, vid: base.VertexID) -> int:
        return len(self._vertex_data.get(vid, ()))

    def get_edge_data(self, eid: base.EdgeID, key: Hashable) -> Any:
        if eid in self._edge_data:
            return self._edge_data[eid].get(key, None)
        return None

    def set_edge_data(self, eid: base.EdgeID, key: Hashable, value: Any) -> None:
        self.add_edge(eid)
        if eid in self._edge_data:
            data = self._edge_data[eid]
        else:
            data = {}
            self._edge_data[eid] = data
        data[key] = value

    def has_edge_data(self, eid: base.EdgeID, key: Hashable) -> bool:
        return key in self._edge_data.get(eid, ())

    def discard_edge_data(self, eid: base.EdgeID, key: Hashable) -> bool:
        data = self._edge_data.get(eid, None)
        if data is None:
            return False
        if key in data:
            del data[key]
            if not data:
                del self._edge_data[eid]
            return True
        return False

    def iter_edge_data_keys(self, eid: base.EdgeID) -> Iterator[Hashable]:
        return iter(self._edge_data.get(eid, ()))

    def count_edge_data_keys(self, eid: base.EdgeID) -> int:
        return len(self._edge_data.get(eid, ()))
