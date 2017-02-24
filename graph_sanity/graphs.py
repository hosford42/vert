import collections.abc

from typing import Union, Iterator, Hashable, Any

import graph_sanity.stores.base as base
import graph_sanity.stores.memory as memory


VertexOrID = Union[base.VertexID, 'Vertex']
EdgeOrID = Union[base.EdgeID, 'Edge']


class GraphComponent:

    def __init__(self, graph_state: base.GraphStore):
        self._graph_store = graph_state

    @property
    def graph(self) -> Graph:
        return self._graph_store.graph

    def _to_vid(self, vertex: VertexOrID) -> base.VertexID:
        if isinstance(vertex, Vertex):
            if vertex.graph is not self.graph:
                raise ValueError(vertex)
            return vertex.vid
        else:
            return vertex

    def _to_eid(self, edge: EdgeOrID) -> base.EdgeID:
        if isinstance(edge, Edge):
            if edge.graph is not self.graph:
                raise ValueError(edge)
            return edge.eid
        else:
            return edge


class FullVertexSet(collections.abc.MutableSet, GraphComponent):
    def __contains__(self, vertex: VertexOrID) -> bool:
        vid = self._to_vid(vertex)
        return self._graph_store.has_vertex(vid)

    def __iter__(self) -> Iterator[Vertex]:
        for vid in self._graph_store.iter_vertices():
            yield Vertex(vid, self._graph_store)

    def __len__(self) -> int:
        return self._graph_store.count_vertices()

    def add(self, vertex: VertexOrID) -> Vertex:
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


class FullEdgeSet(collections.abc.MutableSet, GraphComponent):
    def __contains__(self, edge: EdgeOrID) -> bool:
        eid = self._to_eid(edge)
        return self._graph_store.has_edge(eid)

    def __iter__(self) -> Iterator[Edge]:
        for eid in self._graph_store.iter_edges():
            yield Edge(eid, self._graph_store)

    def __len__(self) -> int:
        return self._graph_store.count_edges()

    def add(self, edge: EdgeOrID) -> Edge:
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


class InboundEdgeSet(collections.abc.Set, GraphComponent):
    def __init__(self, vid: base.VertexID, graph_state: base.GraphStore):
        GraphComponent.__init__(self, graph_state)
        self._vid = vid

    def __contains__(self, edge: EdgeOrID) -> bool:
        eid = self._to_eid(edge)
        source, sink = eid
        if self._vid != sink:
            return False
        return self._graph_store.has_edge(eid)

    def __iter__(self) -> Iterator[Edge]:
        for source in self._graph_store.iter_sources(self._vid):
            eid = (source, self._vid)
            yield Edge(eid, self._graph_store)

    def __len__(self) -> int:
        return self._graph_store.count_sources(self._vid)

    def __getitem__(self, vertex: VertexOrID) -> Edge:
        vid = self._to_vid(vertex)
        eid = (vid, self._vid)
        return Edge(eid, self._graph_store)


class OutboundEdgeSet(collections.abc.Set, GraphComponent):
    def __init__(self, vid: base.VertexID, graph_state: base.GraphStore):
        GraphComponent.__init__(self, graph_state)
        self._vid = vid

    def __contains__(self, edge: EdgeOrID) -> bool:
        eid = self._to_eid(edge)
        source, sink = eid
        if self._vid != source:
            return False
        return self._graph_store.has_edge(eid)

    def __iter__(self) -> Iterator[Edge]:
        for sink in self._graph_store.iter_sinks(self._vid):
            eid = (self._vid, sink)
            yield Edge(eid, self._graph_store)

    def __len__(self) -> int:
        return self._graph_store.count_sinks(self._vid)

    def __getitem__(self, vertex: VertexOrID) -> Edge:
        vid = self._to_vid(vertex)
        eid = (self._vid, vid)
        return Edge(eid, self._graph_store)


class VertexLabelSet(collections.abc.MutableSet, GraphComponent):
    def __init__(self, vid: base.VertexID, graph_store: base.GraphStore):
        GraphComponent.__init__(self, graph_store)
        self._vid = vid

    def __contains__(self, label: base.Label) -> bool:
        return self._graph_store.has_vertex_label(self._vid, label)

    def __iter__(self) -> Iterator[base.Label]:
        return self._graph_store.iter_vertex_labels(self._vid)

    def __len__(self) -> int:
        return self._graph_store.count_vertex_labels(self._vid)

    def add(self, label: base.Label) -> None:
        self._graph_store.add_vertex_label(self._vid, label)

    def remove(self, label: base.Label) -> None:
        if not self._graph_store.has_vertex_label(self._vid, label):
            raise KeyError(label)
        self._graph_store.discard_vertex_label(self._vid, label)

    def discard(self, label: base.Label) -> None:
        self._graph_store.discard_vertex_label(self._vid, label)


class EdgeLabelSet(collections.abc.MutableSet, GraphComponent):
    def __init__(self, eid: base.EdgeID, graph_store: base.GraphStore):
        GraphComponent.__init__(self, graph_store)
        self._eid = eid

    def __contains__(self, label: base.Label) -> bool:
        return self._graph_store.has_edge_label(self._eid, label)

    def __iter__(self) -> Iterator[base.Label]:
        return self._graph_store.iter_edge_labels(self._eid)

    def __len__(self) -> int:
        return self._graph_store.count_edge_labels(self._eid)

    def add(self, label: base.Label) -> None:
        self._graph_store.add_edge_label(self._eid, label)

    def remove(self, label: base.Label) -> None:
        if not self._graph_store.has_edge_label(self._eid, label):
            raise KeyError(label)
        self._graph_store.discard_edge_label(self._eid, label)

    def discard(self, label: base.Label) -> None:
        self._graph_store.discard_edge_label(self._eid, label)


class VertexDataMap(collections.abc.MutableMapping, GraphComponent):

    def __init__(self, vid: base.VertexID, graph_store: base.GraphStore):
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

    def __init__(self, eid: base.EdgeID, graph_store: base.GraphStore):
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

    def __init__(self, vid: base.VertexID, graph_state: base.GraphStore):
        super().__init__(graph_state)
        self._vid = vid

    @property
    def vid(self) -> base.VertexID:
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

    def add(self) -> None:
        self._graph_store.add_vertex(self._vid)

    def remove(self) -> None:
        if not self._graph_store.has_vertex(self._vid):
            raise KeyError(self._vid)
        self._graph_store.discard_vertex(self._vid)

    def discard(self) -> None:
        self._graph_store.discard_vertex(self._vid)


class Edge(GraphComponent):
    def __init__(self, eid: base.EdgeID, graph_state: base.GraphStore):
        super().__init__(graph_state)
        self._eid = eid
        self._source, self._sink = eid

    @property
    def eid(self) -> base.EdgeID:
        return self._eid

    @property
    def source(self) -> Vertex:
        return Vertex(self._source, self._graph_store)

    @property
    def sink(self) -> Vertex:
        return Vertex(self._sink, self._graph_store)

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

    def add(self) -> None:
        self._graph_store.add_edge(self._eid)

    def remove(self) -> None:
        if not self._graph_store.has_edge(self._eid):
            raise KeyError(self._eid)
        self._graph_store.discard_edge(self._eid)

    def discard(self) -> None:
        self._graph_store.discard_edge(self._eid)


class Graph:

    def __init__(self):
        self._graph_store = memory.MemoryGraphStore(self)

    @property
    def vertices(self) -> FullVertexSet:
        return FullVertexSet(self._graph_store)

    @property
    def edges(self) -> FullEdgeSet:
        return FullEdgeSet(self._graph_store)
