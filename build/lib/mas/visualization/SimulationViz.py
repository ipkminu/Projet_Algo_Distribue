from mas.agent.Simulation import Simulation
import tkinter.font as tkFont

from matplotlib import cm, colors
import numpy
import math

import logging


class SimulationViz():
    """Based on :class:`mas.agent.Simulation.Simulation`, encapsulates methods
    and parameters to draw Simulation objects."""

    def __init__(self, simulation, graphViz):
        """A simulation with drawing methods.

        :param simulation: The simulation to visualize.
        :type simulation: :class:`mas.agent.Simulation.Simulation`

        :param graphViz: A graph visualizer.
        :type graphViz: :class:`mas.visualization.GraphViz.GraphViz`
        """

        self._simulation = simulation
        self._graphViz = graphViz

        self._init_agents_graphics()

        self._agents_colors = dict()
        self._init_agents_colors()

    def draw_agent(self, canvas, agent, vertex):
        """Draw a single agent.

        :param agent: The agent to draw.
        :type agent: :class:`mas.agent.Agent.Agent`

        :param canvas: Canvas in which to draw the agent.
        :type canvas: tkinter.Canvas
          (http://tkinter.fdex.eu/doc/caw.html)

        :param vertex: Position of the agent in the graph.
        :type vertex: :class:`mas.graph.Vertex.Vertex`
        """
        x, y = self._graphViz.get_vertex_position(vertex)

        agent_color = self._agents_colors[agent]["color"]
        agent_border_color = self._agents_colors[agent]["border_color"]
        agent_id_color = self._agents_colors[agent]["id_color"]

        manager = self._simulation.get_agents_manager()
        id = manager.get_agent_id(agent)

        r = self._agents_radius
        canvas.create_oval(x - r, y - r, x + r, y + r,
                           fill=agent_color,
                           outline=agent_border_color,
                           width=self._agents_border_thickness,
                           tags=["agents", f"agent{id}", "agent_graphics"]
                           )
        if not self._simulation.anonymous():
            canvas.create_text(
                x,
                y,
                font=tkFont.Font(size=self._agents_id_size, weight='bold'),
                fill=agent_id_color,
                text=id,
                tags=[
                    "text",
                    "agents",
                    "agent_texts",
                    f"agent{id}",
                    f"text_agent{id}"
                ]
            )

    def draw_all_agents(self, canvas):
        """Draw all the agents.

        :param canvas: Canvas in which to draw the agents.
        :type canvas: tkinter.Canvas
          (http://tkinter.fdex.eu/doc/caw.html)
        """
        agents_manager = self._simulation.get_agents_manager()
        agents = self._simulation.get_all_agents()
        for agent in agents:
            position = agents_manager.get_agent_position(agent)
            self.draw_agent(canvas, agent, position)

    def draw_step_number(self, canvas):
        """Write the step number on south-east corner of the canvas.

        :param canvas: Canvas in which to write the step number.
        :type canvas: tkinter.Canvas
          (http://tkinter.fdex.eu/doc/caw.html)

        """
        canvas.update()
        canvas.create_text(
            canvas.winfo_width() - 10,
            canvas.winfo_height() - 10,
            anchor="se",
            font=tkFont.Font(size=15, weight='bold'),
            fill="black",
            text=self._simulation.get_step(),
            tags=["text", "step_text"]
        )

    def get_agent_by_tag(self, tag):
        """TBD"""
        
        if not tag[5:].isdigit():
            logging.error(f"{tag}[5:] is not an integer.")
            return None

        id = int(tag[5:])
        if tag[:5] != "agent":
            logging.error(f"{tag} does not correspond to an agent tag.")
            return None

        return self.get_simulation().get_agent(id)

    def get_agent_color(self, agent):
        """TBD"""
        color = self._agents_colors[agent]["color"]
        border_color = self._agents_colors[agent]["border_color"]
        id_color = self._agents_colors[agent]["id_color"]
        return (color, border_color, id_color)

    def get_agent_information(self, agent):
        """TBD"""
        information = ""
        manager = self.get_simulation().get_agents_manager()
        information += (
            f"id: {manager.get_agent_id(agent)};\n"
            f"status: {manager.get_agent_status(agent)};\n"
            f"agent position: {manager.get_agent_position(agent)};\n"
            f"agent latency: {manager.get_agent_latency(agent)};\n"
            f"position contains mate: {manager.get_agent_position_contains_mate(agent)};\n"
            f"port back: {manager.get_agent_port_back(agent)};\n"
            f"last move: step {manager.get_agent_last_move(agent)};\n"
        )

        if manager.get_agents_prior_knowledge() == dict():
            information += f"prior knowledge: Empty;\n"
        else:
            information += (
                f"prior knowledge:\n"
                f"================\n\n"
            )
            for (key, value) in manager.get_agents_prior_knowledge().items():
                information += (
                    f"{key}:\n"
                    f"{value}\n"
                    f"\n"
                )

        # if manager.get_agent_memory(agent) == dict():
        #     information += f"Memory: Empty;\n"
        # else:
        #     information += (
        #         f"Memory:\n"
        #         f"=======\n\n"
        #     )
        #     for (key, value) in manager.get_agent_memory(agent).items():
        #         information += (
        #             f"{key}:\n"
        #             f"{value}\n"
        #             f"\n"
        #         )

        return information

    def get_agents_border_thickness(self):
        """TBD"""
        return self._agents_border_thickness

    def get_agents_radius(self):
        """TBD"""
        return self._agents_radius

    def get_simulation(self):
        """Get the simulation on which is based this SimulationViz.

        :returns: The simulation on which is based this SimulationViz.
        :rtype: :class:`mas.agent.Simulation.Simulation`
        """
        return self._simulation

    def get_vertex_information(self, vertex):
        """TBD"""
        information = (
            f"id: {self._graphViz.get_vertex_id(vertex)};\n"
            f"name: {vertex.name()};\n"
        )

        if len(vertex.get_neighbors()) == 0:
            information += f"ports_to_neighbors: None;\n"
        else:
            information += "ports_to_neighbors: {\n"
            for (port, neighbor) in vertex.get_port_associations().items():
                neighbor_id = self._graphViz.get_vertex_id(neighbor)
                information += f"\t{port}: {neighbor_id};\n"
            information += "}\n"

        # manager = self._simulation.get_vertices_manager()

        # if not manager.vertex_contains_pebbles(vertex):
        #     information += f"pebbles: None;\n"
        # else:
        #     information += "pebbles:{\n"
        #     for (key, value) in manager.get_pebbles_on_vertex(vertex).items():
        #         agents_manager = self._simulation.get_agents_manager()
        #         agent_id = agents_manager.get_agent_id(key)
        #         information += f"\t{agent_id}: {value};\n"
        #     information += "}\n"
    
        # if manager.get_vertex_memory(vertex) == dict():
        #     information += f"Memory: Empty;\n"
        # else:
        #     information += (
        #         f"Memory:\n"
        #         f"=======\n\n"
        #     )
        #     for (key, value) in manager.get_vertex_memory(vertex).items():
        #         information += (
        #             f"{key}:\n"
        #             f"{value}\n"
        #             f"\n"
        #         )

        return information

    def step_algo(self):
        """Execute :meth:`mas.agent.Simulation.Simulation.step_algo()` from the
        current simulation once.
        """
        self._simulation.step_algo()

    def set_verbose(self, verbose):
        """Activate or deactivate verbose mode.

        :param verbose: True for activating verbose mode, False for
            deactivating.
        :type verbose: boolean
        """
        self._simulation.set_verbose(verbose)

    def _init_agents_colors(self):
        agents = self._simulation.get_all_agents()
        agents_nb = len(agents)

        colours = cm.rainbow(numpy.linspace(0, 1, agents_nb*2))
        c = 0
        for agent in agents:
            self._agents_colors[agent] = dict()
            self._agents_colors[agent]["color"] = colors.to_hex(colours[c])
            self._agents_colors[agent]["id_color"] = _dark_or_light(colours[c])
            self._agents_colors[agent]["border_color"] = colors.to_hex(
                colours[c+1])
            c = c+2

    def _init_agents_graphics(self):
        #self._agents_color = "green"
        #self._agents_id_color = "white"
        #self._agents_border_color = "orange"
        self._agents_radius = 16
        self._agents_id_size = 12
        self._agents_border_thickness = 1

    def mark_position(self, canvas, position, agent_id, color):
        """TBD"""
        pos_id = self._simulation.topology().get_vertex_id(position)

        x, y = self._graphViz.get_vertex_position(position)
        r = self._graphViz.get_vertices_radius() * 2 / 3

        canvas.create_oval(x - r, y - r, x + r,  y + r,
                           fill=color,
                           tags=["vertex_marks",
                                 f"vertex_mark{agent_id}",
                                 f"mark_vertex{pos_id}"])

    def mark_edge(self, canvas, edge, agent_id, color):
        """TBD"""
        (u, v) = tuple(edge)

        graph = self._graphViz
        xu, yu = graph.get_vertex_position(u)
        xv, yv = graph.get_vertex_position(v)

        thickness = graph.get_edge_thickness() + 2
        dashstyle = graph.get_edge_dashstyle()

        edge_id = f"({graph.get_vertex_id(u)},{graph.get_vertex_id(v)})"
        canvas.create_line(xu, yu, xv, yv,
                           fill=color,
                           dash=dashstyle,
                           width=thickness,
                           tags=["edge_marks",
                                 f"edge_mark{agent_id}",
                                 f"edge_mark{edge_id}"])

    def mark_every_edge(self, canvas):
        """TBD"""
        # TODO: À vérifier
        agents = self._simulation.get_all_agents()
        manager = self._simulation.get_agents_manager()
        for agent in agents:
            id = manager.get_agent_id(agent)
            oldpos = self._simulation.get_agent_previous_position(agent)
            newpos = manager.get_agent_position(agent)
            color = self._agents_colors[agent]["color"]
            if oldpos != newpos:
                edge = frozenset({oldpos, newpos})
                self.mark_edge(canvas, edge, id, color)

    def mark_every_visited_edge(self, canvas):
        """TBD"""
        manager = self._simulation.get_agents_manager()
        visited_edges = self._simulation.get_visited_edges()
        for edge in visited_edges:
            if visited_edges[edge] is None:
                continue
            agent = visited_edges[edge]
            agent_id = manager.get_agent_id(agent)
            color = self._agents_colors[agent]["color"]
            self.mark_edge(canvas, edge, agent_id, color)

    def mark_every_agent_position(self, canvas):
        """TBD"""
        agents = self._simulation.get_all_agents()
        manager = self._simulation.get_agents_manager()
        for agent in agents:
            id = manager.get_agent_id(agent)
            pos = self._simulation.get_agent_previous_position(agent)
            color = self._agents_colors[agent]["color"]
            self.mark_position(canvas, pos, id, color)

    def mark_every_visited_position(self, canvas):
        """TBD"""
        manager = self._simulation.get_agents_manager()
        visited_vertices = self._simulation.get_visited_vertices()
        for pos in visited_vertices:
            if visited_vertices[pos] is None:
                continue
            agent = visited_vertices[pos]
            agent_id = manager.get_agent_id(agent)
            color = self._agents_colors[agent]["color"]
            self.mark_position(canvas, pos, agent_id, color)

    def remove_occupied_position_marks(self, canvas):
        """TBD"""
        agents = self._simulation.get_all_agents()
        manager = self._simulation.get_agents_manager()
        for agent in agents:
            pos = manager.get_agent_position(agent)
            pos_id = self._simulation.topology().get_vertex_id(pos)
            canvas.delete(f"mark_vertex{pos_id}")

    def remove_just_traversed_edge_marks(self, canvas):
        agents = self._simulation.get_all_agents()
        manager = self._simulation.get_agents_manager()
        for agent in agents:
            oldpos = self._simulation.get_agent_previous_position(agent)
            newpos = manager.get_agent_position(agent)
            graph = self._graphViz
            edge_id = f"({graph.get_vertex_id(newpos)},{graph.get_vertex_id(oldpos)})"
            canvas.delete(f"mark_vertex{edge_id}")

    def remove_vertex_marks(self, agent, canvas):
        """TBD"""
        manager = self._simulation.get_agents_manager()
        id = manager.get_agent_id(agent)
        canvas.delete(f"vertex_mark{id}")


def _dark_or_light(color):
    [r, g, b] = colors.to_rgb(color)
    hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
    if (hsp > 127.5):
        return "#ffffff"
    else:
        return "#000000"
