import ast
import dbm
import json
import time
from typing import Hashable, Any, Optional, Iterator, Union, MutableMapping, NewType


import vert.stores.base as base

# This cannot be aliased, because the graphs submodule depends on this one.
import vert.graphs


__all__ = [
    'DBMGraphStore',
]


VertexData = NewType('VertexData', list)
EdgeData = NewType('EdgeData', list)

VERTEX_COUNT_KEY = b'cv'
EDGE_COUNT_KEY = b'ce'
VID_PREFIX = b'v'
EID_PREFIX = b'e'

LABEL_INDEX = 0
DATA_INDEX = 1
SOURCES_INDEX = 2
SINKS_INDEX = 3


class DBMGraphStore(base.GraphStore):

    def __init__(self, path: Union[str, MutableMapping[bytes, bytes]], graph: 'vert.graphs.Graph',
                 v_cache_size: int = 100, e_cache_size: int = 100):
        super().__init__(graph)

        self._auto_close_db = False
        self._is_open = True

        self._v_cache_size = v_cache_size
        self._v_cache = {}
        self._v_cache_times = {}
        self._v_cache_dirty = set()

        self._e_cache_size = e_cache_size
        self._e_cache = {}
        self._e_cache_times = {}
        self._e_cache_dirty = set()

        if isinstance(path, str):
            self._auto_close_db = True
            self._db = dbm.open(path, mode='c')
        else:
            self._db = path

    def __del__(self) -> None:
        self.close()

    def close(self):
        if not self._is_open:
            return
        self.flush()
        if self._auto_close_db:
            # noinspection PyUnresolvedReferences
            self._db.close()
        self._is_open = False

    @property
    def vertex_cache_size(self) -> int:
        return self._v_cache_size

    @vertex_cache_size.setter
    def vertex_cache_size(self, value: int) -> None:
        assert value >= 0
        self._v_cache_size = value
        while len(self._v_cache) > self._v_cache_size:
            self._retire_vertex()

    @property
    def edge_cache_size(self) -> int:
        return self._e_cache_size

    @edge_cache_size.setter
    def edge_cache_size(self, value: int) -> None:
        assert value >= 0
        self._e_cache_size = value
        while len(self._e_cache) > self._e_cache_size:
            self._retire_vertex()

    @staticmethod
    def _encode_key(key: Any, prefix: bytes) -> bytes:
        return prefix + repr(key).encode()

    @staticmethod
    def _decode_key(encoded_key: bytes, prefix: bytes) -> Any:
        assert encoded_key.startswith(prefix)
        return ast.literal_eval(encoded_key[len(prefix):].decode())

    def _immediate_read_data(self, key: Any, prefix: bytes) -> Any:
        assert self._is_open
        return json.loads(self._db[self._encode_key(key, prefix)].decode())

    def _immediate_write_data(self, key: Any, prefix: bytes, data: Any) -> None:
        assert self._is_open
        self._db[self._encode_key(key, prefix)] = json.dumps(data).encode()

    def _immediate_del_data(self, key: Any, prefix: bytes) -> None:
        assert self._is_open
        del self._db[self._encode_key(key, prefix)]

    def _retire_vertex(self, vid: Optional[base.VertexID] = None) -> None:
        if vid is None:
            vid = min(self._v_cache_times, key=self._v_cache_times.get)
        data = self._v_cache.pop(vid)
        if vid in self._v_cache_dirty:
            self._immediate_write_data(vid, VID_PREFIX, data)
            self._v_cache_dirty.remove(vid)
        del self._v_cache_times[vid]

    def _retire_edge(self, eid: Optional[base.EdgeID] = None) -> None:
        if eid is None:
            eid = min(self._e_cache_times, key=self._e_cache_times.get)
        data = self._e_cache.pop(eid)
        if eid in self._e_cache_dirty:
            self._immediate_write_data(eid, EID_PREFIX, data)
            self._e_cache_dirty.remove(eid)
        del self._e_cache_times[eid]

    def _read_vertex(self, vid: base.VertexID) -> VertexData:
        assert self._is_open
        if not self._v_cache_size:
            return self._immediate_read_data(vid, VID_PREFIX)

        self._v_cache_times[vid] = time.time()
        if vid in self._v_cache:
            return self._v_cache[vid]
        data = self._immediate_read_data(vid, VID_PREFIX)
        self._v_cache[vid] = data
        if len(self._v_cache) > self._v_cache_size:
            self._retire_vertex()
        return data

    def _write_vertex(self, vid: base.VertexID, data: VertexData):
        assert self._is_open
        if not self._v_cache_size:
            self._immediate_write_data(vid, EID_PREFIX, data)
            return

        self._v_cache_times[vid] = time.time()
        self._v_cache_dirty.add(vid)
        if self._v_cache.get(vid, None) is data:
            return  # Nothing to do.
        self._v_cache[vid] = data
        if len(self._v_cache) > self._v_cache_size:
            self._retire_vertex()

    def _del_vertex(self, vid: base.VertexID):
        assert self._is_open
        # No caching for deletions; it doesn't make sense to, since nothing will be accessing it again.
        del self._v_cache[vid]
        del self._v_cache_times[vid]
        self._v_cache_dirty.discard(vid)
        self._immediate_del_data(vid, VID_PREFIX)

    def _read_edge(self, eid: base.EdgeID) -> EdgeData:
        assert self._is_open
        if not self._e_cache_size:
            return self._immediate_read_data(eid, EID_PREFIX)

        self._e_cache_times[eid] = time.time()
        if eid in self._e_cache:
            return self._e_cache[eid]
        data = self._immediate_read_data(eid, EID_PREFIX)
        self._e_cache[eid] = data
        if len(self._e_cache) > self._e_cache_size:
            self._retire_vertex()

    def _write_edge(self, eid: base.EdgeID, data: EdgeData) -> None:
        assert self._is_open
        if not self._e_cache_size:
            self._immediate_write_data(eid, EID_PREFIX, data)
            return

        self._e_cache_times[eid] = time.time()
        self._e_cache_dirty.add(eid)
        if self._e_cache.get(eid, None) is data:
            return   # Nothing to do.
        self._e_cache[eid] = data
        if len(self._e_cache) > self._e_cache_size:
            self._retire_edge()

    def _del_edge(self, eid: base.EdgeID) -> None:
        assert self._is_open
        # No caching for deletions; it doesn't make sense to, since nothing will be accessing it again.
        del self._e_cache[eid]
        del self._e_cache_times[eid]
        self._e_cache_dirty.discard(eid)
        self._immediate_del_data(eid, EID_PREFIX)

    def flush(self):
        for vid in sorted(self._v_cache_times, key=self._v_cache_times.get):
            self._retire_vertex(vid)
        for eid in sorted(self._e_cache_times, key=self._e_cache_times.get):
            self._retire_edge(eid)

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
            return bool(self._retire_vertex(sink)[SOURCES_INDEX])
        except KeyError:
            return False

    def has_sink(self, source: base.VertexID) -> bool:
        try:
            return bool(self._read_vertex(source)[SINKS_INDEX])
        except KeyError:
            return False

    def iter_sources(self, sink: Optional[base.VertexID] = None) -> Iterator[base.VertexID]:
        if sink is None:
            for key in self.iter_vertices():
                if self._read_vertex(key)[SINKS_INDEX]:
                    yield key
        else:
            try:
                yield from self._read_vertex(sink)[SOURCES_INDEX]
            except KeyError:
                pass

    def iter_sinks(self, source: Optional[base.VertexID] = None) -> Iterator[base.VertexID]:
        if source is None:
            for key in self.iter_vertices():
                if self._read_vertex(key)[SOURCES_INDEX]:
                    yield key
        else:
            try:
                yield from self._read_vertex(source)[SINKS_INDEX]
            except KeyError:
                pass

    def count_sources(self, sink: Optional[base.VertexID] = None) -> int:
        if sink is None:
            count = 0
            for key in self.iter_vertices():
                if self._read_vertex(key)[SINKS_INDEX]:
                    count += 1
            return count
        else:
            try:
                return len(self._read_vertex(sink)[SOURCES_INDEX])
            except KeyError:
                pass

    def count_sinks(self, source: Optional[base.VertexID] = None) -> int:
        if source is None:
            count = 0
            for key in self.iter_vertices():
                if self._read_vertex(key)[SOURCES_INDEX]:
                    count += 1
            return count
        else:
            try:
                return len(self._read_vertex(source)[SINKS_INDEX])
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
            self._write_vertex(vid, data)
            self._db[VERTEX_COUNT_KEY] += 1

    def add_edge(self, eid: base.EdgeID) -> None:
        if not self.has_edge(eid):
            self.add_vertex(eid.source)
            self.add_vertex(eid.sink)
            data = [
                [],  # Labels,
                {},  # Data
            ]
            self._write_edge(eid, data)
            self._db[EDGE_COUNT_KEY] += 1

    def discard_vertex(self, vid: base.VertexID):
        if self.has_vertex(vid):
            _, _, sources, sinks = self._read_vertex(vid)

            for source in sources:
                self.discard_edge(base.EdgeID(source, vid), ignore=vid)
            for sink in sinks:
                self.discard_edge(base.EdgeID(vid, sink), ignore=vid)

            self._del_vertex(vid)
            self._db[VERTEX_COUNT_KEY] -= 1

    def discard_edge(self, eid: base.EdgeID, ignore: Optional[base.VertexID] = None) -> None:
        if self.has_edge(eid):
            if eid.source != ignore:
                source_data = self._read_vertex(eid.source)
                source_data[SINKS_INDEX].remove(eid.sink)
                self._write_vertex(eid.source, source_data)

            if eid.sink != ignore:
                sink_data = self._read_vertex(eid.sink)
                sink_data[SOURCES_INDEX].remove(eid.source)
                self._write_vertex(eid.sink, sink_data)

            self._del_edge(eid)
            self._db[EDGE_COUNT_KEY] -= 1

    def add_vertex_label(self, vid: base.VertexID, label: base.Label) -> None:
        self.add_vertex(vid)
        data = self._read_vertex(vid)
        if label not in data[LABEL_INDEX]:
            data[LABEL_INDEX].append(label)
            self._write_vertex(vid, data)

    def has_vertex_label(self, vid: base.VertexID, label: base.Label) -> bool:
        try:
            return label in self._read_vertex(vid)[LABEL_INDEX]
        except KeyError:
            return False

    def discard_vertex_label(self, vid: base.VertexID, label: base.Label) -> None:
        try:
            data = self._read_vertex(vid)
        except KeyError:
            return  # Nothing to do
        if label in data[LABEL_INDEX]:
            data[LABEL_INDEX].remove(label)
            self._write_vertex(vid, data)

    def iter_vertex_labels(self, vid: base.VertexID) -> Iterator[base.Label]:
        try:
            return iter(self._read_vertex(vid)[LABEL_INDEX])
        except KeyError:
            return iter(())

    def count_vertex_labels(self, vid: base.VertexID) -> int:
        try:
            return len(self._read_vertex(vid)[LABEL_INDEX])
        except KeyError:
            return 0

    def add_edge_label(self, eid: base.EdgeID, label: base.Label) -> None:
        self.add_edge(eid)
        data = self._read_edge(eid)
        if label not in data[LABEL_INDEX]:
            data[LABEL_INDEX].append(label)
            self._write_edge(eid, data)

    def has_edge_label(self, eid: base.EdgeID, label: base.Label) -> bool:
        try:
            return label in self._read_edge(eid)[LABEL_INDEX]
        except KeyError:
            return False

    def discard_edge_label(self, eid: base.EdgeID, label: base.Label) -> None:
        try:
            data = self._read_edge(eid)
        except KeyError:
            return  # Nothing to do
        if label in data[LABEL_INDEX]:
            data[LABEL_INDEX].remove(label)
            self._write_edge(eid, data)

    def iter_edge_labels(self, eid: base.EdgeID) -> Iterator[base.Label]:
        try:
            return iter(self._read_edge(eid)[LABEL_INDEX])
        except KeyError:
            return iter(())

    def count_edge_labels(self, eid: base.EdgeID) -> int:
        try:
            return len(self._read_edge(eid)[LABEL_INDEX])
        except KeyError:
            return 0

    def get_vertex_data(self, vid: base.VertexID, key: Hashable) -> Any:
        try:
            return self._read_vertex(vid)[DATA_INDEX].get(key, None)
        except KeyError:
            return None

    def set_vertex_data(self, vid: base.VertexID, key: Hashable, value: Any) -> None:
        self.add_vertex(vid)
        data = self._read_vertex(vid)
        data[DATA_INDEX][key] = value
        self._write_vertex(vid, data)

    def has_vertex_data(self, vid: base.VertexID, key: Hashable) -> bool:
        try:
            return key in self._read_vertex(vid)[DATA_INDEX]
        except KeyError:
            return False

    def discard_vertex_data(self, vid: base.VertexID, key: Hashable) -> None:
        try:
            data = self._read_vertex(vid)
            del data[DATA_INDEX][key]
        except KeyError:
            return  # Nothing to do
        else:
            self._write_vertex(vid, data)

    def iter_vertex_data_keys(self, vid: base.VertexID) -> Iterator[Hashable]:
        try:
            return iter(self._read_vertex(vid)[DATA_INDEX])
        except KeyError:
            return iter(())

    def count_vertex_data_keys(self, vid: base.VertexID) -> int:
        try:
            return len(self._read_vertex(vid)[DATA_INDEX])
        except KeyError:
            return 0

    def get_edge_data(self, eid: base.EdgeID, key: Hashable) -> Any:
        try:
            return self._read_edge(eid)[DATA_INDEX][key]
        except KeyError:
            return None

    def set_edge_data(self, eid: base.EdgeID, key: Hashable, value: Any) -> None:
        self.add_edge(eid)
        data = self._read_edge(eid)
        data[DATA_INDEX][key] = value
        self._write_edge(eid, data)

    def has_edge_data(self, eid: base.EdgeID, key: Hashable) -> bool:
        try:
            return key in self._read_edge(eid)[DATA_INDEX]
        except KeyError:
            return False

    def discard_edge_data(self, eid: base.EdgeID, key: Hashable) -> None:
        try:
            data = self._read_edge(eid)
            del data[DATA_INDEX][key]
        except KeyError:
            return
        else:
            self._write_edge(eid, data)

    def iter_edge_data_keys(self, eid: base.EdgeID) -> Iterator[Hashable]:
        try:
            return iter(self._read_edge(eid)[DATA_INDEX])
        except KeyError:
            return iter(())

    def count_edge_data_keys(self, eid: base.EdgeID) -> int:
        try:
            return len(self._read_edge(eid)[DATA_INDEX])
        except KeyError:
            return 0
