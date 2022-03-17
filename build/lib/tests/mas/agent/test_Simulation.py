from mas.agent.Simulation import Simulation
from mas.agent.Agent import Agent

from mas.graph.Graph import Graph
from mas.graph.Vertex import Vertex
from mas.graph.graph_generator import line, cycle

import random


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


def _follow_port_zero(agent):
    agent.move_along(0)


def test_topology():
    G, _ = _trivial_graph()
    sim = Simulation(G)
    assert sim.topology() == G


def test_get_agent():
    G, _ = _trivial_graph()

    a1 = Agent(desired_id=0)
    a2 = Agent(desired_id=4)

    sim1 = Simulation(G, agents_list=[a1])
    sim2 = Simulation(G, agents_list=[a1, a2])

    assert sim1.get_agent(0) == a1
    assert sim1.get_agent(1) is None

    assert sim2.get_agent(0) == a1
    assert sim2.get_agent(1) is None
    assert sim2.get_agent(4) == a2


def test_get_all_agents():
    G, _ = _trivial_graph()

    a1 = Agent()
    a2 = Agent()
    sim = Simulation(G, agents_list=[a1, a2])

    assert sim.get_all_agents() == [a1, a2]


def test_default_model():
    G, _ = _trivial_graph()

    sim = Simulation(G)

    assert sim.model() == {
        "topology_type": "unknown",
        "topology_order": 1,
        "topology_size": 0,
        "anonymous": False,
        "synchronous": True,
        "anonymous_topology": False,
        "agents_number": 1,
        "possible_latencies": [1],
        "agents_with_memory": False,
        "prior_knowledge": None,
        "nodes_with_memory": False,
        "number_of_pebbles": 0,
        "removable_pebbles": True,
    }


def test_model():
    G = line(3)

    sim = Simulation(G,
                     anonymous=True,
                     synchronous=False,
                     anonymous_topology=True,
                     agents_list=[Agent(), Agent()],
                     possible_latencies=[1, 2, 3],
                     agents_with_memory=True,
                     prior_knowledge={"knowledge": "test"},
                     nodes_with_memory=True,
                     number_of_pebbles = 3,
                     removable_pebbles = False
    )

    assert sim.model() == {
        "topology_type": "line",
        "topology_order": 3,
        "topology_size": 2,
        "anonymous": True,
        "synchronous": False,
        "anonymous_topology": True,
        "agents_number": 2,
        "possible_latencies": [1, 2, 3],
        "agents_with_memory": True,
        "prior_knowledge": "knowledge;",
        "nodes_with_memory": True,
        "number_of_pebbles": 3,
        "removable_pebbles": False,
    }


def test_get_step():
    G, _ = _trivial_graph()

    sim = Simulation(G)

    assert sim.get_step() == 1

    sim.step_algo()
    assert sim.get_step() == 2

    sim.step_algo()
    assert sim.get_step() == 3

def test_synchronous_step_algo():
    G, u, v = _edge_graph()
    
    a = Agent(desired_position=u)
    sim = Simulation(G, agents_list=[a], synchronous=True, algorithm=_follow_port_zero)
    a.join_to_simulation(sim)

    manager = sim.get_agents_manager()

    assert manager.get_agent_position(a) == u
    sim.step_algo()
    assert manager.get_agent_position(a) == v
    sim.step_algo()
    assert manager.get_agent_position(a) == u

def test_asynchronous_step_algo(mocker):
    G, u, v = _edge_graph()
    
    a = Agent(desired_position=u)
    sim = Simulation(G, agents_list=[a], synchronous=False, algorithm=_follow_port_zero)
    a.join_to_simulation(sim)
    
    manager = sim.get_agents_manager()

    assert manager.get_agent_position(a) == u

    mocker.patch.object(random, 'random', return_value=0)
    sim.step_algo()
    assert manager.get_agent_position(a) == u
    sim.step_algo()
    assert manager.get_agent_position(a) == u
    sim.step_algo()
    assert manager.get_agent_position(a) == u

    mocker.patch.object(random, 'random', return_value=1)
    sim.step_algo()
    assert manager.get_agent_position(a) == v
    sim.step_algo()
    assert manager.get_agent_position(a) == u
    sim.step_algo()
    assert manager.get_agent_position(a) == v

def test_get_async_proba():
    G, _ = _trivial_graph()
    sim = Simulation(G, async_proba=0.4)
    assert sim.get_async_proba() == 0.4


def test_get_agent_previous_position():
    G, u, v = _edge_graph()

    a = Agent(desired_position=u)
    sim = Simulation(G, agents_list=[a], algorithm=_follow_port_zero)
    a.join_to_simulation(sim)

    assert sim.get_agent_previous_position(a) == u
    sim.step_algo()
    assert sim.get_agent_previous_position(a) == u
    sim.step_algo()
    assert sim.get_agent_previous_position(a) == v


def test_get_visited_vertices():
    G = cycle(3)
    u = G.get_vertex_by_id(0)
    v = G.get_vertex_by_id(2)
    w = G.get_vertex_by_id(1)

    a = Agent(desired_position=u)
    sim = Simulation(G, agents_list=[a], algorithm=_follow_port_zero)
    a.join_to_simulation(sim)

    assert sim.get_visited_vertices() == {u: None, v: None, w: None}
    sim.step_algo()
    assert sim.get_visited_vertices() == {u: a, v: None, w: None}
    sim.step_algo()
    assert sim.get_visited_vertices() == {u: a, v: a, w: None}
    sim.step_algo()
    assert sim.get_visited_vertices() == {u: a, v: a, w: a}


def test_get_visited_edges():
    G = cycle(3)
    u = G.get_vertex_by_id(0)
    v = G.get_vertex_by_id(2)
    w = G.get_vertex_by_id(1)

    a = Agent(desired_position=u)
    sim = Simulation(G, agents_list=[a], algorithm=_follow_port_zero)
    a.join_to_simulation(sim)

    uv = frozenset({u, v})
    vw = frozenset({v, w})
    uw = frozenset({u, w})

    assert sim.get_visited_edges() == {uv: None, vw: None, uw: None}
    sim.step_algo()
    assert sim.get_visited_edges() == {uv: a, vw: None, uw: None}
    sim.step_algo()
    assert sim.get_visited_edges() == {uv: a, vw: a, uw: None}
    sim.step_algo()
    assert sim.get_visited_edges() == {uv: a, vw: a, uw: a}

def test_init_position_contains_mate():
    G, u, v = _edge_graph()

    a1 = Agent(desired_id=1, desired_position=u)
    a2 = Agent(desired_id=2, desired_position=u)
    a3 = Agent(desired_id=3, desired_position=v)

    sim = Simulation(G, agents_list=[a1, a2, a3])
    manager = sim.get_agents_manager()

    assert manager.get_agent_position_contains_mate(a1)
    assert manager.get_agent_position_contains_mate(a2)
    assert not manager.get_agent_position_contains_mate(a3)

def test_notify_encounters_synchronous():
    G = Graph()
    u, v, w = Vertex(0), Vertex(1), Vertex(2)
    G.add_vertex(u), G.add_vertex(v), G.add_vertex(w)
    G.add_edge(u,w), G.add_edge(v,w), G.add_edge(u,v)

    a1 = Agent(desired_position=u)
    a2 = Agent(desired_position=v)
    a3 = Agent(desired_position=w)
    sim = Simulation(
        G, 
        agents_list=[a1, a2, a3], 
        algorithm=_follow_port_zero,
        synchronous=True
    )
    a1.join_to_simulation(sim)
    a2.join_to_simulation(sim)
    a3.join_to_simulation(sim)

    manager = sim.get_agents_manager()
    assert not manager.get_agent_position_contains_mate(a1)
    assert not manager.get_agent_position_contains_mate(a2)
    assert not manager.get_agent_position_contains_mate(a3)

    sim.step_algo()
    assert manager.get_agent_position_contains_mate(a1)
    assert manager.get_agent_position_contains_mate(a2)
    assert not manager.get_agent_position_contains_mate(a3)

