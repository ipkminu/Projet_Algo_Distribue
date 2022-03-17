from pip import main
from mas.graph.Vertex import Vertex


def test_get_and_set_name():
    u = Vertex(1)
    assert u.name() == 1

    u.set_name("test")
    assert u.name() == "test"


def test_add_and_get_neighbor():
    u = Vertex(1)
    v = Vertex(2)
    w = Vertex(3)

    u.add_neighbor(v)
    assert u.get_neighbors() == [v]
    u.add_neighbor(w)
    assert u.get_neighbors() == [v, w]


def test_remove_neighbor():
    u = Vertex(1)
    v = Vertex(2)
    w = Vertex(3)

    u.add_neighbor(v)
    u.remove_neighbor(w)
    assert u.get_neighbors() == [v]
    u.remove_neighbor(v)
    assert u.get_neighbors() == []


def test_copy():
    u1 = Vertex(13)
    v = Vertex(1)
    w = Vertex(2)

    u1.add_neighbor(v)
    u1.add_neighbor(w)

    u2 = u1.copy()

    assert u1 != u2
    assert u1.name() == u2.name()

    uneighbors = [neighbor.name() for neighbor in u1.get_neighbors()]
    vneighbors = [neighbor.name() for neighbor in u2.get_neighbors()]

    assert uneighbors == vneighbors


def test_get_ports():
    u = Vertex(1)
    v = Vertex(2)
    w = Vertex(3)

    u.add_neighbor(v)
    u.add_neighbor(w)

    assert set(u.get_ports()) == {0, 1}


def test_get_ports_after_remove_and_add():

    u = Vertex(1)
    v = Vertex(2)
    w = Vertex(3)
    x = Vertex(4)

    u.add_neighbor(v)
    u.add_neighbor(w)

    u.remove_neighbor(v)
    assert u.get_ports() == [1]

    u.add_neighbor(x)
    assert set(u.get_ports()) == {0, 1}

    u.add_neighbor(v)
    assert set(u.get_ports()) == {0, 1, 2}


def test_get_neighbor_by_port():
    u = Vertex(1)
    v = Vertex(2)
    w = Vertex(3)
    x = Vertex(4)

    u.add_neighbor(v)
    u.add_neighbor(w)
    assert u.get_neighbor_by_port(1) == w

    u.remove_neighbor(w)
    assert u.get_neighbor_by_port(1) is None

    u.add_neighbor(x)
    assert u.get_neighbor_by_port(1) == x


def test_get_port_associations():
    u = Vertex(1)
    v = Vertex(2)
    w = Vertex(3)

    u.add_neighbor(v)
    u.add_neighbor(w)

    assert u.get_port_associations() == {0: v, 1: w}


def test_reset_port_associations():
    u = Vertex(1)
    v = Vertex(2)
    w = Vertex(3)
    x = Vertex(4)

    u.add_neighbor(v)
    u.add_neighbor(w)
    u.add_neighbor(x)

    assert u.get_neighbor_by_port(4) is None

    assert u.get_ports() == [0, 1, 2]
    assert u.get_neighbor_by_port(2) == x

    assert u.reset_port_associations({2: v, 4: w, 8: x})
    assert u.get_ports() == [2, 4, 8]
    assert u.get_neighbor_by_port(2) == v

def test_reset_port_associations_with_maintain_unused_ports():
    u = Vertex(1)
    v = Vertex(2)
    w = Vertex(3)
    x = Vertex(4)
    y = Vertex(5)
    z = Vertex(6)

    u.add_neighbor(v)
    u.add_neighbor(w)
    u.add_neighbor(x)

    assert u.reset_port_associations({1: v, 3: w, 5: x}, 
                                     maintain_unused_ports=True)
    assert u.get_ports() == [1, 3, 5]
    u.add_neighbor(y)
    u.add_neighbor(z)
    assert set(u.get_ports()) == set([0, 1, 2, 3, 5])
    assert u.get_neighbor_by_port(0) == y
    assert u.get_neighbor_by_port(1) == v
    assert u.get_neighbor_by_port(2) == z
    assert u.get_neighbor_by_port(3) == w

def test_reset_port_associations_with_compression():
    u = Vertex(1)
    v = Vertex(2)
    w = Vertex(3)
    x = Vertex(4)

    u.add_neighbor(v)
    u.add_neighbor(w)
    u.add_neighbor(x)

    new_associations = {2: w, 4: x, 8: v}
    compressed_new_associations = {0: w, 1: x, 2: v}
    assert u.reset_port_associations(new_associations, compress=True)

    assert u.get_neighbor_by_port(4) is None
    assert u.get_neighbor_by_port(8) is None

    assert u.get_ports() == [0, 1, 2]
    assert u.get_neighbor_by_port(0) == w
    assert u.get_neighbor_by_port(1) == x
    assert u.get_neighbor_by_port(2) == v
    assert u.get_port_associations() == compressed_new_associations


def test_wrong_reset_port_associations():
    u = Vertex(1)
    v = Vertex(2)
    w = Vertex(3)
    x = Vertex(4)

    u.add_neighbor(v)
    u.add_neighbor(w)

    assert not u.reset_port_associations({0: v, 1: w, 2: x})
    assert not u.reset_port_associations({0: v, 1: x})


def test_get_port_by_neighbor():
    u = Vertex(1)
    v = Vertex(2)
    w = Vertex(3)
    x = Vertex(4)

    u.add_neighbor(v)
    u.add_neighbor(w)
    u.add_neighbor(x)

    assert u.get_port_by_neighbor(x) == 2

    u.reset_port_associations({3: v, 5: w, 9: x})
    assert u.get_port_by_neighbor(x) == 9

    y = Vertex(5)
    assert u.get_port_by_neighbor(y) is None
