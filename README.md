# Graph Sanity
*Sane interface for graphs*
 
## TODO:

* Add a graph_sanity.stores.dbm module and implement a persistent graph store
  on top of the built-in dbm module. Use this as the default when a path string
  is passed to the Graph constructor.
* Add graph stores for neo4j, tinkerpop, networkx, and other back ends.
* Add algorithms such as path finding and pattern matching. These should be
  implemented by the graph store, rather than at the interface level.
* Add transactions and make the code thread-safe.
