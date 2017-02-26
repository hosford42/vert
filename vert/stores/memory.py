# -*- coding: utf-8 -*-

# Copyright 2017 Aaron M. Hosford
# See LICENSE.txt for licensing information.

from typing import Hashable, Any, Optional, Iterator


import vert.stores.base as base


__all__ = [
    'MemoryGraphStore',
]


class MemoryGraphStore(base.GraphStore):

    def __init__(self):
        self._forward = {}
        self._backward = {}
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
                yield base.EdgeID(source, sink)

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
        return eid.sink in self._forward.get(eid.source, ())

    def add_vertex(self, vid: base.VertexID) -> None:
        if vid not in self._forward:
            self._forward[vid] = set()
            self._backward[vid] = set()

    def add_edge(self, eid: base.EdgeID) -> None:
        if eid.sink in self._forward.get(eid.source, ()):
            return
        self.add_vertex(eid.source)
        self.add_vertex(eid.sink)
        self._forward[eid.source].add(eid.sink)
        self._backward[eid.sink].add(eid.source)
        self._edge_count += 1

    def discard_vertex(self, vid: base.VertexID):
        if vid not in self._forward:
            return

        # Remove labels and data
        if vid in self._vertex_labels:
            del self._vertex_labels[vid]
        if vid in self._vertex_data:
            del self._vertex_data[vid]

        # Remove all incident edges.
        for sink in self._forward[vid]:
            self.discard_edge(base.EdgeID(vid, sink), ignore=vid)
        for source in self._backward[vid]:
            self.discard_edge(base.EdgeID(source, vid), ignore=vid)

        # Remove the vertex itself
        del self._forward[vid]
        del self._backward[vid]

    def discard_edge(self, eid: base.EdgeID, ignore: Optional[base.VertexID] = None) -> None:
        # Remove labels and data.
        if eid in self._edge_labels:
            del self._edge_labels[eid]
        if eid in self._edge_data:
            del self._edge_data[eid]

        # Remove the edge itself
        if eid.source != ignore:
            self._forward[eid.source].discard(eid.sink)
        if eid.sink != ignore:
            self._backward[eid.sink].discard(eid.source)

        # Decrement the counter
        self._edge_count -= 1

    def add_vertex_label(self, vid: base.VertexID, label: base.Label) -> None:
        self.add_vertex(vid)
        if vid in self._vertex_labels:
            self._vertex_labels[vid].add(label)
        else:
            self._vertex_labels[vid] = {label}

    def has_vertex_label(self, vid: base.VertexID, label: base.Label) -> bool:
        return label in self._vertex_labels.get(vid, ())

    def discard_vertex_label(self, vid: base.VertexID, label: base.Label) -> None:
        labels = self._vertex_labels.get(vid, None)
        if labels is None:
            return
        labels.discard(label)
        if not labels:
            del self._vertex_labels[vid]

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

    def discard_edge_label(self, eid: base.EdgeID, label: base.Label) -> None:
        labels = self._edge_labels.get(eid, None)
        if labels is None:
            return
        labels.discard(label)
        if not labels:
            del self._edge_labels[eid]

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

    def discard_vertex_data(self, vid: base.VertexID, key: Hashable) -> None:
        data = self._vertex_data.get(vid, None)
        if data is None:
            return
        if key in data:
            del data[key]
        if not data:
            del self._vertex_data[vid]

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

    def discard_edge_data(self, eid: base.EdgeID, key: Hashable) -> None:
        data = self._edge_data.get(eid, None)
        if data is None:
            return
        if key in data:
            del data[key]
        if not data:
            del self._edge_data[eid]

    def iter_edge_data_keys(self, eid: base.EdgeID) -> Iterator[Hashable]:
        return iter(self._edge_data.get(eid, ()))

    def count_edge_data_keys(self, eid: base.EdgeID) -> int:
        return len(self._edge_data.get(eid, ()))
