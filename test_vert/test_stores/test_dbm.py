import os

from vert.stores.dbm import DBMGraphStore

# noinspection PyProtectedMember
import test_vert.test_stores._base as _base


class TestDBMGraphStore(_base.TestGraphStore):

    @property
    def graph(self):
        # noinspection PyProtectedMember
        store = self._graph._graph_store
        # noinspection PyProtectedMember
        self.assertEqual(store._v_cache_times.keys(), store._v_cache.keys())
        # noinspection PyProtectedMember
        self.assertLessEqual(store._v_cache_dirty, store._v_cache.keys())
        return self._graph

    def createStore(self):
        # noinspection PyAttributeOutsideInit
        self.path = 'test1.db'
        if os.path.isfile(self.path):
            os.remove(self.path)
        return self.path

    def expectedStoreClass(self):
        return DBMGraphStore

    def tearDown(self):
        super().tearDown()
        graph = getattr(self, 'graph', None)
        if graph:
            # noinspection PyProtectedMember
            graph._graph_store.close()
        path = getattr(self, 'path', None)
        if path and os.path.isfile(path):
            os.remove(path)


class TestDBMGraphStoreNoCache(_base.TestGraphStore):

    @property
    def graph(self):
        # noinspection PyProtectedMember
        store = self._graph._graph_store
        # noinspection PyProtectedMember
        self.assertEqual(store._v_cache_times.keys(), store._v_cache.keys())
        # noinspection PyProtectedMember
        self.assertLessEqual(store._v_cache_dirty, store._v_cache.keys())
        return self._graph

    def createStore(self):
        # noinspection PyAttributeOutsideInit
        self.path = 'test2.db'
        if os.path.isfile(self.path):
            os.remove(self.path)
        return self.path

    def expectedStoreClass(self):
        return DBMGraphStore

    def setUp(self):
        super().setUp()
        # noinspection PyProtectedMember
        self._graph._graph_store.vertex_cache_size = 0
        # noinspection PyProtectedMember
        self._graph._graph_store.edge_cache_size = 0

    def tearDown(self):
        super().tearDown()
        graph = getattr(self, 'graph', None)
        if graph:
            # noinspection PyProtectedMember
            graph._graph_store.close()
        path = getattr(self, 'path', None)
        if path and os.path.isfile(path):
            os.remove(path)
