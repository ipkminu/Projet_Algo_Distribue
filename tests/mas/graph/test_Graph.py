
from mas.graph.Graph import Graph
from mas.graph.Vertex import Vertex
from mas.graph.graph_generator import clique, tree

import numpy as np
import os

path = os.getcwd()
tests_path = os.path.join(path, "tests")
test_res_path = os.path.join(tests_path, "resources")
test_out_path = os.path.join(tests_path, "out")

try:
    os.mkdir(test_out_path)
except OSError:
    print(f"Creation of the directory {test_out_path} failed")


M = np.array([
    [0, 1, 0],
    [1, 0, 1],
    [0, 1, 0]
])


def test_add_and_get_vertex():
    G = Graph()

    u = Vertex(1)
    v = Vertex(3)

    G.add_vertex(u)
    G.add_vertex(v)
    assert G.vertices().keys() == {u, v}

    assert not G.add_vertex(v)


def test_get_vertexByID():
    G = Graph()

    u = Vertex(1)
    v = Vertex(3)

    G.add_vertex(u)
    G.add_vertex(v)
    assert G.get_vertex_by_id(0) == u
    assert G.get_vertex_by_id(1) == v
    assert G.get_vertex_by_id(2) is None


def test_get_vertex_by_name():
    G = Graph()

    u = Vertex(1)
    v = Vertex(3)
    w = Vertex(5)

    G.add_vertex(u)
    G.add_vertex(v)

    assert G.get_vertex_by_name(1) == u
    assert G.get_vertex_by_name(3) == v

    G.remove_vertex(v)
    assert G.get_vertex_by_name(3) is None

    G.add_vertex(w)
    assert G.get_vertex_by_name(5) == w


def test_remove_vertex():
    G = Graph()

    u = Vertex(1)
    v = Vertex(3)

    G.add_vertex(u)
    G.add_vertex(v)

    assert G.vertices().keys() == {u, v}

    assert G.remove_vertex(v)
    assert G.vertices().keys() == {u}

    assert not G.remove_vertex(v)


def test_id_in_G():
    G = Graph()

    u = Vertex(1)
    v = Vertex(3)
    w = Vertex(5)
    x = Vertex(9)

    G.add_vertex(u)
    G.add_vertex(v)
    G.add_vertex(w)
    G.add_vertex(x)

    verticesIds = [a.name() for a in G.vertices()]
    assert verticesIds == [1, 3, 5, 9]

    idsInG = [G.get_vertex_id(a) for a in G.vertices()]
    assert idsInG == [0, 1, 2, 3]


def test_id_after_remove_and_add():
    G = Graph()

    u = Vertex(1)
    v = Vertex(3)
    w = Vertex(5)
    x = Vertex(9)

    G.add_vertex(u)
    G.add_vertex(v)
    G.add_vertex(w)

    idsInG = {G.get_vertex_id(a) for a in G.vertices()}
    assert idsInG == {0, 1, 2}

    G.remove_vertex(v)
    idsInG = {G.get_vertex_id(a) for a in G.vertices()}
    assert idsInG == {0, 1}

    G.add_vertex(v)
    idsInG = {G.get_vertex_id(a) for a in G.vertices()}
    assert idsInG == {0, 1, 2}

    G.add_vertex(x)
    idsInG = {G.get_vertex_id(a) for a in G.vertices()}
    assert idsInG == {0, 1, 2, 3}


def test_add_edge():
    G = Graph()

    u = Vertex(1)
    v = Vertex(3)
    w = Vertex(5)

    G.add_vertex(u)
    G.add_vertex(v)
    assert G.add_edge(u, v)

    assert not G.add_edge(u, w)

    G.add_vertex(w)
    G.add_edge(u, w)

    assert G.edges() == {(u, v), (u, w)}


def test_add_existing_edge():
    G = Graph()

    u = Vertex(1)
    v = Vertex(3)

    G.add_vertex(u)
    G.add_vertex(v)

    G.add_edge(u, v)
    assert not G.add_edge(u, v)


def test_remove_edge():
    G = Graph()

    u = Vertex(1)
    v = Vertex(3)
    w = Vertex(5)
    x = Vertex(9)

    G.add_vertex(u)
    G.add_vertex(v)
    G.add_vertex(w)
    G.add_edge(u, v)
    G.add_edge(u, w)

    assert G.remove_edge(u, v)
    assert not G.remove_edge(u, v)
    assert G.edges() == {(u, w)}

    assert G.remove_edge(w, u)


def test_remove_edge_when_directed_neighbor():
    G = Graph()

    u = Vertex(1)
    v = Vertex(3)
    w = Vertex(5)

    G.add_vertex(u)
    G.add_vertex(v)
    G.add_vertex(w)

    G.add_edge(u, v)
    G.add_edge(u, w)

    u.remove_neighbor(v)
    w.remove_neighbor(u)

    assert not G.remove_edge(u, v)
    assert not G.remove_edge(u, w)


def test_add_edge_when_directed_neighbor():
    G = Graph()

    u = Vertex(1)
    v = Vertex(3)
    w = Vertex(5)

    u.add_neighbor(v)
    w.add_neighbor(u)

    G.add_vertex(u)
    G.add_vertex(v)
    G.add_vertex(w)

    assert not G.add_edge(u, v)
    assert not G.add_edge(u, w)


def test_graph_to_str():
    G = Graph()

    u = Vertex(1)
    v = Vertex(3)
    w = Vertex(5)

    G.add_vertex(u)
    G.add_vertex(v)
    G.add_vertex(w)
    G.add_edge(u, v)
    G.add_edge(u, w)

    assert G.__str__(
    ) == "Graph{\n\t(0)1 : {3, 5},\n\t(1)3 : {1},\n\t(2)5 : {1}\n}\n"


def test_init_from_graph():
    G1 = Graph()

    u = Vertex(1)
    v = Vertex(3)
    w = Vertex(5)

    G1.add_vertex(u)
    G1.add_vertex(v)
    G1.add_vertex(w)
    G1.add_edge(u, v)
    G1.add_edge(u, w)
    G1.add_edge(v, w)

    G2 = Graph()
    G2.init_from_graph(G1)

    assert set([v.name() for v in G2.vertices()]) == {1, 3, 5}
    assert set([(u.name(), v.name())
               for (u, v) in G2.edges()]) == {(1, 3), (1, 5), (3, 5)}


def test_init_from_adjacency_matrix():
    G = Graph()
    G.init_from_adjacency_matrix(M)

    assert [a.name() for a in G.get_vertex_by_id(0).get_neighbors()] == [1]
    assert [a.name() for a in G.get_vertex_by_id(1).get_neighbors()] == [0, 2]
    assert [a.name() for a in G.get_vertex_by_id(2).get_neighbors()] == [1]


def test_init_from_file():
    G = Graph()
    file = os.path.join(test_res_path, "testGraph.txt")
    G.init_from_file(file)

    assert [a.name() for a in G.get_vertex_by_name(
        "0").get_neighbors()] == ["1", "342"]
    assert [a.name() for a in G.get_vertex_by_name(
        "1").get_neighbors()] == ["0", "2"]
    assert [a.name() for a in G.get_vertex_by_name(
        "2").get_neighbors()] == ["1", "342"]
    assert [a.name() for a in G.get_vertex_by_name(
        "342").get_neighbors()] == ["0", "2"]


def test_order():
    G = Graph()

    G.init_from_adjacency_matrix(M)
    assert G.order() == 3


def test_size():
    G = Graph()

    G.init_from_adjacency_matrix(M)
    assert G.size() == 2


def test_order_after_remove_and_add():
    G = Graph()
    G.init_from_adjacency_matrix(M)

    vertices = list(G.vertices())
    a = vertices[0]

    G.remove_vertex(a)
    assert G.order() == 2

    G.add_vertex(a)
    assert G.order() == 3


def test_compute_adjacency_matrix():
    G = Graph()

    u = Vertex(1)
    v = Vertex(3)
    w = Vertex(5)

    G.add_vertex(u)
    G.add_vertex(v)
    G.add_vertex(w)
    G.add_edge(u, v)
    G.add_edge(v, w)

    assert np.array_equal(G.adjacency_matrix(), M)


def test_compute_adjacency_matrix_after_remove_and_add():
    G = Graph()

    u = Vertex(1)
    v = Vertex(3)
    w = Vertex(5)

    G.add_vertex(u)
    G.add_vertex(v)
    G.add_vertex(w)
    G.add_edge(u, v)
    G.add_edge(v, w)

    newM = M.copy()
    newM[0, 1] = 0
    newM[1, 0] = 0
    G.remove_edge(u, v)
    assert np.array_equal(G.adjacency_matrix(), newM)

    G.remove_vertex(u)
    assert np.array_equal(G.adjacency_matrix(), np.array([[0, 1], [1, 0]]))


def test_compute_distance_matrix():
    G = Graph()
    G.init_from_adjacency_matrix(M)

    assert np.array_equal(G.distance_matrix(), np.array(
        [[0, 1, 2], [1, 0, 1], [2, 1, 0]]))


def test_compute_distance_matrix_after_remove_and_add():
    G = Graph()
    G.init_from_adjacency_matrix(M)

    a = G.get_vertex_by_id(2)
    G.remove_vertex(a)
    assert np.array_equal(G.distance_matrix(), np.array([[0, 1], [1, 0]]))


def test_distance():
    G = Graph()
    G.init_from_adjacency_matrix(M)

    a = G.get_vertex_by_id(0)
    b = G.get_vertex_by_id(1)
    c = G.get_vertex_by_id(2)
    assert G.distance(a, c) == 2
    assert G.distance(b, c) == 1


def test_diameter():
    G = Graph()
    G.init_from_adjacency_matrix(M)

    assert G.diameter() == 2


def test_moving_along_ports():
    G = Graph()

    u = Vertex("u")
    v = Vertex("v")
    w = Vertex("w")

    G.add_vertex(u)
    G.add_vertex(v)
    G.add_vertex(w)

    G.add_edge(u, v)
    G.add_edge(v, w)
    G.add_edge(w, u)

    vertex = G.get_vertex_by_id(0)
    assert vertex == u
    vertex = vertex.get_neighbor_by_port(0)
    assert vertex == v
    vertex = vertex.get_neighbor_by_port(1)
    assert vertex == w
    vertex = vertex.get_neighbor_by_port(1)
    assert vertex == u


def test_is_planar():
    G = clique(5)

    assert not G.is_planar()

    u = G.get_vertex_by_id(0)
    v = G.get_vertex_by_id(1)
    G.remove_edge(u, v)
    assert G.is_planar()


def test_save_graphids():
    G1 = Graph()

    u1 = Vertex("u")
    v1 = Vertex("v")

    G1.add_vertex(u1)
    G1.add_vertex(v1)
    G1.add_edge(u1, v1)

    file = os.path.join(test_out_path, "save_graphids.txt")
    G1.save(file)

    G2 = Graph()
    G2.init_from_file(file)

    u2 = G2.get_vertex_by_id(0)
    v2 = G2.get_vertex_by_id(1)

    assert G2.order() == G1.order()
    assert G2.size() == G1.size()
    assert (u2, v2) in G2.edges()


def test_save_realids():
    G1 = Graph()

    u1 = Vertex("u")
    v1 = Vertex("v")

    G1.add_vertex(u1)
    G1.add_vertex(v1)
    G1.add_edge(u1, v1)

    file = os.path.join(test_out_path, "save_realids.txt")
    G1.save(file, ids="real")

    G2 = Graph()
    G2.init_from_file(file)

    u2 = G2.get_vertex_by_id(0)
    v2 = G2.get_vertex_by_id(1)

    assert G2.order() == G1.order()
    assert G2.size() == G1.size()
    assert u2.name() == "u"
    assert v2.name() == "v"
    assert (u2, v2) in G2.edges()


def test_is_connected():
    G1 = tree(10)

    assert G1.is_connected()

    G2 = Graph()
    file = os.path.join(test_res_path, "disconnected_graph.txt")
    G2.init_from_file(file)
