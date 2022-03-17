from .Vertex import Vertex
import numpy as np
import networkx as nx


class Graph:
    """Generic Graph class."""

    INFTY = 9999

    def __init__(self):
        """A graph.
        """
        self._vertexToID = dict()
        self._IDToVertex = dict()
        self._nameToVertex = dict()

        self._type = "unknown"

        self._adjacency_matrix_computed = False
        self._distance_matrix_computed = False
        self._is_planar_computed = False
        self._is_connected_computed = False
        self._distance_matrix = np.empty(0, float)
        self._adjacency_matrix = np.empty(0, int)
        self._is_planar = False
        self._is_connected = False

        self._edges = set()

        self._diameter = 0
        self._order = 0

    def add_edge(self, u, v):
        """Add an (undirected) edge to the graph.

        :param u: First extremity of the edge to add.
        :type u: :class:`mas.graph.Vertex.Vertex`

        :param v: Second extremity of the edge to add.
        :type v: :class:`mas.graph.Vertex.Vertex`

        :returns: True if the edge was successfully added (if it did not
            already belong to the graph, and if its extremities were actual
            vertices of the graph), False otherwise.
        :rtype: boolean
        """

        if ((u not in self.vertices()) or (v not in self.vertices())):
            return False

        success1 = u.add_neighbor(v)
        success2 = v.add_neighbor(u)

        if success1 and not success2:
            u.remove_neighbor(v)
        if success2 and not success1:
            v.remove_neighbor(u)

        success = success1 and success2
        if success:
            self._edges.add((u, v))
            self._untoggle_computed()

        return success

    def add_vertex(self, vertex):
        """Add a vertex to the graph.

        :param vertex: The vertex to add.
        :type vertex: :class:`mas.graph.Vertex.Vertex`

        :returns: True if the vertex was successfully added (if it did not
            already belong to the graph), False otherwise.
        :rtype: boolean
        """
        if vertex not in self._vertexToID:
            ID = self._order
            self._vertexToID[vertex] = ID
            self._IDToVertex[ID] = vertex
            self._nameToVertex[vertex.name()] = vertex

            self._order += 1
            self._untoggle_computed()
            return True
        return False

    def adjacency_matrix(self):
        """Compute (if needed) and get the adjacency matrix
        of the graph.

        :returns: The adjacency matrix of the graph.
        :rtype: numpy.array
            (https://numpy.org/doc/stable/reference/generated/numpy.array.html)
        """
        self._compute_adjacency_matrix()
        return self._adjacency_matrix

    def diameter(self):
        """Get the maximum distance between two vertices.

        :returns: The diameter of the graph.
        :rtype: int
        """
        if (not self._distance_matrix_computed):
            self._compute_distance_matrix()

        return self._diameter

    def distance(self, u, v):
        """Get the distance between two vertices.

        :param u: Any vertex of the graph.
        :type u: :class:`mas.graph.Vertex.Vertex`

        :param v: Any vertex of the graph.
        :type v: :class:`mas.graph.Vertex.Vertex`

        :returns: The distance between the u and v.
        :rtype: int
        """
        self._compute_distance_matrix()
        i = self._vertexToID[u]
        k = self._vertexToID[v]
        return self._distance_matrix[i, k]

    def distance_matrix(self):
        """Get the distance matrix of the graph.

        :returns: The distance matrix of the graph.
        :rtype: numpy.array
            (https://numpy.org/doc/stable/reference/generated/numpy.array.html)
        """
        self._compute_distance_matrix()
        return self._distance_matrix

    def edges(self):
        """Get all the edges of the graph.

        :returns: The edges of the graph as tuples of two vertices.
        :rtype: set of tuples
        """
        return self._edges

    def get_vertex_by_id(self, ID):
        """Get the vertex uniquely associated to an identifier.

        :param ID: An identifier.
        :type ID: int

        :returns: The unique vertex associated to ID if it exists, None
            otherwise.
        :rtype: :class:`mas.graph.Vertex.Vertex`
        """
        if ID not in self._IDToVertex:
            return None
        return self._IDToVertex[ID]

    def get_vertex_by_name(self, name):
        """Get a vertex of the graph given its name.

        :param name: The name (not necessarily unique) of a vertex of the graph.
        :type name: string

        :returns: The last vertex added to the graph with the given ``name``
            parameter (see :class:`mas.graph.Vertex.Vertex`).
            If no such vertex belongs to the graph, then returns None.
        :rtype: :class:`mas.graph.Vertex.Vertex`
        """
        if name not in self._nameToVertex:
            return None
        return self._nameToVertex[name]

    def get_vertex_id(self, vertex):
        """Get the unique identifier of a vertex.

        :param vertex: A vertex.
        :type vertex: :class:`mas.graph.Vertex.Vertex`

        :returns: The unique identifier of the vertex in the graph.
        :rtype: int
        """
        return self._vertexToID[vertex]

    def init_from_adjacency_matrix(self, adjacency_matrix):
        """Initialize the graph from an adjacency matrix. Note that the graph
        is supposed to be undirected.

        :param adjacency_matrix: The adjacency matrix of the graph.
        :type adjacency_matrix: numpy.array
            (https://numpy.org/doc/stable/reference/generated/numpy.array.html)
        """
        order = len(adjacency_matrix)
        self.__init__()

        for i in range(order):
            self.add_vertex(Vertex(i))

        for i in range(order):
            for k in range(i, order):
                if adjacency_matrix[i, k] == 1:
                    u = self._IDToVertex[i]
                    v = self._IDToVertex[k]
                    self.add_edge(u, v)

        self._adjacency_matrix = adjacency_matrix.copy()
        self._adjacency_matrix_computed = True

    def init_from_file(self, filename):
        """Initialize the graph from a file in which:

        * the first line contains a list of names of vertices separated by\
            spaces;

        * the following lines contain adjacency lists of vertices separated by\
            spaces, and where:

            - the first name is the name of the vertex whose line is the\
                adjacency list;

            - the next names are the names of its neighbors.

        The graph is supposed to be undirected, i.e., if a vertex u belongs to
        the adjacency list of an other vertex v, then v will also be linked to
        u.

        :param filename: Name of the file to open.
        :type filename: string
        """
        def removeln(str):
            if str[-1] == "\n":
                str = str[:-1]
            return str

        with open(filename) as file:
            lines = file.readlines()

        self.__init__()

        verticesData = lines[0].split(" ")
        verticesData[-1] = removeln(verticesData[-1])

        for v in verticesData:
            self.add_vertex(Vertex(v))

        for line in lines[1:]:
            adjList = line.split(" ")
            vertex = self.get_vertex_by_name(removeln(adjList[0]))
            for v in adjList[1:]:
                neighbor = self.get_vertex_by_name(removeln(v))
                self.add_edge(vertex, neighbor)

    def init_from_graph(self, graph, copy=True):
        """Become a copy of the given graph.

        :param graph: The graph to copy.
        :type graph: :class:`mas.graph.Graph.Graph`

        :param copy: If set to True, the edges and vertices of the current graph
            are copies of those of the ``graph`` parameter. If set to False, the
            new graph is a copy, but its edges and vertices are the same of
            those of the ``graph`` parameter.
            Default to True.
        :type copy: :class:`mas.graph.Graph.Graph`
        """
        self.__init__()

        for vertex in graph.vertices():
            if copy:
                self.add_vertex(Vertex(vertex.name()))
            else: 
                self.add_vertex(vertex)

        for edge in graph.edges():
            nameU = edge[0].name()
            nameV = edge[1].name()
            u = self.get_vertex_by_name(nameU)
            v = self.get_vertex_by_name(nameV)
            self.add_edge(u, v)

    def is_connected(self):
        """ Connexity test of the graph.

        :returns: True if the graph is connected, False otherwise.
        :rtype: boolean
        """
        self._compute_is_connected()
        return self._is_connected

    def is_planar(self):
        """ Planarity test of the graph.

        :returns: True if the graph is planar, False otherwise.
        :rtype: boolean
        """
        self._compute_is_planar()
        return self._is_planar

    def order(self):
        """Get the number of vertices of the graph.

        :returns: The number of vertices of the graph.
        :rtype: int
        """
        return self._order

    def remove_edge(self, u, v):
        """Remove an edge from the graph.

        :param u: First extremity of the edge to remove.
        :type u: :class:`mas.graph.Vertex.Vertex`

        :param v: Second extremity of the edge to remove.
        :type v: :class:`mas.graph.Vertex.Vertex`

        :returns: True if the edge between u and v was successfully removed 
            (if it belonged to the graph), False otherwise.
        :rtype: boolean
        """

        if ((u not in self.vertices()) or (v not in self.vertices())):
            return False

        success1 = v.remove_neighbor(u)
        success2 = u.remove_neighbor(v)

        if success1 and not success2:
            v.add_neighbor(u)
        if success2 and not success1:
            u.add_neighbor(v)

        success = success1 and success2
        if success:
            if ((u, v) in self._edges):
                self._edges.remove((u, v))
            else:
                self._edges.remove((v, u))
            self._untoggle_computed()

        return success

    def remove_vertex(self, vertex):
        """Remove a vertex from the graph.

        :param vertex: The vertex to remove.
        :type vertex: :class:`mas.graph.Vertex.Vertex`

        :returns: True if vertex was successfully removed (if it belonged to
            the graph), False otherwise.
        :rtype: boolean
        """
        if vertex in self._vertexToID:
            self._order -= 1
            maxID = self._order
            maxIDVertex = self._IDToVertex[maxID]
            self._swap_vertices_ids(maxIDVertex, vertex)
            del(self._vertexToID[vertex])
            del(self._IDToVertex[maxID])
            del(self._nameToVertex[vertex.name()])

            for u in vertex.get_neighbors():
                u.remove_neighbor(vertex)

            self._untoggle_computed()
            return True
        return False

    def save(self, filename, ids="graph"):
        """Exports the graph to a txt file.

        :param filename: Name of the output file.
        :type filename: string

        :param ids: Specifies how the vertices are named in the output file. If
            "graph", the vertices are named according to their identifier in
            the graph. If "real", the vertices are named according to their
            ``name`` parameter (:class:`mas.Graph.Vertex.Vertex`). 
            Default to "graph".
        :type ids: string, optional
        """

        def id(vertex):
            if (ids == "graph"):
                return self._vertexToID[vertex]
            elif (ids == "real"):
                return vertex.name()

        str = ""
        i = 1
        for vertex in self.vertices():
            str += f"{id(vertex)}"
            str += " " if i < self.order() else "\n"
            i += 1

        for vertex in self.vertices():
            str += f"{id(vertex)}"
            for neighbor in vertex.get_neighbors():
                str += f" {id(neighbor)}"
            str += '\n'

        with open(filename, "w") as f:
            f.write(str)

    def set_type(self, type):
        """Change the type of the graph. e.g. \"planar\", \"clique\", etc.

        :param type: Type of the graph.
        :type type: str
        """
        self._type = type

    def size(self):
        """Get the number of edges of the graph.

        :returns: The number of edges of the graph.
        :rtype: int
        """
        return len(self._edges)

    def type(self):
        """Get the type of the graph.

        :returns: The type of the graph.
        :rtype: str
        """
        return self._type

    def vertices(self):
        """Get all the vertices of the graph.

        :returns: The vertices of the graph, associated to their unique
            identifier.
        :rtype: dict
        """
        return self._vertexToID

    def _compute_adjacency_matrix(self):
        if self._adjacency_matrix_computed:
            return

        size = self.order()
        self._adjacency_matrix = np.zeros((size, size), int)

        for vertex in self._vertexToID:
            for neighbor in vertex.get_neighbors():
                i = self._vertexToID[vertex]
                k = self._vertexToID[neighbor]
                self._adjacency_matrix[i, k] = 1

        self._adjacency_matrix_computed = True

    def _compute_distance_matrix(self):
        if self._distance_matrix_computed:
            return

        self._compute_adjacency_matrix()

        self._diameter = 0

        size = self._init_distMat()

        for k in range(size):
            for i in range(size):
                for j in range(size):
                    m = min(
                        self._distance_matrix[i, j],
                        self._distance_matrix[i, k] +
                        self._distance_matrix[k, j]
                    )
                    self._distance_matrix[i, j] = m
                    self._distance_matrix[j, i] = m
                    if (k == size - 1) and (self._diameter <= m):
                        self._diameter = m

        self._distance_matrix_computed = True

    def _compute_is_connected(self):
        if not self._is_connected_computed:
            G = nx.from_numpy_array(self.adjacency_matrix())
            self._is_connected = nx.is_connected(G)

    def _compute_is_planar(self):
        if not self._is_planar_computed:
            G = nx.from_numpy_array(self.adjacency_matrix())
            self._is_planar = nx.check_planarity(G)[0]

    def _init_distMat(self):
        size = self._order
        self._distance_matrix = np.zeros((size, size), float)

        for i in range(size):
            for j in range(i+1, size):
                if self._adjacency_matrix[i, j] == 1:
                    self._distance_matrix[i, j] = 1
                    self._distance_matrix[j, i] = 1
                else:
                    self._distance_matrix[i, j] = self.INFTY
                    self._distance_matrix[j, i] = self.INFTY

        return size

    def __str__(self):
        str = "Graph{\n"
        order = len(self._vertexToID)
        if (order != 0):
            v = self._IDToVertex[0]
            vID = self._vertexToID[v]
            str += f"\t({vID}){v.__str__()}"
        for i in range(1, order):
            v = self._IDToVertex[i]
            vID = self._vertexToID[v]
            str += f",\n\t({vID}){v.__str__()}"
        str += "\n}\n"
        return str

    def _swap_vertices_ids(self, u, v):
        IDu = self._vertexToID[u]
        self._vertexToID[u] = self._vertexToID[v]
        self._vertexToID[v] = IDu

    def _untoggle_computed(self):
        self._adjacency_matrix_computed = False
        self._distance_matrix_computed = False
        self._is_planar_computed = False
        self._is_connected_computed = False

