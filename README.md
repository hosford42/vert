# Vert
*Graphs for Python*
 
## TODO:

* Add separately installable graph stores for neo4j, tinkerpop, networkx, and 
  other back ends.
* Add algorithms such as path finding and pattern matching. Whenever possible,
  these should be implemented by the graph store, rather than at the interface 
  level. By having the interface classes inspect the graph store for the method
  before calling it, it should be possible to fall back on a slower default 
  client-side implementation when the store does not provide one.
* Add transactions and make the code thread-safe.
* Add support for reading & writing common graph file formats.
* 100% code coverage for unit testing.
* Prettify the string representations for Edges and Vertices.
