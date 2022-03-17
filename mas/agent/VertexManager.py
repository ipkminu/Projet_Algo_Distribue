from collections import defaultdict


class VertexManager:

    """
    Used for adding informations to vertices during a simulation.
    """

    def __init__(self, topology, agents_positions=dict()):
        """A vertex manager. It allows to add informations about vertices in a
        given topology (according to a simulation): their memory; the number of
        agents or pebbles they contain; ...

        :param topology: A graph.
        :type topology: :class:`mas.graph.Graph.Graph`

        :param agents_positions: Dictionnary of vertices
          (:class:`mas.graph.Vertex.Vertex`) keyed by agents
          (:class:`mas.agent.Agent.Agent`).
          Default to dict().
        :type agents_positions: dict
        """

        self._vertices_memory = dict()
        self._init_vertices_memory(topology)

        self._pos_to_agents_list = defaultdict(list)
        self._init_pos_to_agents_list(agents_positions)

        self._vertices_pebbles = dict()
        self._init_vertices_pebbles(topology)

    def _init_pos_to_agents_list(self, agents_positions):
        for agent in agents_positions:
            vertex = agents_positions[agent]
            self._pos_to_agents_list[vertex].append(agent)

    def _init_vertices_memory(self, topology):
        for vertex in topology.vertices():
            self._vertices_memory[vertex] = dict()

    def _init_vertices_pebbles(self, topology):
        for vertex in topology.vertices():
            self._vertices_pebbles[vertex] = dict()

    def get_agents_on_vertex(self, vertex):
        """Get all the agents on a vertex.

        :param vertex: A vertex.
        :type vertex: :class:`mas.graph.Vertex.Vertex`

        :returns: All the agents on the given vertex.
        :rtype: list
        """
        return self._pos_to_agents_list[vertex]

    def get_pebbles_on_vertex(self, vertex):
        """Get all the pebbles on a vertex.

        :param vertex: A vertex.
        :type vertex: :class:`mas.graph.Vertex.Vertex`

        :returns: A dictionnary of int keyed by agents.
        :rtype: dict
        """
        pass

    def get_nb_of_pebbles_on_vertex(self, vertex, agent=None):
        """Get the number of pebbles on a vertex

        :param vertex: A vertex.
        :type vertex: :class:`mas.graph.Vertex.Vertex`

        :param agent: A mobile agent.
          Default to None
        :type agent: class:`mas.agent.Agent.Agent`, optional

        :returns: If agent is None, the returns the sum of every pebble on the 
          given vertex. Otherwise returns the number of pebbles on this vertex
          coming from the given agent.
        :rtype: int
        """
        pass

    def get_occupied_positions(self):
        """Get the list of every vertex of the topology containing at least one
        agent.

        :return: A list of vertices.
        :rtype: list
        """
        return list(self._pos_to_agents_list)

    def get_vertex_memory(self, vertex, field=None):
        """Get a vertex's memory.

        :param vertex: A vertex.
        :type vertex: :class:`mas.graph.Vertex.Vertex`

        :param field: A memory field.
            Default to None.
        :type field: any, optional

        :returns: If field is None, then returns all the vertex's memory, otherwise 
            returns the given field of vertex's memory.
        :rtype: dict or any
        """
        pass

    def put_agent_pebble_on_vertex(self, agent, vertex):
        """Increase the number of pebbles left by an agent on a vertex.

        :param vertex: A vertex.
        :type vertex: :class:`mas.graph.Vertex.Vertex`

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`
        """
        pass

    def move_agent(self, agent, oldpos, newpos):
        """Modify the position of an agent.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :param port: Port of the edge for the agent to traverse.
        :type port: int
        """
        if agent not in self._pos_to_agents_list[oldpos]:
            return False

        self._pos_to_agents_list[oldpos].remove(agent)
        self._pos_to_agents_list[newpos].append(agent)
        if len(self._pos_to_agents_list[oldpos]) == 0:
            del(self._pos_to_agents_list[oldpos])
        return True

    def remove_agent_pebble_from_vertex(self, agent, vertex):
        """Decrease the number of pebbles left by an agent on a vertex.

        :param vertex: A vertex.
        :type vertex: :class:`mas.graph.Vertex.Vertex`

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: False if the given vertex did not contain any pebble from the
          given agent. True otherwise.
        :rtype: boolean
        """
        pass

    def set_vertex_memory(self, vertex, field, value, append=False):
        """Set or add a vertex's memory field.

        :param vertex: A vertex.
        :type vertex: :class:`mas.graph.Vertex.Vertex`

        :param field: A memory field
        :type field: any

        :param value: Value to add in given field.
        :type value: any

        :param append: If True, appends the value to the given memory field.
            If False, set the value of the given memory field to the given
            value.
            Default to False.
        :type append: boolean, optional
        """
        pass

    def vertex_contains_pebbles(self, vertex, agent=None):
        """Ask if a vertex contains a pebble

        :param vertex: A vertex.
        :type vertex: :class:`mas.graph.Vertex.Vertex`

        :param agent: A mobile agent.
          Default to None.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: If agent is set to None, then returns True if the given vertex
          contains at least one pebble, and False otherwise.
          If agent is not None, then return True if the given vertex contains
          at least one pebble from the given agent, and False otherwise.
        :rtype: boolean
        """
        pass
