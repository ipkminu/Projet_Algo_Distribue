from mas.visualization.GraphViz import GraphViz
from mas.graph.Vertex import Vertex

from mas.graph.graph_generator import clique

res_path = "tests/resources/"

G = GraphViz()
G.init_from_file(res_path + "testGraph.txt")

u = Vertex(1)
v = Vertex(3)


def test_get_padding():
    assert G.get_padding() == 10


def test_max_x_y_coordinate():
    xmax, ymax = G.get_max_x_y_coordinate()
    p = G.get_padding()

    for vertex in G.vertices():
        x, y = G.get_vertex_position(vertex)
        assert xmax + 2*p >= x
        assert ymax + 2*p >= y


def test_min_x_y_coordinate():
    xmin, ymin = 0, 0
    for vertex in G.vertices():
        x, y = G.get_vertex_position(vertex)
        p = G.get_padding()

        assert xmin + p <= x
        assert ymin + p <= y


def test_add_and_remove_vertex():
    G = GraphViz()

    G.add_vertex(u)
    G.add_vertex(v)

    assert G.vertices().keys() == {u, v}

    G.remove_vertex(v)
    assert G.vertices().keys() == {u}


def test_add_and_remove_edge():
    G = GraphViz()

    G.add_vertex(u)
    assert not G.add_edge(u, v)
    assert not G.remove_edge(u, v)

    G.add_vertex(v)
    assert G.add_edge(u, v)
    assert not G.add_edge(u, v)
    assert G.remove_edge(u, v)
    assert not G.remove_edge(u, v)


def test_set_layout_method():
    G = GraphViz()
    assert G.set_layout_method("planar")
    assert not G.set_layout_method("flower")


def test_get_layout_method():
    G = GraphViz()
    G.set_layout_method("planar")
    assert G.get_layout_method() == "planar"

    G.set_layout_method("flower")
    assert G.get_layout_method() == "planar"


def test_get_all_layout_methods():
    all = set([
        "circo",
        "circular",
        "dot",
        "kamada_kawai",
        "random",
        "spectral",
        "spring",
        "spiral"
    ])

    K5 = clique(5)
    G = GraphViz()
    G.init_from_graph(K5)

    assert set(G.get_all_layout_methods()) == all

    u = G.get_vertex_by_id(0)
    v = G.get_vertex_by_id(1)
    G.remove_edge(u, v)

    all.add("planar")
    assert set(G.get_all_layout_methods()) == all


def test_get_and_set_vertices_radius():
    G = GraphViz()

    assert G.get_vertices_radius() == 6

    G.set_vertices_radius(3)
    assert G.get_vertices_radius() == 3


def test_get_and_set_max_x_y_coordinate():
    G = GraphViz()

    assert G.get_max_x_y_coordinate() == (700, 700)

    G.set_max_x_coordinate(300)
    G.set_max_y_coordinate(400)
    assert G.get_max_x_y_coordinate() == (300, 400)


def test_remove_vertex():
    G = GraphViz()

    u = Vertex(1)

    G.add_vertex(u)

    assert G.remove_vertex(u)

def test_get_vertex_by_tag():
    G = GraphViz()
    u = Vertex(0)
    v = Vertex(1)
    G.add_vertex(u)
    G.add_vertex(v)

    assert G.get_vertex_by_tag("vertex0") == u
    assert G.get_vertex_by_tag("vertex1") == v
    assert G.get_vertex_by_tag("bidule3") is None
    assert G.get_vertex_by_tag("agent1") is None
