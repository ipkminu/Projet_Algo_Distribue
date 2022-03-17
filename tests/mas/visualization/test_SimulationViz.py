from mas.agent.Simulation import Simulation
from mas.agent.Agent import Agent
from mas.visualization.SimulationViz import SimulationViz
from mas.graph.graph_generator import *
from mas.graph.Vertex import Vertex


def _follow_port_zero(agent):
    agent.move_along(0)


def test_get_agent_by_tag():
    G = Graph()
    u = Vertex(0)
    G.add_vertex(u)

    a = Agent(desired_id=3)
    sim = Simulation(G, agents_list=[a])
    a.join_to_simulation(sim)
    simviz = SimulationViz(sim, G)

    assert simviz.get_agent_by_tag("agent3") == a
    assert simviz.get_agent_by_tag("machins3") is None
    assert simviz.get_agent_by_tag("agent1") is None
    assert simviz.get_agent_by_tag("chose3") is None


def test_get_agent_information1():
    G = Graph()
    u = Vertex(0)
    G.add_vertex(u)

    a = Agent(desired_id=23, desired_position=u)
    info = {"info1": "ceci est une information", "info2": "ça aussi"}
    sim = Simulation(
        G, agents_list=[a], agents_with_memory=True, prior_knowledge=info)
    a.join_to_simulation(sim)
    simviz = SimulationViz(sim, G)

    expected_memory = (
        f"id: 23;\n"
        f"status: ;\n"
        f"agent position: {u};\n"
        f"agent latency: 1;\n"
        f"position contains mate: False;\n"
        f"port back: None;\n"
        f"last move: step 0;\n"
        f"prior knowledge:\n"
        f"================\n"
        f"\n"
        f"info1:\n"
        f"ceci est une information\n"
        f"\n"
        f"info2:\n"
        f"ça aussi\n"
        f"\n"
        f"Memory: Empty;\n"
    )
    memory = simviz.get_agent_information(a)

    assert memory == expected_memory


def test_get_agent_information2():
    G = cycle(3)
    u = G.get_vertex_by_id(0)
    v = G.get_vertex_by_id(2)

    a = Agent(desired_id=23, desired_position=u, desired_latency=2)
    sim = Simulation(
        G, agents_list=[a], agents_with_memory=True, algorithm=_follow_port_zero)
    a.join_to_simulation(sim)
    manager = sim.get_agents_manager()
    manager.set_agent_memory(a, "info1", "ceci est une information")
    manager.set_agent_memory(a, "info2", "ça aussi")
    manager.set_agent_status(a, "test")
    simviz = SimulationViz(sim, G)

    sim.step_algo()
    sim.step_algo()

    expected_memory = (
        f"id: 23;\n"
        f"status: test;\n"
        f"agent position: {v};\n"
        f"agent latency: 2;\n"
        f"position contains mate: False;\n"
        f"port back: 1;\n"
        f"last move: step 2;\n"
        f"prior knowledge: Empty;\n"
        f"Memory:\n"
        f"=======\n"
        f"\n"
        f"info1:\n"
        f"ceci est une information\n"
        f"\n"
        f"info2:\n"
        f"ça aussi\n"
        f"\n"
    )
    memory = simviz.get_agent_information(a)

    assert memory == expected_memory


def test_get_agent_information3():
    G = Graph()
    u = Vertex(0)
    G.add_vertex(u)

    a1 = Agent(desired_id=23, desired_position=u)
    a2 = Agent(desired_id=12, desired_position=u)
    sim = Simulation(G, agents_list=[a1, a2])
    a1.join_to_simulation(sim)
    a2.join_to_simulation(sim)
    simviz = SimulationViz(sim, G)

    expected_memory = (
        f"id: 23;\n"
        f"status: ;\n"
        f"agent position: {u};\n"
        f"agent latency: 1;\n"
        f"position contains mate: True;\n"
        f"port back: None;\n"
        f"last move: step 0;\n"
        f"prior knowledge: Empty;\n"
        f"Memory: Empty;\n"
    )
    memory = simviz.get_agent_information(a1)

    assert memory == expected_memory

def test_get_vertex_information():
    G = Graph()
    u = Vertex("toto")
    G.add_vertex(u)

    sim = Simulation(G)
    simviz = SimulationViz(sim, G)

    expected_memory = (
        f"id: 0;\n"
        f"name: toto;\n"
        f"ports_to_neighbors: None;\n"
        f"pebbles: None;\n"
        f"Memory: Empty;\n"
    )
    memory = simviz.get_vertex_information(u)

    assert memory == expected_memory

def test_get_vertex_information2():
    G = Graph()
    u, v, w = Vertex(0), Vertex(1), Vertex(2)
    G.add_vertex(u), G.add_vertex(v), G.add_vertex(w)
    G.add_edge(u,v), G.add_edge(u,w)

    a1 = Agent(desired_id=23, desired_position=u)
    a2 = Agent(desired_id=12, desired_position=u)
    sim = Simulation(G, agents_list=[a1, a2], number_of_pebbles=3)
    a1.join_to_simulation(sim)
    a2.join_to_simulation(sim)
    simviz = SimulationViz(sim, G)

    manager = sim.get_vertices_manager()
    manager.put_agent_pebble_on_vertex(a1, u)
    manager.put_agent_pebble_on_vertex(a1, u)
    manager.put_agent_pebble_on_vertex(a2, u)

    manager.set_vertex_memory(u, "test_field", "test_value")

    expected_memory = (
        f"id: 0;\n"
        f"name: 0;\n"
        f"ports_to_neighbors: {{\n"
        f"\t0: 1;\n"
        f"\t1: 2;\n"
        f"}}\n"
        f"pebbles:{{\n"
        f"\t23: 2;\n"
        f"\t12: 1;\n"
        f"}}\n"
        f"Memory:\n"
        f"=======\n"
        f"\n"
        f"test_field:\n"
        f"test_value\n"
        f"\n"
    )
    memory = simviz.get_vertex_information(u)

    assert memory == expected_memory