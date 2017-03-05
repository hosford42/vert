# -*- coding: utf-8 -*-

# Copyright 2017 Aaron M. Hosford
# See LICENSE.txt for licensing information.

from typing import NewType, Hashable, Any, Optional, Iterator, NamedTuple, Union


__all__ = [
    'GraphStore',
    'VertexID',
    'EdgeID',
    'Label',
]

VertexID = NewType('VertexID', Union[int, str, bytes])
EdgeID = NamedTuple('EdgeId', [('source', VertexID), ('sink', VertexID)])
Label = NewType('Label', Hashable)


class GraphStore:
    """
    The abstract interface for graph stores. All graph stores must support this interface in order to be accessed via
    the first-class object interface (the Graph, Vertex, and Edge classes).
    """

    @property
    def is_open(self) -> bool:
        """A Boolean value indicating whether the graph store is open. When a graph store is closed, it cannot be
        accessed."""
        return True  # By default, always open

    def close(self) -> None:
        """Perform a proper shutdown of the graph store, ensuring that if the graph store is persistent, it will be
        in a consistent on-disk state."""
        pass  # By default, a no-op

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return False

    def count_vertices(self) -> int:
        """Return the total number of vertices in the graph."""
        raise NotImplementedError()

    def count_edges(self) -> int:
        """Return the total number of edges in the graph."""
        raise NotImplementedError()

    def iter_vertices(self) -> Iterator[VertexID]:
        """Return an iterator over the IDs of every vertex in the graph."""
        raise NotImplementedError()

    def iter_edges(self) -> Iterator[EdgeID]:
        """Return an iterator over the IDs of every edge in the graph."""
        raise NotImplementedError()

    def has_source(self, sink: VertexID) -> bool:
        """Return a Boolean value indicating whether the given vertex has at least one inbound edge."""
        raise NotImplementedError()

    def has_sink(self, source: VertexID) -> bool:
        """Return a Boolean value indicating whether the given vertex has at least one outbound edge."""
        raise NotImplementedError()

    def iter_sources(self, sink: Optional[VertexID] = None) -> Iterator[VertexID]:
        """Return an iterator over the IDs of every vertex which is linked to this vertex via an inbound edge."""
        raise NotImplementedError()

    def iter_sinks(self, source: Optional[VertexID] = None) -> Iterator[VertexID]:
        """Return an iterator over the IDs of every vertex which is linked to from this vertex via an outbound edge."""
        raise NotImplementedError()

    def count_sources(self, sink: Optional[VertexID] = None) -> int:
        """Return the number of inbound edges to this vertex."""
        raise NotImplementedError()

    def count_sinks(self, source: Optional[VertexID] = None) -> int:
        """Return the number of outbound edges from this vertex."""
        raise NotImplementedError()

    def has_vertex(self, vid: VertexID) -> bool:
        """Return whether the given ID has a vertex associated with it in the graph."""
        raise NotImplementedError()

    def has_edge(self, eid: EdgeID) -> bool:
        """Return whether the given ID has an edge associated with it in the graph."""
        raise NotImplementedError()

    def add_vertex(self, vid: VertexID) -> None:
        """
        Add a vertex to the graph associated with this ID. If a vertex with the given ID already exists, do nothing.
        """
        raise NotImplementedError()

    def add_edge(self, eid: EdgeID) -> None:
        """
        Add an edge to the graph associated with this ID. If an edge with the given ID already exists, do nothing. If
        either the source or sink vertex of the edge does not exist, add it first.
        """
        raise NotImplementedError()

    def discard_vertex(self, vid: VertexID) -> None:
        """
        Remove the vertex associated with this ID from the graph. If such a vertex does not exist, do nothing. Any
        incident edges to the vertex are also removed.
        """
        raise NotImplementedError()

    def discard_edge(self, eid: EdgeID, ignore: Optional[VertexID] = None) -> None:
        """
        Remove the edge associated with this ID from the graph. If such an edge does not exist, do nothing. The source
        and sink vertex are not removed.
        """
        raise NotImplementedError()

    def add_vertex_label(self, vid: VertexID, label: Label) -> None:
        raise NotImplementedError()

    def has_vertex_label(self, vid: VertexID, label: Label) -> bool:
        raise NotImplementedError()

    def discard_vertex_label(self, vid: VertexID, label: Label) -> None:
        raise NotImplementedError()

    def iter_vertex_labels(self, vid: VertexID) -> Iterator[Label]:
        raise NotImplementedError()

    def count_vertex_labels(self, vid: VertexID) -> int:
        raise NotImplementedError()

    def add_edge_label(self, eid: EdgeID, label: Label) -> None:
        raise NotImplementedError()

    def has_edge_label(self, eid: EdgeID, label: Label) -> bool:
        raise NotImplementedError()

    def discard_edge_label(self, eid: EdgeID, label: Label) -> None:
        raise NotImplementedError()

    def iter_edge_labels(self, eid: EdgeID) -> Iterator[Label]:
        raise NotImplementedError()

    def count_edge_labels(self, eid: EdgeID) -> int:
        raise NotImplementedError()

    def get_vertex_data(self, vid: VertexID, key: Hashable) -> Any:
        raise NotImplementedError()

    def set_vertex_data(self, vid: VertexID, key: Hashable, value: Any) -> None:
        raise NotImplementedError()

    def has_vertex_data(self, vid: VertexID, key: Hashable) -> bool:
        raise NotImplementedError()

    def discard_vertex_data(self, vid: VertexID, key: Hashable) -> None:
        raise NotImplementedError()

    def iter_vertex_data_keys(self, vid: VertexID) -> Iterator[Hashable]:
        raise NotImplementedError()

    def count_vertex_data_keys(self, vid: VertexID) -> int:
        raise NotImplementedError()

    def get_edge_data(self, eid: EdgeID, key: Hashable) -> Any:
        raise NotImplementedError()

    def set_edge_data(self, eid: EdgeID, key: Hashable, value: Any) -> None:
        raise NotImplementedError()

    def has_edge_data(self, eid: EdgeID, key: Hashable) -> bool:
        raise NotImplementedError()

    def discard_edge_data(self, eid: EdgeID, key: Hashable) -> None:
        raise NotImplementedError()

    def iter_edge_data_keys(self, eid: EdgeID) -> Iterator[Hashable]:
        raise NotImplementedError()

    def count_edge_data_keys(self, eid: EdgeID) -> int:
        raise NotImplementedError()
