"""Generic Graph module.

.. currentmodule:: mas.graph

We assume that a graph consists of a set of vertices, each of them associated to
the set of their neighbors.
We generally assume the graphs to be *undirected*, that is if a vertex u belongs
to the neighbors of an other vertex v, then v also belongs to the neighbors of
u.
It is possible to produce directed graphs in :mod:`graph` but most of the
methods and functions handle only undirected graphs.

Glossary
--------

.. glossary::

    Graph
        Given a set V, a *graph* :math:`G` is a couple :math:`(V, E)` where
        :math:`V` is a set and :math:`E` is a relation over this set,
        i.e., :math:`E \\subseteq V \\times V`.

    undirected graph
        A :term:`graph` :math:`G = (V,E)` is *undirected* if whenever
        :math:`(u,v)` belongs to :math:`E`, then :math:`(v,u)` also does.

    vertex
        Given a :term:`graph` :math:`G = (V, E)`, :math:`V` is said to be the
        *vertex* set of :math:`G`.

    edge
        Given a :term:`graph` :math:`G = (V, E)`, :math:`E` is said to be the
        *edge* set of :math:`G`.

    order
        Number of vertices of a graph.

    size
        Number of edges of a graph.

    diameter
        Maximum distance between two vertices of the graph.

Module classes
--------------

    * :class:`mas.graph.Graph.Graph`
    * :class:`mas.graph.Vertex.Vertex`

Module content
--------------

.. autoclass:: mas.graph.Graph.Graph
    :members:

.. autoclass:: mas.graph.Vertex.Vertex
    :members:
    :special-members: __init__

.. automodule:: mas.graph.graph_generator
    :members:
"""

__author__ = 'Sébastien Ratel'

__all__ = [
    "Graph",
    "Vertex",
    "graph_generator"
]
