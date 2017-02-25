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

    def count_vertices(self) -> int:
        raise NotImplementedError()

    def count_edges(self) -> int:
        raise NotImplementedError()

    def iter_vertices(self) -> Iterator[VertexID]:
        raise NotImplementedError()

    def iter_edges(self) -> Iterator[EdgeID]:
        raise NotImplementedError()

    def has_source(self, sink: VertexID) -> bool:
        raise NotImplementedError()

    def has_sink(self, source: VertexID) -> bool:
        raise NotImplementedError()

    def iter_sources(self, sink: Optional[VertexID] = None) -> Iterator[VertexID]:
        raise NotImplementedError()

    def iter_sinks(self, source: Optional[VertexID] = None) -> Iterator[VertexID]:
        raise NotImplementedError()

    def count_sources(self, sink: Optional[VertexID] = None) -> int:
        raise NotImplementedError()

    def count_sinks(self, source: Optional[VertexID] = None) -> int:
        raise NotImplementedError()

    def has_vertex(self, vid: VertexID) -> bool:
        raise NotImplementedError()

    def has_edge(self, eid: EdgeID) -> bool:
        raise NotImplementedError()

    def add_vertex(self, vid: VertexID) -> None:
        raise NotImplementedError()

    def add_edge(self, eid: EdgeID) -> None:
        raise NotImplementedError()

    def discard_vertex(self, vid: VertexID):
        raise NotImplementedError()

    def discard_edge(self, eid: EdgeID, ignore: Optional[VertexID] = None) -> None:
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
