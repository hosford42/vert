# Vert
*Graphs for Python*

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
        # Implementations for each of GraphStore's abstract methods
        ...
        
    with Graph(MyGraphStore(...)) as g:
        # Now the graph consults your back end for storage and retrieval
        ...

 
## TODO:

* Add separately installable graph stores for neo4j, tinkerpop, networkx, and 
  other back ends.
* Add algorithms such as path finding and pattern matching. Whenever possible,
  these should be implemented by the graph store, rather than at the interface 
  level. By having the interface classes inspect the graph store for the method
  before calling it, it should be possible to fall back on a slower default 
  client-side implementation when the store does not provide one.
* Add support for transactions and make the code thread-safe.
* Add support for reading & writing common graph file formats.
* 100% code coverage for unit testing.
* Prettify the string representations for Edges and Vertices.
* Make the DBM graph store more efficient.
* Add an example for creating a third-party module to provide support for
  new kinds of graph stores.
