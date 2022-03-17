class Vertex:
    """A graph vertex.
    """

    def __init__(self, name):
        """A graph vertex.

        :param name: Name of the vertex (not necessarily a unique identifier).
        :type name: string
        """
        self._name = name

        self._neighbors = []

        self._portToNeighbor = dict()
        self._next_port = 0
        self._unused_ports = []

    def add_neighbor(self, vertex):
        """Add a neighbor.

        :param v: The neighbor to add.
        :type v: :class:`mas.graph.Vertex.Vertex`

        :returns: True if the neighbor to add was not a neighbor already, False
            otherwise.
        :rtype: boolean
        """
        if vertex not in self._neighbors:
            if len(self._unused_ports) != 0:
                port = self._unused_ports[0]
                self._unused_ports.remove(port)
            else:
                port = self._next_port
                self._next_port += 1
            self._neighbors.append(vertex)
            self._portToNeighbor[port] = vertex
            return True
        return False

    def copy(self):
        """Copy the vertex.

        :returns: A new vertex with the same name and the same adjacency list as
            the current one.
        :rtype: :class:`mas.graph.Vertex.Vertex`
        """
        copy = Vertex(self._name)
        for neighbor in self.get_neighbors():
            copy.add_neighbor(neighbor)
        return copy

    def get_neighbor_by_port(self, port):
        """Get a neighbor given a port.

        :param port: Port number.
        :type port: int

        :returns: The neighbor reached when following the given port. If the
            port does not exist, then returns None.
        :rtype: :class:`mas.graph.Vertex.Vertex`
        """
        if port not in self._portToNeighbor:
            return None

        return self._portToNeighbor[port]

    def get_neighbors(self):
        """Get the list of all the neighbors.

        :returns: All the neighbors of the current vertex.
        :rtype: list
        """
        return self._neighbors

    def get_port_associations(self):
        """Get all the ports available from the vertex, associated to the
        vertices they lead to.

        :returns: A dictionary of vertices keyed by ports (int)
        :rtype: dict
        """
        return self._portToNeighbor

    def get_port_by_neighbor(self, neighbor):
        """Get the port leading to the given neighbor.

        :param neighbor: A vertex.
        :type neighbor: :class:`mas.graph.Vertex.Vertex`

        :returns: The port leading to neighbor. None, if neighbor is not an
            actual neighbor of the vertex.
        :rtype: int
        """
        for port, vertex in self._portToNeighbor.items():
            if vertex == neighbor:
                return port

        return None

    def get_ports(self):
        """Get all the ports available.

        :returns: The ports available from the given vertex.
        :rtype: list
        """
        return list(self._portToNeighbor)

    def name(self):
        """Get the name of the vertex.

        :returns: Vertex name.
        :rtype: string
        """
        return self._name

    def remove_neighbor(self, vertex):
        """Remove a neighbor.

        :param vertex: The neighbor to remove.
        :type vertex: :class:`mas.graph.Vertex.Vertex`

        :returns: True if vertex was an actual neigbor, False otherwise.
        :rtype: boolean
        """
        if vertex in self._neighbors:
            for p, u in self._portToNeighbor.items():
                if u == vertex:
                    port = p
                    break
            self._neighbors.remove(vertex)
            self._unused_ports.append(port)
            del(self._portToNeighbor[port])
            return True
        return False

    def reset_port_associations(self, 
                                portToNeighbor, 
                                compress=False, 
                                maintain_unused_ports=False):
        """Associate new ports to the neighbors of the current vertex.

        :param portToNeighbor: A dictionary of vertices keyed by ports (int).
        :type portToNeighbor: dict

        :returns: False if the values of the given dictionnary do not exactly
            correspond to the list of neighbors of the current vertex.
            True otherwise.
        :rtype: boolean

        :param compress: If set to True, the given ports to associate with
            vertices are mapped to [0,...,n-1] where n corresponds to the number
            of ports. This mapping :math:`\phi` preserves the order of the
            ports, i.e., if :math:`p_1 < p_2`, then :math:`\phi(p_1) <
            \phi(p_2)`.
            Default to False.
        :type compress: boolean, optional

        :param maintain_unused_ports: If set to True, current Vertex will store
            unassociated ports in range [0,maxp] where maxp denotes the given
            port with maximum value.
            Default to False.
        :type maintain_unused_ports: boolean, optional
        """
        n = len(self._portToNeighbor.values())
        if n != len(portToNeighbor.values()):
            return False

        for vertex in self._portToNeighbor.values():
            if vertex not in portToNeighbor.values():
                return False
        self._portToNeighbor = portToNeighbor

        if compress:
            port_list = list(self._portToNeighbor)
            port_list.sort()
            print(port_list)
            print(self._portToNeighbor)
            for i in range(0, n):
                self._portToNeighbor[i] = self._portToNeighbor[port_list[i]]
                del self._portToNeighbor[port_list[i]]

        if maintain_unused_ports:
            maxp = max(list(self._portToNeighbor))
            self._unused_ports = [
                i 
                for i in range(0,maxp) 
                if i not in self._portToNeighbor
            ]

        return True

    def set_name(self, name):
        """Change the name of the vertex.

        :param name: The new name.
        :type name: string
        """
        self._name = name

    def __str__(self):
        str = f"{self.name()} : {'{'}"
        n = len(self._neighbors)
        if (n != 0):
            str += f"{self._neighbors[0].name()}"
        for i in range(1, n):
            str += f", {self._neighbors[i].name()}"
        str += "}"
        return str
