# Vert
*Graphs for Python*

## Copyright/License

All content copyright 2017 Aaron M. Hosford. Use of this software is governed by the MIT 
license. See LICENSE.txt for the full license agreement. 

## Package Structure

* **test_vert**: Unit tests for vert
    * **test_stores**: Unit tests for vert.stores
        * **\_\_init\_\_.py**: Empty placeholder.
        * **\_base.py**: Contains base class for vert.stores test cases.
        * **test_dbm.py**: Unit tests for vert.stores.dbm.
        * **test_memory.py**: Unit tests for vert.stores.memory.
    * **\_\_init\_\_.py**: Empty placeholder.
* **vert**: The package root
    * **stores**: Subpackage containing implementations of various graph stores that the vert
      package supports out of the box.
        * **\_\_init\_\_.py**: Empty placeholder.
        * **base.py**: Defines the GraphStore interface that all graph stores have to implement.
          The GraphStore interface hides the implementation details for each graph store,
          providing a consistent, albeit clunky, means of accessing and modifying the 
          contents of a graph.
        * **dbm.py**: Defines DBMGraphStore, a DBM-backed persistent graph store.
        * **memory.py**: Defines the MemoryGraphStore, a non-persistent, memory-only graph store.
    * **\_\_init\_\_.py**: Exports the publicly visible symbols for the vert package. Nothing
      is actually defined in this module.
    * **graphs.py**: Defines the Graph, Vertex, and Edge, classes, along with other supporting
      infrastructure. This module's classes transform the clunky interface provided by
      GraphStore into a convenient and versatile object-oriented interface designed to make
      it easy to work with graphs in a consistent manner regardless of how the underlying
      storage mechanisms work.

## Examples

#### Non-Persistent

    from vert import Graph
    
    with Graph() as g:
        dog = g.vertices['dog'].add()
        cat = g.vertices['cat'].add()
        edge = g.edges['dog', 'cat']
        print(edge.exists)  # False
        edge.add()
        print(edge.exists)  # True
        edge.labels.add('chases')
        print('chases' in edge.labels)  # True
    
    with Graph() as g:
        edge = g.edges['dog', 'cat']
        print(edge.exists)  # False 

#### DBM-Backed Persistence

    from vert import Graph
    
    with Graph('test.db') as g:
        dog = g.vertices['dog'].add()
        cat = g.vertices['cat'].add()
        edge = g.edges['dog', 'cat']
        print(edge.exists)  # False
        edge.add()
        print(edge.exists)  # True
        edge.labels.add('chases')
        print('chases' in edge.labels)  # True
    
    with Graph('test.db') as g:
        edge = g.edges['dog', 'cat']
        print(edge.exists)  # Still true
        print('chases' in edge.labels)  # Still true

#### Defining Your Own Storage Mechanism

    from vert import Graph, GraphStore
    
    class MyGraphStore(GraphStore):
        # Implement each of GraphStore's abstract methods here
        ...
        
    with Graph(MyGraphStore(...)) as g:
        # Now the graph consults your back end for storage and retrieval
        ...

## TODO:

* Add separately installable graph stores for neo4j, tinkerpop, networkx, 
  sqlite, and other back ends.
* Add an example for creating a third-party module to provide support for
  new kinds of graph stores.
* Add algorithms such as path finding and pattern matching. Whenever possible,
  these should be implemented by the graph store, rather than at the interface 
  level. By having the interface classes inspect the graph store for the method
  before calling it, it should be possible to fall back on a slower default 
  client-side implementation when the store does not provide one. An alternate
  approach would be to add the methods to the GraphStore class but have them
  raise a special sentinel exception if the particular implementation doesn't
  provide the algorithm.
* Add support for transactions and make the code thread-safe.
* Add support for reading & writing common graph file formats.
* Add support for transferring from one graph store to another.
* 100% code coverage for unit testing.
* Prettify the string representations for Edges and Vertices.
* Make the DBM graph store more efficient.
* Add proper documentation strings.
* Add an intro to the README file.
* Support older versions of Python.
