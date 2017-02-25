from typing import Hashable, Any, Optional, Iterator


import graph_sanity.stores.base as base

# This cannot be aliased, because the graphs submodule depends on this one.
import graph_sanity.graphs


class MemoryGraphStore(base.GraphStore):

    def __init__(self, graph: 'graph_sanity.graphs.Graph'):
        super().__init__(graph)
        self.forward = {}
        self.backward = {}
        self.vertex_labels = {}
        self.edge_labels = {}
        self.vertex_data = {}
        self.edge_data = {}
        self.edge_count = 0

    def count_vertices(self) -> int:
        return len(self.forward)

    def count_edges(self) -> int:
        return self.edge_count

    def iter_vertices(self) -> Iterator[base.VertexID]:
        return iter(self.forward)

    def iter_edges(self) -> Iterator[base.EdgeID]:
        for source, sinks in self.forward.items():
            for sink in sinks:
                yield base.EdgeID(source, sink)

    def has_source(self, sink: base.VertexID) -> bool:
        return bool(self.backward.get(sink, ()))

    def has_sink(self, source: base.VertexID) -> bool:
        return bool(self.forward.get(source, ()))

    def iter_sources(self, sink: Optional[base.VertexID] = None) -> Iterator[base.VertexID]:
        if sink is None:
            for vid, sinks in self.forward.items():
                if sinks:
                    yield vid
        else:
            yield from self.backward.get(sink, ())

    def iter_sinks(self, source: Optional[base.VertexID] = None) -> Iterator[base.VertexID]:
        if source is None:
            for vid, sources in self.backward.items():
                if sources:
                    yield vid
        else:
            yield from self.forward.get(source, ())

    def count_sources(self, sink: Optional[base.VertexID] = None) -> int:
        if sink is None:
            return int(sum(bool(sinks) for sinks in self.forward.values()))
        else:
            return len(self.backward.get(sink, ()))

    def count_sinks(self, source: Optional[base.VertexID] = None) -> int:
        if source is None:
            return int(sum(bool(sources) for sources in self.backward.values()))
        else:
            return len(self.forward.get(source, ()))

    def has_vertex(self, vid: base.VertexID) -> bool:
        return vid in self.forward

    def has_edge(self, eid: base.EdgeID) -> bool:
        return eid.sink in self.forward.get(eid.source, ())

    def add_vertex(self, vid: base.VertexID) -> None:
        if vid not in self.forward:
            self.forward[vid] = set()
            self.backward[vid] = set()

    def add_edge(self, eid: base.EdgeID) -> None:
        if eid.sink in self.forward.get(eid.source, ()):
            return
        self.add_vertex(eid.source)
        self.add_vertex(eid.sink)
        self.forward[eid.source].add(eid.sink)
        self.backward[eid.sink].add(eid.source)
        self.edge_count += 1

    def discard_vertex(self, vid: base.VertexID):
        if vid not in self.forward:
            return

        # Remove labels and data
        if vid in self.vertex_labels:
            del self.vertex_labels[vid]
        if vid in self.vertex_data:
            del self.vertex_data[vid]

        # Remove all incident edges.
        for sink in self.forward[vid]:
            self.discard_edge(base.EdgeID(vid, sink), ignore=vid)
        for source in self.backward[vid]:
            self.discard_edge(base.EdgeID(source, vid), ignore=vid)

        # Remove the vertex itself
        del self.forward[vid]
        del self.backward[vid]

    def discard_edge(self, eid: base.EdgeID, ignore: Optional[base.VertexID] = None) -> None:
        # Remove labels and data.
        if eid in self.edge_labels:
            del self.edge_labels[eid]
        if eid in self.edge_data:
            del self.edge_data[eid]

        # Remove the edge itself
        if eid.source != ignore:
            self.forward[eid.source].discard(eid.sink)
        if eid.sink != ignore:
            self.backward[eid.sink].discard(eid.source)

        # Decrement the counter
        self.edge_count -= 1

    def add_vertex_label(self, vid: base.VertexID, label: base.Label) -> None:
        self.add_vertex(vid)
        if vid in self.vertex_labels:
            self.vertex_labels[vid].add(label)
        else:
            self.vertex_labels[vid] = {label}

    def has_vertex_label(self, vid: base.VertexID, label: base.Label) -> bool:
        return label in self.vertex_labels.get(vid, ())

    def discard_vertex_label(self, vid: base.VertexID, label: base.Label) -> None:
        labels = self.vertex_labels.get(vid, None)
        if labels is None:
            return
        labels.discard(label)
        if not labels:
            del self.vertex_labels[vid]

    def iter_vertex_labels(self, vid: base.VertexID) -> Iterator[base.Label]:
        return iter(self.vertex_labels.get(vid, ()))

    def count_vertex_labels(self, vid: base.VertexID) -> int:
        return len(self.vertex_labels.get(vid, ()))

    def add_edge_label(self, eid: base.EdgeID, label: base.Label) -> None:
        self.add_edge(eid)
        if eid in self.edge_labels:
            self.edge_labels[eid].add(label)
        else:
            self.edge_labels[eid] = {label}

    def has_edge_label(self, eid: base.EdgeID, label: base.Label) -> bool:
        return label in self.edge_labels.get(eid, ())

    def discard_edge_label(self, eid: base.EdgeID, label: base.Label) -> None:
        labels = self.edge_labels.get(eid, None)
        if labels is None:
            return
        labels.discard(label)
        if not labels:
            del self.edge_labels[eid]

    def iter_edge_labels(self, eid: base.EdgeID) -> Iterator[base.Label]:
        return iter(self.edge_labels.get(eid, ()))

    def count_edge_labels(self, eid: base.EdgeID) -> int:
        return len(self.edge_labels.get(eid, ()))

    def get_vertex_data(self, vid: base.VertexID, key: Hashable) -> Any:
        if vid in self.vertex_data:
            return self.vertex_data[vid].get(key, None)

    def set_vertex_data(self, vid: base.VertexID, key: Hashable, value: Any) -> None:
        self.add_vertex(vid)
        if vid in self.vertex_data:
            data = self.vertex_data[vid]
        else:
            data = {}
            self.vertex_data[vid] = data
        data[key] = value

    def has_vertex_data(self, vid: base.VertexID, key: Hashable) -> bool:
        return key in self.vertex_data.get(vid, ())

    def discard_vertex_data(self, vid: base.VertexID, key: Hashable) -> None:
        data = self.vertex_data.get(vid, None)
        if data is None:
            return
        if key in data:
            del data[key]
        if not data:
            del self.vertex_data[vid]

    def iter_vertex_data_keys(self, vid: base.VertexID) -> Iterator[Hashable]:
        return iter(self.vertex_data.get(vid, ()))

    def count_vertex_data_keys(self, vid: base.VertexID) -> int:
        return len(self.vertex_data.get(vid, ()))

    def get_edge_data(self, eid: base.EdgeID, key: Hashable) -> Any:
        if eid in self.edge_data:
            return self.edge_data[eid].get(key, None)

    def set_edge_data(self, eid: base.EdgeID, key: Hashable, value: Any) -> None:
        self.add_edge(eid)
        if eid in self.edge_data:
            data = self.edge_data[eid]
        else:
            data = {}
            self.edge_data[eid] = data
        data[key] = value

    def has_edge_data(self, eid: base.EdgeID, key: Hashable) -> bool:
        return key in self.edge_data.get(key, ())

    def discard_edge_data(self, eid: base.EdgeID, key: Hashable) -> None:
        data = self.edge_data.get(eid, None)
        if data is None:
            return
        if key in data:
            del data[key]
        if not data:
            del self.edge_data[eid]

    def iter_edge_data_keys(self, eid: base.EdgeID) -> Iterator[Hashable]:
        return iter(self.edge_data.get(eid, ()))

    def count_edge_data_keys(self, eid: base.EdgeID) -> int:
        return len(self.edge_data.get(eid, ()))
