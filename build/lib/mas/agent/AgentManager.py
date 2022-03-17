import random

class AgentManager:
    """
    Used for managing all the data about agents during a simulation.
    """

    def __init__(self,
                 agents_list,
                 topology,
                 prior_knowledge=dict(),
                 possible_latencies=[1],
                 initial_status="",
                 number_of_pebbles=0):
        """An agent manager. It encapsulates all the data about agents in an
        agent list: their identifiers; their positions; the information they
        store; ...

        :param agents_list: List of agents to manage.
        :type agents_list: list.

        :param topology: Topology on which the simulation is run
        :type topology: :class:`mas.graph.Graph.Graph`

        :param prior_knowledge: prior information to give to every agents.
            Default to dict().
        :type prior_knowledge: dict

        :param possible_latencies: If agents_list is set to None, every agent
            is generated with a latency randomly picked in this list.
            Default to [1].
        :type possible_latencies: list of int, optional

        :param initial_status: Initial status of agents.
            Default to ""
        :type initial_status: string, optional

        :param number_of_pebbles: Number of pebbles initially available for 
            every agent.
            Default to 0.
        :type number_of_pebbles: int, optional
        """

        self._agents_positions = dict()
        self._init_position(agents_list, topology)

        self._agents_id = dict()
        self._init_ids(agents_list)

        self._agents_latency = dict()
        self._init_latencies(agents_list, possible_latencies)

        self._agents_positions_contains_mate = dict()
        self._init_positions_contains_mate(agents_list)

        self._agents_port_back = dict()
        self._init_agents_port_back(agents_list)

        self._agents_last_move = dict()
        self._init_agents_last_move(agents_list)

        self._agents_prior_knowledge = prior_knowledge

        self._agents_memory = dict()
        self._init_agents_memory(agents_list)

        self._agents_status = dict()
        self._init_agents_status(agents_list, initial_status)

        self._agents_pebbles = dict()
        self._max_pebbles = number_of_pebbles
        self._init_agents_pebbles(agents_list, number_of_pebbles)

    def _init_agents_last_move(self, agents_list):
        for agent in agents_list:
            self._set_agent_last_move(agent, 0)

    def _init_agents_memory(self, agents_list):
        for agent in agents_list:
            self._agents_memory[agent] = dict()

    def _init_agents_pebbles(self, agents_list, number_of_pebbles):
        for agent in agents_list:
            self._agents_pebbles[agent] = number_of_pebbles

    def _init_agents_port_back(self, agents_list):
        for agent in agents_list:
            self._set_agent_port_back(agent, None)

    def _init_agents_status(self, agents_list, initial_status):
        for agent in agents_list:
            self.set_agent_status(agent, initial_status)

    def _init_ids(self, agents_list):
        ids = random.sample(range(0, 50000), len(agents_list))
        i = 0
        for agent in agents_list:
            id = agent.desired_id()
            if (id is None) or (id in self._agents_id.values()):
                id = ids[i]
            self._agents_id[agent] = id
            i += 1

    def _init_latencies(self, agents_list, possible_latencies):
        for agent in agents_list:
            latency = agent.desired_latency()
            if latency is None:
                latency = random.choice(possible_latencies)
            self._agents_latency[agent] = latency

    def _init_position(self, agents_list, topology):
        for agent in agents_list:
            pos = agent.desired_initial_position()
            if pos is None:
                pos = random.choice(list(topology.vertices()))
            self._agents_positions[agent] = pos

    def _init_positions_contains_mate(self, agents_list):
        for agent in agents_list:
            self._agents_positions_contains_mate[agent] = False

    def add_pebble_to_agent(self, agent):
        """Increase the number of pebbles of an agent.
        
        :returns: True if the given agent had strictly less pebbles than the
            maximum number allowed, False otherwise.
        :rtype: boolean
        """
        pass

    def agent_moved(self, agent, step):
        """Specify that an agent moved at current step.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :param step: Execution step of a simulation.
        :type step: int
        """
        self._set_agent_last_move(agent, step)

    def get_agent_last_move(self, agent):
        """Get the last step the agent moved.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: A step.
        :rtype: int
        """
        return self._agents_last_move[agent]

    def get_agent_id(self, agent):
        """Get the unique identifier of the agent.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: The unique identifier of the agent.
        :rtype: int
        """
        return self._agents_id[agent]

    def get_agent_latency(self, agent):
        """Get the latency of the agent.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: The latency of the agent.
        :rtype: int
        """
        return self._agents_latency[agent]

    def get_agent_memory(self, agent, field=None):
        """Get the agent's memory.
        
        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :param field: A memory field.
            Default to None.
        :type field: any, optinal

        :returns: If field is None, then returns all the agent's memory,
            otherwise returns the given field of agent's memory.
        :rtype: dict or any
        """
        pass

    def get_agent_status(self, agent):
        """Get the status of the agent.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: The status of the agent.
        :rtype: str
        """
        return self._agents_status[agent]

    def get_all_agents_memory(self):
        """Get the memory of every agent.
        
        :returns: All agent's memory.
        :rtype: dict
        """
        return self._agents_memory

    def get_all_agents_positions(self):
        """Get the position of every agent
        
        :returns: The position of every agent.
        :rtype: dict
        """
        return self._agents_positions

    def get_agent_port_back(self, agent):
        """Get the port number of the edge the agent comes from.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: The port for the agent to get back to the previous position.
            If the agent did not perform any move, returns None.
        :rtype: int
        """
        return self._agents_port_back[agent]

    def get_agent_position(self, agent):
        """Get the position of an agent.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: The current position of the agent.
        :rtype: :class:`mas.graph.Vertex.Vertex`
        """
        return self._agents_positions[agent]

    def get_agent_position_contains_mate(self, agent):
        """Get a boolean according to whether current position of the agent 
        contains one or several agents.

        :returns: True if the current position of the agent contains an other
            agent, False otherwise.
        :rtype: boolean
        """
        return self._agents_positions_contains_mate[agent]

    def get_agents_prior_knowledge(self):
        """Get the prior knowledge given to every agent.
        
        :returns: The prior knowledge of the agents.
        :rtype: dict
        """
        return self._agents_prior_knowledge

    def get_remaining_pebbles_of_agent(self, agent):
        """Get the number of pebbles of an agent.
        
        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`
        
        :returns: The number of pebbles the agent still possesses.
        :rtype: int
        """
        pass

    def move_agent(self, agent, port):
        """Modify the position of an agent.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :param port: Port of the edge for the agent to traverse.
        :type port: int
        """
        oldpos = self.get_agent_position(agent)
        newpos = oldpos.get_neighbor_by_port(port)
        self._set_agent_position(agent, newpos)

        port_back = newpos.get_port_by_neighbor(oldpos)
        self._set_agent_port_back(agent, port_back)

        return oldpos, newpos

    def remove_from_agent_memory(self, agent, field, value=None):
        """Remove a value from an agent's memory field.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :param field: A memory field
        :type field: any

        :param value: If None, removes the given field, otherwise remove this
            value from given field.
            Default to None.
        :type value: any
        
        :returns: False if the given field does not exist, or if the given value
            does not belong to this field. True, otherwise.
        :rtype: boolean
        """
        pass

    def remove_pebble_from_agent(self, agent):
        """Decrease the number of pebbles of an agent.
        
        :returns: True if the given agent had at least one pebble, False
            otherwise.
        :rtype: boolean
        """
        pass

    def set_agent_memory(self, agent, field, value, append=False):
        """Set or add an agent's memory field (memory can not contain a field
            of same name as a field of prior knowledge).
        
        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :param field: A memory field
        :type field: any

        :param value: Value to add in given field.
        :type value: any

        :param append: If True, appends the value to the given memory field.
            If False, set the value of the given memory field to the given
            value.
            Default to False.
        :type append: boolean, optional

        :returns: False if the given field is also a field of the prior
            knowledge, True otherwise.
        :rtype: boolean
        """
        pass

    def set_agent_status(self, agent, status):
        """Set the agent's status.
        
        :param status: New status.
        :type status: str
        """
        self._agents_status[agent] = status

    def update_agent_position_contains_mate(self, agent, newvalue):
        """Set the agent's field of agents_positions_contains_mate.
        
        :param status: New value.
        :type status: boolean
        """
        self._agents_positions_contains_mate[agent] = newvalue

    def _set_agent_last_move(self, agent, step):
        self._agents_last_move[agent] = step

    def _set_agent_port_back(self, agent, port_back):
        self._agents_port_back[agent] = port_back

    def _set_agent_position(self, agent, position):
        self._agents_positions[agent] = position

