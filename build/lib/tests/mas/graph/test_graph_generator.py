from mas.graph.graph_generator import *

def test_line_ports():
  G = line(3)
  u = G.get_vertex_by_id(0)
  v = G.get_vertex_by_id(1)
  w = G.get_vertex_by_id(2)

  assert u.get_neighbor_by_port(0) is None
  assert v.get_neighbor_by_port(0) == u
  assert w.get_neighbor_by_port(0) == v

  assert u.get_neighbor_by_port(1) == v
  assert v.get_neighbor_by_port(1) == w
  assert w.get_neighbor_by_port(1) is None

def test_cycle_ports():
  G = cycle(3)
  u = G.get_vertex_by_id(0)
  v = G.get_vertex_by_id(1)
  w = G.get_vertex_by_id(2)

  assert u.get_neighbor_by_port(0) == w
  assert v.get_neighbor_by_port(0) == u
  assert w.get_neighbor_by_port(0) == v

  assert u.get_neighbor_by_port(1) == v
  assert v.get_neighbor_by_port(1) == w
  assert w.get_neighbor_by_port(1) == u

