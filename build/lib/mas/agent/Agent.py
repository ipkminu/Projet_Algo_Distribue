class Agent:
    """Mobile agents."""

    def __init__(self,
                 desired_id=None,
                 desired_position=None,
                 desired_latency=None):
        """A mobile agent.

        :param desired_id: Desired unique identifier.
          Default to None.
        :type desired_id: int, optional

        :param desired_position: Desired starting position.
          Default to None.
        :type desired_position: :class:`mas.graph.Vertex.Vertex`, optional

        :param desired_latency: Number of rounds to wait before doing an action.
          This parameter is ignored and considered as random in asynchronous
          models.
          Default to None.
        :type desired_latency: int, optional
        """
        self._desired_id = desired_id
        self._desired_initial_position = desired_position
        self._desired_latency = desired_latency
        self._simulation = None
        self._moves_nb = 0

    def available_ports(self):
        """Get the list of all the available ports from current position.

        :returns: A list of ports.
        :rtype: list
        """
        return self._simulation.ask_for_available_ports(self)

    def become(self, status):
        """Change the status of the agent.

        :param status: New status.
        :type status: string
        """
        self._simulation.ask_for_becoming(self, status)

    def desired_id(self):
        """Get the desired id of this agent.

        :returns: The desired id.
        :rtype: int
        """
        return self._desired_id

    def desired_initial_position(self):
        """Get the desired starting position of this agent.

        :returns: A vertex.
        :rtype: :class:`mas.graph.Vertex.Vertex`
        """
        return self._desired_initial_position

    def desired_latency(self):
        """Get the desired latency of this agent.

        :returns: The desired latency.
        :rtype: int
        """
        return self._desired_latency

    def get_id(self):
        """Get the id of the agent, if possible.

        :returns: If the simulation to which the agent is linked is anonymous,
          returns None. Otherwise, returns the unique id of the agent.
        :rtype: int
        """
        return self._simulation.ask_for_id(self)

    def get_moves_nb(self):
        """Get the total number of moves done by the agent.

        :returns: The total number of moves done by the agent.
        :rtype: int
        """
        return self._moves_nb

    def get_port_back(self):
        """Get the port number of the edge the agent comes from.

        :returns: The port to get back to the previous position. If the agent
          did not perform any move, returns None.
        :rtype: int
        """
        return self._simulation.ask_for_port_back(self)

    def get_position_id(self):
        """Get the id of the vertex the agent is currently on.

        :returns: If the simulation to which the agent is linked has an
          anonymous topology, returns None. Otherwise, returns the unique id of
          the vertex the agent is currently on.
          See :meth:`mas.agent.Simulation.Simulation.get_vertex_id()`.
        :rtype: int
        """
        return self._simulation.ask_for_position_id(self)

    def get_sim_step(self):
        """Get the current step number in the simulation.

        :returns: If the simulation is synchronous, returns the number of rounds
          since its begining. Otherwise, returns None.
          See :meth:`mas.agent.Simulation.Simulation.get_step()`.
        :rtype: int
        """
        return self._simulation.ask_for_sim_step()

    def join_to_simulation(self, simulation):
        """Link the agent to a simulation. This is mandatory for calling most
          of the agent's methods.

          :param simulation: The simulation into which the agent should take
            place.
          :type simulation: :class:`mas.agent.Simulation.Simulation`
        """
        self._simulation = simulation

    def leave_pebble(self):
        """Leave a pebble on current position

        :returns: True if the simulation allowed the agent to leave a pebble,
            False otherwise.
        :rtype: boolean
        """
        return self._simulation.ask_for_leaving_pebble(self)

    def move_along(self, port):
        """Move the agent along a given port, if the simulation allows it.

        :param port: Port of the edge to move on.
        :type port: int

        :returns: True if the simulation allowed the agent to move. False
          otherwise.
          See :meth:`mas.agent.Simulation.Simulation.ask_for_moving()`.
        :rtype: boolean
        """
        is_moving_legal = self._simulation.ask_for_moving(self, port)
        if is_moving_legal:
            self._moves_nb += 1
        return is_moving_legal

    def position_contains_mate(self):
        """Ask if current position contains an other agent.

        :returns: True if the current position of the agent contains several
          agents, False otherwise.
        :type: boolean
        """
        return self._simulation.ask_if_position_contains_mate(self)

    def position_contains_pebble(self):
        """Ask if the agent left a pebble on current position.

        :returns: True if the current position of the agent contains a pebble
            left by this agent, False otherwise
        :type: boolean
        """
        return self._simulation.ask_if_position_contains_pebble(self)

    def read_memory_field(self, field):
        """Read access to a given agent's memory field.

        :returns: The value in given memory field if it exists and if the
            simulation allowed reading this field.
        :rtype: any
        """
        return self._simulation.ask_for_memory_field(self, field)

    def read_position_memory_field(self, field):
        """Read access to position's given memory field.

        :returns: The value in given memory field if it exists and if the
            simulation allowed reading this field.
        :rtype: any
        """
        return self._simulation.ask_for_position_memory_field(self, field)

    def read_prior_knowledge_field(self, field):
        """Read access to a given agent's prior knowledge field.

        :returns: The value in given memory field if it exists and if the
            simulation allowed reading this field.
        :rtype: any
        """
        return self._simulation.ask_for_prior_knowledge_field(field)

    def recover_pebble(self):
        """recover a pebble on current position, if possible.

        :returns: True if the position contained a current agent's pebble, and
            if the  simulation allowed the agent to recover this pebble,
            False otherwise.
        :rtype: boolean
        """
        return self._simulation.ask_for_recovering_pebble(self)

    def remaining_pebbles(self):
        """Get the number of pebbles left (and not recovered) by the agent on
        its current position.

        :returns: The number of current agent's pebbles on its position
        :rtype: int
        """
        return self._simulation.ask_for_remaining_pebbles(self)

    def remove_from_memory_field(self, field, value):
        """Remove a value from an agent's memory field.

        :returns: True if the simulation allowed the removal, False otherwise.
        :rtype: boolean
        """
        return self._simulation.ask_for_removing_from_memory_field(self,
                                                                   field,
                                                                   value)

    def status(self):
        """Get the status of the agent.

        :returns: The status of the agent.
        :rtype: string
        """
        return self._simulation.ask_for_status(self)

    def wait(self):
        """Do nothing. Used, for script legibility, to specify that the agent
        has currently no action to perform.
        """
        pass  # pragma: no cover

    def write_on_memory_field(self, field, value, append=False):
        """Write access to a given agent's memory field.

        :param field: A memory field
        :type field: any

        :param value: Value to add in given field.
        :type value: any

        :param append: If True, appends the value to the given memory field.
            If False, set the value of the given memory field to the given
            value.
            Default to False.
        :type append: boolean, optional

        :returns: True if the simulation allowed writing on the given field.
        :rtype: boolean
        """
        return self._simulation.ask_for_writing_on_memory_field(self,
                                                                field,
                                                                value,
                                                                append)

    def write_on_position_memory_field(self, field, value, append=False):
        """Write access to current position's memory field.

        :param field: A memory field
        :type field: any

        :param value: Value to add in given field.
        :type value: any

        :param append: If True, appends the value to the given memory field.
            If False, set the value of the given memory field to the given
            value.
            Default to False.
        :type append: boolean, optional

        :returns: True if the simulation allowed writing on the given field.
        :rtype: boolean
        """
        return self._simulation.ask_for_writing_on_position_field(self,
                                                                  field,
                                                                  value,
                                                                  append)
