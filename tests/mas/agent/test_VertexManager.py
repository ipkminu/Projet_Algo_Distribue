from mas.graph.Graph import Graph
from mas.graph.Vertex import Vertex

from mas.agent.VertexManager import VertexManager
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

def test_set_and_get_vertex_memory():
  G, u, v = _edge_graph()

  manager = VertexManager(G)

  manager.set_vertex_memory(u, "vertex_value", 3)
  manager.set_vertex_memory(v, "vertex_value", 1)

  assert manager.get_vertex_memory(u, "vertex_value") == 3
  assert manager.get_vertex_memory(v, "vertex_value") == 1

  manager.set_vertex_memory(u, "vertex_value", 3, append=True)
  manager.set_vertex_memory(v, "vertex_value", 2)

  assert manager.get_vertex_memory(u, "vertex_value") == [3,3]
  assert manager.get_vertex_memory(v, "vertex_value") == 2

  manager.set_vertex_memory(u, "vertex_color", "blue")

  assert manager.get_vertex_memory(u) == {
    "vertex_value": [3,3], 
    "vertex_color": "blue"
  }

def test_get_occupied_positions():
  G, u, _ = _edge_graph()
  a1 = Agent()

  manager = VertexManager(G, {a1: u})
  assert manager.get_occupied_positions() == [u]

def test_get_agents_on_vertex():
  G, u, v = _edge_graph()
  w = Vertex(2)
  G.add_vertex(w)

  a1 = Agent()
  a2 = Agent()
  a3 = Agent()

  manager = VertexManager(G, {a1: u, a2: u, a3: w})
  assert manager.get_agents_on_vertex(u) == [a1, a2]
  assert manager.get_agents_on_vertex(v) == []
  assert manager.get_agents_on_vertex(w) == [a3]

def test_move_agent():
  G, u, v = _edge_graph()
  a1 = Agent()
  a2 = Agent()
  manager = VertexManager(G, {a1: u})

  assert manager.move_agent(a1, u, v)
  assert manager.get_agents_on_vertex(v) == [a1]

  assert not manager.move_agent(a1, u, v)
  assert manager.get_agents_on_vertex(v) == [a1]

  assert not manager.move_agent(a2, v, u)
  assert manager.get_agents_on_vertex(u) == []

def test_vertex_contains_pebbles():
  G, u = _trivial_graph()
  a1 = Agent()
  manager = VertexManager(G, {a1: u})

  assert not manager.vertex_contains_pebbles(u)
  manager.put_agent_pebble_on_vertex(a1, u)
  assert manager.vertex_contains_pebbles(u)

def test_vertex_contains_pebbles_agent_given():
  G, u = _trivial_graph()
  a1 = Agent()
  a2 = Agent()
  manager = VertexManager(G, {a1: u, a2: u})

  manager.put_agent_pebble_on_vertex(a1, u)
  assert manager.vertex_contains_pebbles(u, agent=a1)
  assert not manager.vertex_contains_pebbles(u, agent=a2)

def test_get_nb_of_pebbles_on_vertex():
  G, u = _trivial_graph()
  a1 = Agent()
  a2 = Agent()
  manager = VertexManager(G, {a1: u, a2: u})

  assert manager.get_nb_of_pebbles_on_vertex(u) == 0
  manager.put_agent_pebble_on_vertex(a1, u)
  assert manager.get_nb_of_pebbles_on_vertex(u) == 1
  manager.put_agent_pebble_on_vertex(a2, u)
  assert manager.get_nb_of_pebbles_on_vertex(u) == 2

def test_get_nb_pebbles_on_vertex_agent_given():
  G, u = _trivial_graph()
  a1 = Agent()
  a2 = Agent()
  manager = VertexManager(G, {a1: u, a2: u})

  assert manager.get_nb_of_pebbles_on_vertex(u) == 0
  manager.put_agent_pebble_on_vertex(a1, u)
  assert manager.get_nb_of_pebbles_on_vertex(u,agent=a1) == 1
  manager.put_agent_pebble_on_vertex(a2, u)
  assert manager.get_nb_of_pebbles_on_vertex(u,agent=a2) == 1

def test_remove_agent_pebble_from_vertex():
  G, u = _trivial_graph()
  a1 = Agent()
  manager = VertexManager(G, {a1: u})

  assert manager.get_nb_of_pebbles_on_vertex(u) == 0
  assert not manager.remove_agent_pebble_from_vertex(a1, u)

  manager.put_agent_pebble_on_vertex(a1, u)
  assert manager.get_nb_of_pebbles_on_vertex(u) == 1
  assert manager.remove_agent_pebble_from_vertex(a1, u)
  assert manager.get_nb_of_pebbles_on_vertex(u) == 0
  assert not manager.vertex_contains_pebbles(u)

  assert not manager.remove_agent_pebble_from_vertex(a1, u)
  