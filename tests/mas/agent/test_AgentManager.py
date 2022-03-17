from mas.agent.AgentManager import AgentManager
from mas.graph.Graph import Graph
from mas.graph.Vertex import Vertex
from mas.graph.graph_generator import random_graph

from mas.agent.Agent import Agent


def _trivial_graph():
    G = Graph()
    u = Vertex(1)
    G.add_vertex(u)
    return G, u


def _edge_graph():
    G = Graph()
    u = Vertex(1)
    v = Vertex(2)
    G.add_vertex(u)
    G.add_vertex(v)
    G.add_edge(u, v)

    return G, u, v


def test_init_desired_id():
    G, _ = _trivial_graph()

    a1 = Agent(desired_id=3)
    a2 = Agent(desired_id=3)

    manager = AgentManager([a1, a2], G)

    assert manager.get_agent_id(a1) == 3
    assert not manager.get_agent_id(a2) == 3


def test_init_possible_latencies():
    G, _ = _trivial_graph()

    a1 = Agent(desired_latency=1)
    a2 = Agent(desired_latency=None)

    manager = AgentManager([a1, a2], G, possible_latencies=[2, 3])

    assert manager.get_agent_latency(a1) == 1
    assert manager.get_agent_latency(a2) in [2, 3]


def test_init_desired_position():
    G = random_graph(1000, 0)
    u = G.get_vertex_by_id(0)

    a = Agent(desired_position=u)

    manager = AgentManager([a], G)
    assert manager.get_agent_position(a) == u


def test_move_agent():
    G, u, v = _edge_graph()

    a = Agent(desired_id=1, desired_position=u)

    manager = AgentManager([a], G)

    assert manager.get_agent_position(a) == u

    manager.move_agent(a, 0)
    assert manager.get_agent_position(a) == v
    

def test_get_agents_prior_knowledge():
    G, _ = _trivial_graph()
    a = Agent()

    information = {"field_test": "value_test"}
    manager = AgentManager([a], G, prior_knowledge=information)

    assert manager.get_agents_prior_knowledge() == information


def test_init_and_get_agent_memory():
    G, _ = _trivial_graph()
    a1 = Agent()
    a2 = Agent()

    information = {"graphsize": 1, "agentsnb": 2}
    manager = AgentManager([a1, a2], G, prior_knowledge=information)

    assert manager.get_agent_memory(a1) == {}
    assert manager.get_agents_prior_knowledge() == information

    assert manager.get_agent_memory(a1, field="nonexistingfield") is None


def test_set_and_get_agent_memory():
    G, _ = _trivial_graph()
    a1 = Agent()
    a2 = Agent()

    information = {"graphsize": 1, "agentsnb": 2}
    manager = AgentManager([a1, a2], G, prior_knowledge=information)

    assert manager.get_agent_memory(a1) == {}
    assert manager.get_agent_memory(a2) == {}

    manager.set_agent_memory(a1, "graph", G)

    assert manager.get_agent_memory(a1) == {"graph": G}
    assert manager.get_agent_memory(a2) == {}
    assert manager.get_agent_memory(a1, field="graph") == G


def test_get_all_agents_memory():
    G, _ = _trivial_graph()
    a1 = Agent()
    a2 = Agent()

    information = {"graphsize": 1}
    manager = AgentManager([a1, a2], G, prior_knowledge=information)
    manager.set_agent_memory(a1, "field_test", "value_test")

    assert manager.get_all_agents_memory() == {
        a1: {"field_test": "value_test"},
        a2: {}
    }


def test_modes_set_agent_memory():
    G, u, v = _edge_graph()
    a = Agent()

    manager = AgentManager([a], G)

    assert manager.get_agent_memory(a) == dict()

    manager.set_agent_memory(a, "graph", G, append=False)
    assert manager.get_agent_memory(a, field="graph") == G

    manager.set_agent_memory(a, "vertices", u, append=True)
    assert manager.get_agent_memory(a, field="vertices") == [u]

    manager.set_agent_memory(a, "vertices", v, append=True)
    assert manager.get_agent_memory(a, field="vertices") == [u, v]

    manager.set_agent_memory(a, "vertices", u, append=False)
    assert manager.get_agent_memory(a, field="vertices") == u


def test_remove_value_from_agent_memory():
    G, _ = _trivial_graph()
    a = Agent()

    manager = AgentManager([a], G)
    manager.set_agent_memory(a, "numbers", [1, 2])

    assert manager.get_agent_memory(a, field="numbers") == [1, 2]

    assert manager.remove_from_agent_memory(a, "numbers", value=1)
    assert manager.get_agent_memory(a, field="numbers") == [2]

    assert not manager.remove_from_agent_memory(a, "numbers", value=1)

    manager.set_agent_memory(a, "numbers", 1)
    assert not manager.remove_from_agent_memory(a, "numbers", value=2)
    assert manager.remove_from_agent_memory(a, "numbers", value=1)
    assert manager.get_agent_memory(a) == dict()


def test_remove_field_from_agent_memory():
    G, _ = _trivial_graph()
    a = Agent()

    manager = AgentManager([a], G)

    manager.set_agent_memory(a, "numbers", [1, 2])

    assert manager.get_agent_memory(a) == {"numbers": [1, 2]}

    assert manager.remove_from_agent_memory(a, "numbers")
    assert manager.get_agent_memory(a) == dict()

    assert not manager.remove_from_agent_memory(a, "nonexistingfield")


def test_init_agent_status():
    G, _ = _trivial_graph()
    a1 = Agent()
    a2 = Agent()

    manager = AgentManager([a1, a2], G)

    assert manager.get_agent_status(a1) == ""
    assert manager.get_agent_status(a2) == ""


def test_set_and_get_agent_status():
    G, _ = _trivial_graph()
    a1 = Agent()
    a2 = Agent()

    manager = AgentManager([a1, a2], G)

    manager.set_agent_status(a1, "newstatus")

    assert manager.get_agent_status(a1) == "newstatus"
    assert manager.get_agent_status(a2) == ""


def test_init_and_get_agents_pebbles():
    G, _ = _trivial_graph()
    a1 = Agent()
    a2 = Agent()

    manager = AgentManager([a1, a2], G, number_of_pebbles=2)
    assert manager.get_remaining_pebbles_of_agent(a1) == 2
    assert manager.get_remaining_pebbles_of_agent(a2) == 2

def test_add_and_remove_pebble_to_agent():
    G, _ = _trivial_graph()
    a = Agent()

    manager = AgentManager([a], G, number_of_pebbles=1)
    assert manager.get_remaining_pebbles_of_agent(a) == 1
    assert not manager.add_pebble_to_agent(a)
    assert manager.remove_pebble_from_agent(a)
    assert manager.get_remaining_pebbles_of_agent(a) == 0
    assert not manager.remove_pebble_from_agent(a)
    assert manager.add_pebble_to_agent(a)
    assert manager.get_remaining_pebbles_of_agent(a) == 1

