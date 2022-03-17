import networkx as nx
from mas.graph.Graph import Graph

import logging

class GraphViz(Graph):
    """Based on :class:`mas.graph.Graph.Graph`, encapsulates methods and
    parameters to draw Graph objects."""

    def __init__(self):
        """A graph with drawing methods."""
        Graph.__init__(self)

        self._positions_computed = False
        self._vertexToPosition = dict()
        self._max_x_coordinate = 700
        self._max_y_coordinate = 700
        self._padding = 10

        self._layout_all_methods = [
            "circo",
            "circular",
            "dot",
            "kamada_kawai",
            "planar",
            "random",
            "spectral",
            "spring",
            "spiral"
        ]
        self._layout_method = "kamada_kawai"

        self._init_vertices_graphics()
        self._init_edges_graphics()

    def add_edge(self, u, v):
        """
          See :meth:`mas.graph.Graph.Graph.add_edge()`.
        """
        success = Graph.add_edge(self, u, v)
        if success:
            self._positions_computed = False
        return success

    def add_vertex(self, vertex):
        """
          See :meth:`mas.graph.Graph.Graph.add_vertex()`.
        """
        success = Graph.add_vertex(self, vertex)
        if success:
            self._positions_computed = False
        return success

    def draw(self, canvas):  # pragma: no cover
        """Draw the graph.

        :param canvas: Canvas in which to draw the graph.
        :type canvas: tkinter.Canvas
          (http://tkinter.fdex.eu/doc/caw.html)
        """
        self._positions_computed = False

        for v in self.vertices():
            for u in v.get_neighbors():
                self._draw_edge(u, v, canvas)

        for v in self.vertices():
            self._draw_vertex(v, canvas)

    def get_all_layout_methods(self):
        """Get the name of all the available layout methods.

        :returns: Available layout methods.
        :rtype: list
        """
        if not self.is_planar():
            self._layout_all_methods.remove("planar")
        else:
            if "planar" not in self._layout_all_methods:
                self._layout_all_methods.append("planar")
        return self._layout_all_methods

    def get_edge_dashstyle(self):
        """TBD"""
        return self._edge_dashstyle

    def get_edge_thickness(self):
        """TBD"""
        return self._edge_thickness

    def get_layout_method(self):
        """Get the name of the algorithm currently chosen to compute the
        coordinate of the vertices.

        :returns: Layout method's name.
        :rtype: string
        """
        return self._layout_method

    def get_max_x_y_coordinate(self):
        """Get the maximum x and y coordinate without considering the padding.

        :returns: A vector :math:`(x_{\\max},y_{\\max})` such that the center\
            point :math:`(x,y)` of any vertex of the graph is such that:

          * :math:`x \\le (x_{\\max} + 2p)`, and
          * :math:`y \\le (y_{\\max} + 2p)`,

          where :math:`p` is the padding of the graph.
        :rtype: tuple
        """
        return (self._max_x_coordinate, self._max_y_coordinate)

    def get_padding(self):
        """Get the padding of the graph.

        :returns: Padding separating the drawing of the graph from the
            canvas borders.
        :rtype: int
        """
        return self._padding

    def get_vertex_by_tag(self, tag):
        """TBD"""
        if not tag[6:].isdigit():
            logging.error(f"{tag}[6:] is not an integer.")
            return None

        id = int(tag[6:])
        if tag[:6] != "vertex":
            logging.error(f"{tag} does not correspond to a vertex tag.")
            return None

        return self.get_vertex_by_id(id)

    def get_vertices_border_color(self):
        """TBD"""
        return self._vertex_border_color

    def get_vertices_border_thickness(self):
        """TBD"""
        return self._vertex_border_thickness

    def get_vertices_color(self):
        """TBD"""
        return self._vertex_color

    def get_vertex_position(self, vertex):
        """Get the position of the vertex in the canvas.

        :param vertex: The vertex considered.
        :type vertex: Vertex

        :returns: The center coordinate (x,y) in the canvas of the given vertex.
        :rtype: tuple
        """
        self._compute_positions()
        return self._vertexToPosition[vertex]

    def get_vertices_radius(self):
        """Get the radius of the disks representing the vertices.

        :returns: The radius of the vertices in the drawing of the graph.
        :rtype: int
        """
        return self._vertex_radius

    def remove_vertex(self, vertex):
        """
          See :meth:`mas.graph.Graph.Graph.remove_vertex()`.
        """
        success = Graph.remove_vertex(self, vertex)
        if success:
            self._positions_computed = False
        return success

    def remove_edge(self, u, v):
        """
          See :meth:`mas.graph.Graph.Graph.remove_edge()`.
        """
        success = Graph.remove_edge(self, u, v)
        if success:
            self._positions_computed = False
        return success

    def set_layout_method(self, layout_method):
        """Change the algorithm used to compute the coordinates of the vertices.

        :param layout_method: Name of the algorithm to use.
        :type layout_method: string

        :returns: True if the given layout_method exists, False otherwise.
        :rtype: boolean
        """
        if layout_method in self._layout_all_methods:
            self._layout_method = layout_method
            return True
        return False

    def set_max_x_coordinate(self, xmax):
        """Set the maximum x coordinate without considering the padding.

        :param xmax: The maximum x-value of the center of a vertex (without
          considering the padding).
        :type xmax: int
        """
        self._max_x_coordinate = xmax

    def set_max_y_coordinate(self, ymax):
        """Set the maximum y coordinate without considering the padding.

        :param ymax: The maximum y-value of the center of a vertex (without
          considering the padding).
        :type ymax: int
        """
        self._max_y_coordinate = ymax

    def set_vertices_radius(self, radius):
        """Set the radius of the disks representing the vertices.

        :param radius: The radius of the vertices in the drawing of the graph.
        :type radius: int
        """
        self._vertex_radius = radius

    def _center_normalize_shift(self, vertex, xmin, ymin, xmax, ymax):
        # center;
        # normalize between 0 and self._max_coordinate;
        # shift proportionally to _vertex_radius
        xmax += abs(xmin)
        ymax += abs(ymin)

        x = self._vertexToPosition[vertex][0] + abs(xmin)
        y = self._vertexToPosition[vertex][1] + abs(ymin)
        x = x / xmax * self._max_x_coordinate if xmax > 0 else 0
        y = y / ymax * self._max_y_coordinate if ymax > 0 else 0
        x += self._vertex_radius + self._padding
        y += self._vertex_radius + self._padding
        return (x, y)

    def _compute_positions(self):
        if self._positions_computed:
            return

        adjMat = self.adjacency_matrix()
        G = nx.from_numpy_array(adjMat)
        pos = self._nx_layout(G)

        for v in self.vertices():
            vertexID = self.get_vertex_id(v)
            # * self._position_scaling
            self._vertexToPosition[v] = pos[vertexID]

        xmin = min([self._vertexToPosition[v][0] for v in self.vertices()])
        ymin = min([self._vertexToPosition[v][1] for v in self.vertices()])
        xmax = max([self._vertexToPosition[v][0] for v in self.vertices()])
        ymax = max([self._vertexToPosition[v][1] for v in self.vertices()])

        for v in self.vertices():
            (x, y) = self._center_normalize_shift(v, xmin, ymin, xmax, ymax)
            self._vertexToPosition[v] = (x, y)

        self._positions_computed = True

    def _draw_edge(self, u, v, canvas):  # pragma: no cover
        self._compute_positions()

        if (self.get_vertex_id(u) < self.get_vertex_id(v)):
            xu, yu = self.get_vertex_position(u)
            xv, yv = self.get_vertex_position(v)

            edge_id = f"({self.get_vertex_id(u)},{self.get_vertex_id(v)})"
            canvas.create_line(xu, yu, xv, yv,
                               fill=self._edge_color,
                               dash=self._edge_dashstyle,
                               width=self._edge_thickness,
                               tags=["edges", f"edge{edge_id}"]
                               )

    def _draw_vertex(self, vertex, canvas):  # pragma: no cover
        self._compute_positions()

        x, y = self.get_vertex_position(vertex)
        r = self._vertex_radius
        canvas.create_oval(x - r, y - r, x + r, y + r,
                           fill=self._vertex_color,
                           outline=self._vertex_border_color,
                           width=self._vertex_border_thickness,
                           tags=["vertices",
                                 f"vertex{self.get_vertex_id(vertex)}"]
                           )

    def _init_edges_graphics(self):
        self._edge_thickness = 1
        self._edge_color = "#555555"
        self._edge_dashstyle = ()

    def _init_vertices_graphics(self):
        # with open(file) as f:
        #   verticesGraphics = json.load(f)
        self._vertex_border_thickness = 2
        self._vertex_border_color = "black"
        self._vertex_radius = 6
        self._vertex_color = "navy"

    def _nx_layout(self, nxgraph):  # pragma: no cover
        if self._layout_method == "circo":
            return nx.nx_pydot.pydot_layout(nxgraph, prog="circo")
        elif self._layout_method == "circular":
            return nx.circular_layout(nxgraph)
        elif self._layout_method == "dot":
            return nx.nx_pydot.pydot_layout(nxgraph, prog="dot")
        elif self._layout_method == "kamada_kawai":
            return nx.kamada_kawai_layout(nxgraph)
        elif self._layout_method == "planar":
            return nx.planar_layout(nxgraph)
        elif self._layout_method == "random":
            return nx.random_layout(nxgraph)
        elif self._layout_method == "spectral":
            return nx.spectral_layout(nxgraph)
        elif self._layout_method == "spring":
            return nx.spring_layout(nxgraph, iterations=500)
        elif self._layout_method == "spiral":
            return nx.spiral_layout(nxgraph)
        else:
            return nx.kamada_kawai_layout(nxgraph)
