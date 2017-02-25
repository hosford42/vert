import ast
import dbm
import json
from typing import Hashable, Any, Optional, Iterator, Union, MutableMapping


import vert.stores.base as base

# This cannot be aliased, because the graphs submodule depends on this one.
import vert.graphs


VERTEX_COUNT_KEY = b'cv'
EDGE_COUNT_KEY = b'ce'
VID_PREFIX = b'v'
EID_PREFIX = b'e'

LABEL_INDEX = 0
DATA_INDEX = 1
SOURCES_INDEX = 2
SINKS_INDEX = 3

# VertexData = NamedTuple(
#     'VertexData',
#     [
#         ('forward', List[base.VertexID]),
#         ('backward', List[base.VertexID]),
#         ('labels', List[base.Label]),
#         ('data', )])
# EdgeData = NamedTuple('EdgeData', [('source',), ('sink',), ('labels',), ('data',)])


class DBMGraphStore(base.GraphStore):

    def __init__(self, path: Union[str, MutableMapping[bytes, bytes]], graph: 'vert.graphs.Graph'):
        super().__init__(graph)
        if isinstance(path, str):
            self._close_db = True
            self._db = dbm.open(path, 'rw')
        else:
            self._close_db = False
            self._db = path

    def __del__(self):
        if self._close_db:
            # noinspection PyUnresolvedReferences
            self._db.close()

    @staticmethod
    def _encode_key(key: Any, prefix: bytes) -> bytes:
        return prefix + repr(key).encode()

    @staticmethod
    def _decode_key(encoded_key: bytes, prefix: bytes) -> Any:
        assert encoded_key.startswith(prefix)
        return ast.literal_eval(encoded_key[len(prefix):].decode())

    def _read_data(self, key, prefix):
        return json.loads(self._db[self._encode_key(key, prefix)].decode())

    def _write_data(self, key, prefix, data):
        self._db[self._encode_key(key, prefix)] = json.dumps(data).encode()

    def _del_data(self, key, prefix):
        del self._db[self._encode_key(key, prefix)]

    def count_vertices(self) -> int:
        return int(self._db[VERTEX_COUNT_KEY].decode())

    def count_edges(self) -> int:
        return int(self._db[EDGE_COUNT_KEY].decode())

    def iter_vertices(self) -> Iterator[base.VertexID]:
        for key in self._db:
            if key.startswith(VID_PREFIX):
                yield self._decode_key(key, VID_PREFIX)

    def iter_edges(self) -> Iterator[base.EdgeID]:
        for key in self._db:
            if key.startswith(EID_PREFIX):
                yield self._decode_key(key, EID_PREFIX)

    def has_source(self, sink: base.VertexID) -> bool:
        try:
            return bool(self._read_data(sink, VID_PREFIX)[SOURCES_INDEX])
        except KeyError:
            return False

    def has_sink(self, source: base.VertexID) -> bool:
        try:
            return bool(self._read_data(source, VID_PREFIX)[SINKS_INDEX])
        except KeyError:
            return False

    def iter_sources(self, sink: Optional[base.VertexID] = None) -> Iterator[base.VertexID]:
        if sink is None:
            for key in self.iter_vertices():
                if self._read_data(key, VID_PREFIX)[SINKS_INDEX]:
                    yield key
        else:
            try:
                yield from self._read_data(sink, VID_PREFIX)[SOURCES_INDEX]
            except KeyError:
                pass

    def iter_sinks(self, source: Optional[base.VertexID] = None) -> Iterator[base.VertexID]:
        if source is None:
            for key in self.iter_vertices():
                if self._read_data(key, VID_PREFIX)[SOURCES_INDEX]:
                    yield key
        else:
            try:
                yield from self._read_data(source, VID_PREFIX)[SINKS_INDEX]
            except KeyError:
                pass

    def count_sources(self, sink: Optional[base.VertexID] = None) -> int:
        if sink is None:
            count = 0
            for key in self.iter_vertices():
                if self._read_data(key, VID_PREFIX)[SINKS_INDEX]:
                    count += 1
            return count
        else:
            try:
                return len(self._read_data(sink, VID_PREFIX)[SOURCES_INDEX])
            except KeyError:
                pass

    def count_sinks(self, source: Optional[base.VertexID] = None) -> int:
        if source is None:
            count = 0
            for key in self.iter_vertices():
                if self._read_data(key, VID_PREFIX)[SOURCES_INDEX]:
                    count += 1
            return count
        else:
            try:
                return len(self._read_data(source, VID_PREFIX)[SINKS_INDEX])
            except KeyError:
                pass

    def has_vertex(self, vid: base.VertexID) -> bool:
        return self._encode_key(vid, VID_PREFIX) in self._db

    def has_edge(self, eid: base.EdgeID) -> bool:
        return self._encode_key(eid, EID_PREFIX) in self._db

    def add_vertex(self, vid: base.VertexID) -> None:
        if not self.has_vertex(vid):
            data = [
                [],  # Labels
                {},  # Data
                [],  # Sources
                [],  # Sinks
            ]
            self._write_data(vid, VID_PREFIX, data)
            self._db[VERTEX_COUNT_KEY] += 1

    def add_edge(self, eid: base.EdgeID) -> None:
        if not self.has_edge(eid):
            self.add_vertex(eid.source)
            self.add_vertex(eid.sink)
            data = [
                [],  # Labels,
                {},  # Data
            ]
            self._write_data(eid, EID_PREFIX, data)
            self._db[EDGE_COUNT_KEY] += 1

    def discard_vertex(self, vid: base.VertexID):
        if self.has_vertex(vid):
            _, _, sources, sinks = self._read_data(vid, VID_PREFIX)

            for source in sources:
                self.discard_edge(base.EdgeID(source, vid), ignore=vid)
            for sink in sinks:
                self.discard_edge(base.EdgeID(vid, sink), ignore=vid)

            self._del_data(vid, VID_PREFIX)
            self._db[VERTEX_COUNT_KEY] -= 1

    def discard_edge(self, eid: base.EdgeID, ignore: Optional[base.VertexID] = None) -> None:
        if self.has_edge(eid):
            if eid.source != ignore:
                source_data = self._read_data(eid.source, VID_PREFIX)
                source_data[SINKS_INDEX].remove(eid.sink)
                self._write_data(eid.source, VID_PREFIX, source_data)

            if eid.sink != ignore:
                sink_data = self._read_data(eid.sink, VID_PREFIX)
                sink_data[SOURCES_INDEX].remove(eid.source)
                self._write_data(eid.sink, VID_PREFIX, sink_data)

            self._del_data(eid, EID_PREFIX)
            self._db[EDGE_COUNT_KEY] -= 1

    def add_vertex_label(self, vid: base.VertexID, label: base.Label) -> None:
        self.add_vertex(vid)
        data = self._read_data(vid, VID_PREFIX)
        if label not in data[LABEL_INDEX]:
            data[LABEL_INDEX].append(label)
            self._write_data(vid, VID_PREFIX, data)

    def has_vertex_label(self, vid: base.VertexID, label: base.Label) -> bool:
        try:
            return label in self._read_data(vid, VID_PREFIX)[LABEL_INDEX]
        except KeyError:
            return False

    def discard_vertex_label(self, vid: base.VertexID, label: base.Label) -> None:
        try:
            data = self._read_data(vid, VID_PREFIX)
        except KeyError:
            return  # Nothing to do
        if label in data[LABEL_INDEX]:
            data[LABEL_INDEX].remove(label)
            self._write_data(vid, VID_PREFIX, data)

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

    def set_edge_data(self, eid: base.EdgeID, key: Hashable, value: Any) -> None:
        self.add_edge(eid)
        if eid in self._edge_data:
            data = self._edge_data[eid]
        else:
            data = {}
            self._edge_data[eid] = data
        data[key] = value

    def has_edge_data(self, eid: base.EdgeID, key: Hashable) -> bool:
        return key in self._edge_data.get(key, ())

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
