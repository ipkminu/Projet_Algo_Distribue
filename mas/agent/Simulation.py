#from msilib.schema import Error
from multiprocessing.dummy import Array

from numpy import NaN, empty
from .Agent import Agent
from .agent_algorithms import *
from .AgentManager import AgentManager
from .VertexManager import VertexManager
import random


class Simulation:
    """
    This is the main class of the distributed part of this simulator. It
    gathers the topology, the agents and the model. It makes the agents apply
    their algorithms and specifies which actions are legal for them.
    """

    def __init__(self,
                 topology,
                 algorithm=nothing,
                 agents_list=None,
                 agents_number=1,
                 possible_latencies=[1],
                 anonymous=False,
                 synchronous=True,
                 anonymous_topology=False,
                 agents_with_memory=False,
                 prior_knowledge=dict(),
                 nodes_with_memory=False,
                 number_of_pebbles=0,
                 removable_pebbles=True,
                 async_proba=0.3,
                 initial_status="",
                 verbose=False):
        """A Simulation specifying a model and a topology, executing the
        agents's algorithms, and sending requests to an AgentManager.

        :param topology: Topology on which the simulation is run
        :type topology: :class:`mas.graph.Graph.Graph`

        :param agents_list: List of agents to add to the simulation.
            Default to None.
        :type agents_list: list of :class:`mas.agent.Agent.Agent`,
            optional

        :param algorithm: an algorithm of the form ``algorithm(agent)``, where
            ``agent`` is of type :class:`mas.Agent.Agent`.
            Default to ``nothing`` (does nothing).
        :type algorithm: function

        :param agents_number: Number of agents to add to the simulation. Not
            taken into account if agents_list is not None.
            Default to 1.
        :type agents_number: int, optional

        :param anonymous: Anonymity of agents.
            Default to False.
        :type anonymous: boolean, optional

        :param synchronous: Synchronous model.
            Default to True.
        :type synchronous: boolean, optional

        :param anonymous_topology: Anonymity of the vertices.
            Default to False.
        :type anonymous_topology: boolean, optional

        :param agents_with_memory: Agents able to remember things.
            Default to False.
        :type agents_with_memory: boolean, optional

        :param prior_knowledge: Initial information available for every agent.
            Default to dict().
        :type prior_knowledge: dict, optional

        :param nodes_with_memory: Nodes contain whiteboards to write on.
            Default to False.
        :type nodes_with_memory: boolean, optional

        :param number_of_pebbles: Number of pebbles initially available for 
            every agent.
            Default to 0.
        :type number_of_pebbles: int, optional

        :param removable_pebbles: Agents can recover the pebbles they left.
            Default to True.
        :type removable_pebbles: boolean, optional

        :param possible_latencies: If agents_list is set to None, every agent
            is generated with a latency randomly picked in this list.
            Default to [1].
        :type possible_latencies: list of int, optional

        :param async_proba: Probability for the asynchrony to prevent an agent
            from executing its algorithm at each step.
            Default to 0.3.
        :type async_proba: [0,1] double, optional

        :param initial_status: Initial status of agents.
            Default to ""
        :type initial_status: string, optional

        :param verbose: print warnings when agents call unvailable (in the
            model) methods or when the simulation prevents an agent from moving.
            Also indicate when an agent changes its status.
            Default to False.
        :type verbose: boolean, optional
        """
        self._topology = topology
        self._anonymous = anonymous
        self._anonymous_topology = anonymous_topology
        self._synchronous = synchronous
        self._algorithm = algorithm
        self._possible_latencies = possible_latencies
        self._agents_with_memory = agents_with_memory
        self._prior_knowledge = prior_knowledge != dict()
        self._nodes_with_memory = nodes_with_memory
        self._number_of_pebbles = number_of_pebbles
        self._removable_pebbles = removable_pebbles

        self._verbose = verbose

        self._step = 1

        self._async_proba = async_proba

        self._agents_list = []
        self._init_agents_list(agents_list, agents_number)

        self._agents_manager = AgentManager(
            self._agents_list,
            topology,
            prior_knowledge=prior_knowledge,
            possible_latencies=possible_latencies,
            initial_status=initial_status,
            number_of_pebbles=number_of_pebbles
        )

        self._vertices_manager = VertexManager(
            topology,
            agents_positions=self._agents_manager.get_all_agents_positions()
        )

        self._notify_all_encounters()

        self._agents_to_move = []

        self._verbose_introduction()

        self._visited_vertices = dict()
        self._visited_edges = dict()
        self._previous_positions = dict()
        self._init_visited_edges_and_vertices()
        self._init_previous_positions()

        #Memory
        self._agent_memory = dict()

    def _init_agents_list(self, agents_list, agents_number):
        if agents_list is None:
            for _ in range(agents_number):
                agent = Agent()
                self._agents_list.append(agent)
                agent.join_to_simulation(self)
        else:
            self._agents_list = agents_list

    def _init_previous_positions(self):
        for agent in self._agents_list:
            pos = self._agents_manager.get_agent_position(agent)
            self._previous_positions[agent] = pos

    def _init_visited_edges_and_vertices(self):
        vertices = self._topology.vertices()
        edges = self._topology.edges()

        for vertex in vertices:
            self._visited_vertices[vertex] = None

        for (u, v) in edges:
            self._visited_edges[frozenset({u, v})] = None

    def anonymous(self):
        """Get the anonymity status of the simulation.

        :returns: True if the simulation is anonymous, False otherwise.
        :rtype: boolean
        """
        return self._anonymous

    def anonymous_topology(self):
        """Get the graph anonymity status of the simulation.

        :returns: True if the topology of the simulation is anonymous, False
            otherwise.
        :rtype: boolean
        """
        return self._anonymous_topology

    def ask_for_available_ports(self, agent):
        """Get the list of all the available ports from agent's current
            position.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: A list of ports.
        :rtype: list"""
        pos = self._agents_manager.get_agent_position(agent)
        return pos.get_ports()

    def ask_for_becoming(self, agent, status):
        """Set agent's status.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: New status.
        :rtype: str
        """
        id = self._agents_manager.get_agent_id(agent)
        oldstatus = self._agents_manager.get_agent_status(agent)
        self._verbose_message(
            f"agent {id} was {oldstatus} and became {status}.")
        self._agents_manager.set_agent_status(agent, status)

    def ask_for_id(self, agent):
        """Returns the id of the agent, if the model allows it.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: If the model is anonymous, returns None. Otherwise, returns
            the unique identifier of the agent.
        :rtype: int
        """
        if self.anonymous():
            self._verbose_message("warning: agents are anonymous.")
            return None

        return self._agents_manager.get_agent_id(agent)

    def ask_for_leaving_pebble(self, agent):
        """Make an agent leave a pebble, if possible.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: True if the given agent successfully left a pebble, False
            otherwise.
        :rtype: boolean
        """
        pass

    def ask_for_memory_field(self, agent, field):
        """Get an agent's memory field, if the model allows it.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :param field: A memory field
        :type field: any

        :returns: None if agents have no memory or if the given memory field
            does not exist. Otherwise, returns the value on the given agent's
            memory field.
        :rtype: any
        """
        if field in self._agent_memory.keys():
            return self._agent_memory[field]  
        else :
            return False
            
        

    def ask_for_moving(self, agent, port):
        """ Moves an agent, if possible. Namely, the agent ``position``
        attribute of the agent will be modified if:

        * it did not already move at this step;

        * its latency is not too high.

        If the simulation is asynchronous and the move is possible, then the
        agent instantly changes its position (according to the port).
        If the simulation is synchronous and the move is possible, then the
        agent is added to a list of moves to perform at the end of the step.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :param port: A port.
        :type port: int

        :returns: True if the move is legal, False otherwise.
        :rtype: boolean
        """
        is_moving_legal = self._is_moving_legal(agent, port)

        if is_moving_legal:
            self._agents_manager.agent_moved(agent, self._step)
            if not self.synchronous():
                self._move_agent(agent, port)
            else:
                self._add_to_agents_to_move(agent, port)

        return is_moving_legal

    def ask_for_port_back(self, agent):
        """Get the port number of the edge the agent comes from.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: The port for the agent to get back to the previous position.
            If the agent did not perform any move, returns None.
        :rtype: int
        """
        return self._agents_manager.get_agent_port_back(agent)

    def ask_for_position_id(self, agent):
        """Get the unique identifier of the given agent's position, if
        possible.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: If the simulation has an anonymous topology, then returns
            None.
            Otherwise, returns the unique identifier of the vertex the given
            agent is currently on.
        :rtype: int
        """

        if self.anonymous_topology():
            self._verbose_message("warning: graph is anonymous.")
            return None

        pos = self._agents_manager.get_agent_position(agent)
        return self._topology.get_vertex_id(pos)

    def ask_for_prior_knowledge_field(self, field):
        """Get a memory field from available prior knowledge, if the model
        allows it.

        :param field: A memory field
        :type field: any

        :returns: None if agents have no prior knowledge or if the given field
            does not exist. Otherwise, returns the value on the given prior
            knowledge's field.
        :rtype: any
        """
        if not self._prior_knowledge:
            self._verbose_message("warning: agents have no prior knowledge.")
            return None

        prior_knowledge = self._agents_manager.get_agents_prior_knowledge()
        if field in prior_knowledge:
            return prior_knowledge[field]
        else:
            self._verbose_message(f"warning: agent's prior knowledge has no "
                                  f"field named \"{field}\".")

        return None

    def ask_for_recovering_pebble(self, agent):
        """Give back a pebble to the given agent, if possible.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: False if the pebbles are not removable or if current position
            of the given agent do not contain pebbles from him. True otherwise.
        :rtype: boolean
        """
        pass

    def ask_for_removing_from_memory_field(self, agent, field, value):
        """Remove a value from an agent's memory field.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :param field: A memory field
        :type field: any

        :param value: The value to remove.
        :type value: any

        :returns: False if agent's have no memory, if the given field does
            not exist, or if the given value does not belong to this field. 
            True, otherwise.
        :rtype: boolean
        """
        pass

    def ask_for_remaining_pebbles(self, agent):
        """Get the number of remaining pebbles of an agent.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: The number of pebbles the agent still possesses.
        :rtype: int
        """
        pass

    def ask_for_sim_step(self):
        """Get the current step number, if possible.

        :returns: The step number, if the simulation is synchronous.
            None, otherwise.
        :rtype: int
        """
        if not self.synchronous():
            self._verbose_message("warning: simulation is asynchronous.")
            return None

        return self.get_step()

    def ask_for_status(self, agent):
        """Get the status of an agent.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: The status of the agent.
        :rtype: str
        """
        return self._agents_manager.get_agent_status(agent)

    def ask_for_position_memory_field(self, agent, field):
        """Get a vertex's memory field.

        :param vertex: A vertex.
        :type vertex: :class:`mas.graph.Vertex.Vertex`

        :param field: A memory field.
        :type field: any

        :returns: None if agents have no memory or if the given field does not
            exist. Otherwise, returns the value on the position's memory field
            of the given agent.
        :rtype: dict or any
        """

    def ask_for_writing_on_memory_field(self, agent, field, value, append):
        """Write on an agent's memory field, if possible.

        :param agent: A mobile agent.
        :type agent: :class:`mas.agent.Agent.Agent`

        :param field: A memory field
        :type field: any

        :param value: Value to add in given field.
        :type value: any

        :param append: If True, appends the value to the given memory field.
            If False, set the value of the given memory field to the given
            value.
            Default to False.
        :type append: boolean, optional

        :returns: False if agents do not have memory or if the field does not
            exist, True otherwise.
        :rtype: boolean
        """
        if field not in self._agent_memory.keys() and append == True :
            self._agent_memory[field]=value
            return value
        if field not in self._agent_memory.keys() and append == False:
            print ("La variable n'existe pas")
        if field in self._agent_memory.keys():
            self._agent_memory[field]=value
            return value










    def ask_for_writing_on_position_field(self, agent, field, value, append):
        """Write on the position's memory field of an agent, if possible.

        :param agent: A mobile agent.
        :type agent: :class:`mas.agent.Agent.Agent`

        :param field: A memory field
        :type field: any

        :param value: Value to add in given field.
        :type value: any

        :param append: If True, appends the value to the given memory field.
            If False, set the value of the given memory field to the given
            value.
            Default to False.
        :type append: boolean, optional

        :returns: False if vertices do not have memory or if the field does not
            exist, True otherwise.
        :rtype: boolean
        """
        pass

    def ask_if_position_contains_mate(self, agent):
        """Ask if several agents are on the current position of the given agent.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: True if the current position of the agent contains several
          agents, False otherwise.
        :type: boolean
        """
        return self._agents_manager.get_agent_position_contains_mate(agent)

    def ask_if_position_contains_pebble(self, agent):
        """Ask if current position of the given agent contains at least one
        pebble from him.

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: True if the current position of the agent contains a pebble
            from him, False otherwise.
        :type: boolean
        """
        pass

    def get_agent(self, id):
        """Get an agent given an identifier.

        :param id: A unique agent identifier.
        :type id: int

        :returns: The agent identified by id if it exists, None otherwise.
        :rtype: class:`mas.agent.Agent.Agent`
        """
        for agent in self._agents_list:
            if id == self._agents_manager.get_agent_id(agent):
                return agent
        return None

    def get_agents_manager(self):
        """Get the agent manager of this simulation.

        :returns: The agents manager of the simulation.
        :rtype: class:`mas.agent.AgentManager.AgentManager`
        """
        return self._agents_manager

    def get_all_agents(self):
        """Get a list of all the agents in the simulation.

        :returns: All the agents in the simulation.
        :rtype: list
        """
        return self._agents_list

    def get_agent_previous_position(self, agent):
        """Get the given agent's previous position

        :param agent: A mobile agent.
        :type agent: class:`mas.agent.Agent.Agent`

        :returns: The previous position of the given agent.
        :rtype: :class:`mas.graph.Vertex.Vertex`
        """
        return self._previous_positions[agent]

    def get_async_proba(self):
        """Get the probability for the asynchrony to prevent an agent from
        executing its algorithm at each step.

        :returns: The probability for an agent not execute its algorithm at 
            each step.
        :rtype: [0,1] double
        """
        return self._async_proba

    def get_step(self):
        """Get the current step number.

        :returns: The step number.
        :rtype: int
        """
        return self._step

    def get_vertices_manager(self):
        """Get the vertices manager.

        :returns: The vertices manager.
        :rtype: class:`mas.agent.VertexManager.VertexManager`
        """
        return self._vertices_manager

    def get_visited_edges(self):
        """Get all the visited edges since the begining of the simulation. Each
        edge is associated to the last agent that traversed it.

        :returns: A dictionnary of agents keyed by 2-sets of vertices.
        :rtype: dict
        """
        return self._visited_edges

    def get_visited_vertices(self):
        """Get all the visited vertices since the begining of the simulation. 
        Each vertex is associated to the last agent that traversed it.

        :returns: A dictionnary of agents keyed by vertices.
        :rtype: dict
        """
        return self._visited_vertices

    def model(self):
        """Get all the informations about the model of the simulation.

        :returns: A dictionnary of boolean keyed by model hypothesis.
        :rtype: dict
        """

        prior_knowledge = None
        if self._prior_knowledge:
            prior_knowledge = ""
            for key in self._agents_manager.get_agents_prior_knowledge():
                prior_knowledge += f"{key}; "
            prior_knowledge = prior_knowledge[:-1]

        return {
            "topology_type": self._topology.type(),
            "topology_order": self._topology.order(),
            "topology_size": self._topology.size(),
            "anonymous": self._anonymous,
            "synchronous": self._synchronous,
            "anonymous_topology": self._anonymous_topology,
            "agents_number": len(self._agents_list),
            "possible_latencies": self._possible_latencies,
            "agents_with_memory": self._agents_with_memory,
            "prior_knowledge": prior_knowledge,
            "nodes_with_memory": self._nodes_with_memory,
            "number_of_pebbles": self._number_of_pebbles,
            "removable_pebbles": self._removable_pebbles,
        }

    def set_verbose(self, verbose):
        """Activate or deactivate verbose mode.

        :param verbose: True for activating verbose mode, False for
            deactivating.
        :type verbose: boolean
        """
        if verbose == self._verbose:
            return

        self._verbose = verbose
        self._verbose_introduction()

    def step_algo(self):
        """Run the algorithm of every agent once, according to the model of
        the simulation. Also increases the step number.
        """

        self._update_visited_vertices()
        if self.synchronous():
            self._init_synchronous_step_algo()

        if not self.synchronous():
            random.shuffle(self._agents_list)

        for agent in self._agents_list:
            if not self.synchronous():
                if random.random() <= self._async_proba:
                    id = self._agents_manager.get_agent_id(agent)
                    self._verbose_message(f"asynchrony prevented agent "
                                          f"{id} to apply its "
                                          f"algorithm this round.")
                    continue

            self._algorithm(agent)

        if self.synchronous():
            self._move_multiple_agents(self._agents_to_move)

        self._update_visited_edges()
        self._step += 1

    def synchronous(self):
        """Get the synchronicity status of the simulation.

        :returns: True if the simulation is synchronous, False otherwise.
        :rtype: boolean
        """
        return self._synchronous

    def topology(self):
        """Get the topology of the simulation.

        :returns: The topology of the simulation.
        :rtype: class:`mas.graph.Graph.Graph`
        """
        return self._topology

    def _add_to_agents_to_move(self, agent, port):
        self._agents_to_move.append((agent, port))

    def _init_synchronous_step_algo(self):
        self._agents_to_move = []

    def _is_moving_legal(self, agent, port):
        legal = True

        agent_position = self._agents_manager.get_agent_position(agent)
        id = self._agents_manager.get_agent_id(agent)
        if agent_position.get_neighbor_by_port(port) is None:
            legal = False
            self._verbose_message(f"warning: agent {id} is "
                                  f"trying to move through non existing port "
                                  f"{port}.")

        elif self._agents_manager.get_agent_last_move(agent) == self._step:
            legal = False
            self._verbose_message(f"warning: agent {id} "
                                  f"already moved this round.")

        elif self._synchronous:
            agent_latency = self._agents_manager.get_agent_latency(agent)
            legal = (self._step % agent_latency) == 0
            if not legal:
                self._verbose_message(f"warning: agent {id}'s "
                                      f"latency  does not allow him to move this "
                                      f"round.")

        return legal

    def _move_agent(self, agent, port):
        oldpos, newpos = self._agents_manager.move_agent(agent, port)
        self._vertices_manager.move_agent(agent, oldpos, newpos)
        self._notify_encounter_on_position(oldpos)
        self._notify_encounter_on_position(newpos)

    def _move_multiple_agents(self, agents_with_ports):
        """Move multiple agents along given edges.

          :param agents_with_ports: Vectors of the form (agent, port)
          :type agents_with_ports: list of tuples
            (class:`mas.agent.Agent.Agent`, int)
        """
        for (agent, port) in agents_with_ports:
            oldpos, newpos = self._agents_manager.move_agent(agent, port)
            self._vertices_manager.move_agent(agent, oldpos, newpos)
        self._notify_all_encounters()

    def _notify_all_encounters(self):
        for vertex in self._vertices_manager.get_occupied_positions():
            self._notify_encounter_on_position(vertex)

    def _notify_encounter_on_position(self, vertex):
        agents_on_vertex = self._vertices_manager.get_agents_on_vertex(vertex)
        numerous_agents = len(agents_on_vertex) > 1
        for agent in agents_on_vertex:
            self._agents_manager.update_agent_position_contains_mate(
                agent,
                numerous_agents
            )

    def _update_visited_edges(self):
        for agent in self._agents_list:
            old_pos = self._agents_manager.get_agent_position(agent)
            new_pos = self._previous_positions[agent]
            if old_pos != new_pos:
                self._visited_edges[frozenset({old_pos, new_pos})] = agent

    def _update_visited_vertices(self):
        for agent in self._agents_list:
            pos = self._agents_manager.get_agent_position(agent)
            self._visited_vertices[pos] = agent
            self._previous_positions[agent] = pos

    def _verbose_introduction(self):
        if self._verbose:  # pragma: no cover
            verbose_str = "\nMODEL:\n======\n"
            for (key, value) in self.model().items():
                verbose_str += f"{key}: {value}\n"
            print(verbose_str)

    def _verbose_message(self, error_message):
        if self._verbose:  # pragma: no cover
            print(error_message)
