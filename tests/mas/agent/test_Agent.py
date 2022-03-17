from mas.agent.Agent import Agent
from mas.agent.Simulation import Simulation

from mas.graph.Graph import Graph
from mas.graph.Vertex import Vertex


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


def move(agent):
    p = agent.available_ports()[0]
    agent.move_along(p)


def test_status_and_become():
    G, _ = _trivial_graph()
    a = Agent(2)

    sim = Simulation(G, agents_list=[a])
    a.join_to_simulation(sim)

    assert a.status() == ""

    a.become("new status")
    assert a.status() == "new status"


def test_get_id_named():
    G, u = _trivial_graph()

    a = Agent(desired_id=2, desired_position=u)

    sim = Simulation(G, agents_list=[a], anonymous=False)
    a.join_to_simulation(sim)
    assert a.get_id() == 2


def test_get_id_anonymous():
    G, u = _trivial_graph()

    a = Agent(desired_id=1, desired_position=u)

    sim = Simulation(G, agents_list=[a], anonymous=True)
    a.join_to_simulation(sim)
    assert a.get_id() is None


def test_move_along():
    G, u, _ = _edge_graph()

    a = Agent(desired_id=1, desired_position=u)

    sim = Simulation(G, agents_list=[a])

    a.join_to_simulation(sim)

    assert a.move_along(0)


def test_multiple_move_along():
    G, u, _ = _edge_graph()

    a = Agent(desired_id=1, desired_position=u)

    sim = Simulation(G, agents_list=[a])

    a.join_to_simulation(sim)

    assert a.move_along(0)
    assert not a.move_along(0)


def test_move_along_with_latency():
    G, u, _ = _edge_graph()

    a = Agent(desired_id=1, desired_position=u, desired_latency=2)

    sim = Simulation(G, agents_list=[a])
    a.join_to_simulation(sim)

    assert not a.move_along(0)


def test_move_along_nonexisting_port():
    G, u, _ = _edge_graph()

    a = Agent(desired_id=1, desired_position=u)

    sim = Simulation(G, agents_list=[a])
    a.join_to_simulation(sim)

    assert not a.move_along(2)


def test_get_position_id_named_graph():
    G, _, v = _edge_graph()

    a = Agent(desired_id=1, desired_position=v)

    sim = Simulation(G, agents_list=[a], anonymous_topology=False)
    a.join_to_simulation(sim)
    assert a.get_position_id() == 1


def test_get_position_id_anonymous_topology():
    G, _, v = _edge_graph()

    a = Agent(desired_id=1, desired_position=v)

    sim = Simulation(G, agents_list=[a], anonymous_topology=True)
    a.join_to_simulation(sim)
    assert a.get_position_id() is None


def test_port_back():
    G, u, v = _edge_graph()

    u.reset_port_associations({5: v})
    v.reset_port_associations({3: u})

    agent = Agent(desired_id=1, desired_position=u)

    sim = Simulation(G, agents_list=[agent], algorithm=move)
    agent.join_to_simulation(sim)

    assert agent.get_port_back() is None

    sim.step_algo()
    assert agent.get_port_back() == 3

    sim.step_algo()
    assert agent.get_port_back() == 5


def test_get_moves_nb():
    G, _, _ = _edge_graph()

    agent = Agent(desired_id=0)
    sim = Simulation(G, agents_list=[agent], algorithm=move)
    agent.join_to_simulation(sim)

    assert agent.get_moves_nb() == 0

    sim.step_algo()
    assert agent.get_moves_nb() == 1

    sim.step_algo()
    assert agent.get_moves_nb() == 2


def test_get_sim_step_synchronous():
    G, _ = _trivial_graph()

    agent = Agent(desired_id=0)
    sim = Simulation(G, agents_list=[agent])
    agent.join_to_simulation(sim)

    assert agent.get_sim_step() == 1

    sim.step_algo()
    assert agent.get_sim_step() == 2

    sim.step_algo()
    assert agent.get_sim_step() == 3


def test_get_sim_step_asynchronous():
    G, _ = _trivial_graph()

    agent = Agent(desired_id=0)
    sim = Simulation(G, synchronous=False, agents_list=[agent])
    agent.join_to_simulation(sim)

    assert agent.get_sim_step() is None

    sim.step_algo()
    assert agent.get_sim_step() is None


def test_read_memory_field_agents_with_memory():
    G, _ = _trivial_graph()

    agent = Agent(desired_id=0)
    sim = Simulation(G, agents_list=[agent], agents_with_memory=True)
    agent.join_to_simulation(sim)
    manager = sim.get_agents_manager()
    manager.set_agent_memory(agent, "field_test", "value_test")

    assert agent.read_memory_field("field_test") == "value_test"


def test_read_nonexisting_memory_field():
    G, _ = _trivial_graph()

    agent = Agent(desired_id=0)
    sim = Simulation(G, agents_list=[agent], agents_with_memory=True)
    agent.join_to_simulation(sim)

    assert agent.read_memory_field("nonexisting_field") is None


def test_read_memory_field_agents_without_memory():
    G, _ = _trivial_graph()

    agent = Agent(desired_id=0)
    sim = Simulation(G, agents_list=[agent], agents_with_memory=False)
    agent.join_to_simulation(sim)
    manager = sim.get_agents_manager()
    manager.set_agent_memory(agent, "field_test", "value_test")

    assert agent.read_memory_field("field_test") is None


def test_write_on_memory_field_agents_with_memory():
    G, _ = _trivial_graph()
    agent = Agent(desired_id=0)
    sim = Simulation(G, agents_list=[agent], agents_with_memory=True)
    agent.join_to_simulation(sim)

    assert agent.write_on_memory_field("field", "value")
    assert agent.read_memory_field("field") == "value"

    assert agent.write_on_memory_field("field", "newvalue")
    assert agent.read_memory_field("field") == "newvalue"

    assert agent.write_on_memory_field("field", "oldvalue", append=True)
    assert agent.read_memory_field("field") == ["newvalue", "oldvalue"]


def test_write_on_memory_field_agents_without_memory():
    G, _ = _trivial_graph()

    agent = Agent(desired_id=0)
    sim = Simulation(G, agents_list=[agent], agents_with_memory=False)
    agent.join_to_simulation(sim)

    assert not agent.write_on_memory_field("value", "newfield")
    assert agent.read_memory_field("newfield") is None


def test_write_on_prior_knowledge_field():
    G, _ = _trivial_graph()
    info = {"field": "oldvalue"}
    agent = Agent(desired_id=0)
    sim = Simulation(
        G, agents_list=[agent], agents_with_memory=True, prior_knowledge=info)
    agent.join_to_simulation(sim)

    assert not agent.write_on_memory_field("field", "newvalue")
    assert agent.read_memory_field("field") is None
    assert agent.read_prior_knowledge_field("field") == "oldvalue"


def test_read_prior_knowledge_field():
    G, _ = _trivial_graph()
    info = {"field": "value"}
    agent = Agent(desired_id=0)
    sim = Simulation(
        G, agents_list=[agent], agents_with_memory=True, prior_knowledge=info)
    agent.join_to_simulation(sim)

    assert agent.read_prior_knowledge_field("field") == "value"


def test_read_nonexisting_prior_knowledge_field():
    G, _ = _trivial_graph()

    agent = Agent()

    info = {"field": "value"}
    sim1 = Simulation(G, agents_list=[agent], prior_knowledge=info)
    agent.join_to_simulation(sim1)
    assert agent.read_prior_knowledge_field("nonexistingfield") is None

    sim2 = Simulation(G, agents_list=[agent])
    agent.join_to_simulation(sim2)
    assert agent.read_prior_knowledge_field("nonexistingfield") is None


def test_remove_from_memory_field():
    G, _ = _trivial_graph()

    agent = Agent(desired_id=0)
    sim = Simulation(G, agents_list=[agent], agents_with_memory=True)
    agent.join_to_simulation(sim)

    agent.write_on_memory_field("field_test", [1, 2])
    assert agent.remove_from_memory_field("field_test", 2)
    assert agent.read_memory_field("field_test") == [1]
    assert not agent.remove_from_memory_field("field_test", 3)


def test_remove_from_memory_field_without_memory():
    G, _ = _trivial_graph()

    agent = Agent(desired_id=0)
    sim = Simulation(G, agents_list=[agent])
    agent.join_to_simulation(sim)
    manager = sim.get_agents_manager()
    manager.set_agent_memory(agent, "field_test", [1, 2])

    assert not agent.remove_from_memory_field("field_test", 2)
    assert manager.get_agent_memory(agent, field="field_test") == [1, 2]


def test_remove_from_memory_nonexisting_field():
    G, _ = _trivial_graph()

    agent = Agent(desired_id=0)
    sim = Simulation(G, agents_list=[agent], agents_with_memory=True)
    agent.join_to_simulation(sim)

    assert not agent.remove_from_memory_field("field_test", 2)


def test_initial_position_contains_mate():
    G, u, v = _edge_graph()

    a1 = Agent(desired_id=1, desired_position=u)
    a2 = Agent(desired_id=2, desired_position=u)
    a3 = Agent(desired_id=3, desired_position=v)

    sim = Simulation(G, agents_list=[a1, a2, a3])
    a1.join_to_simulation(sim)
    a2.join_to_simulation(sim)
    a3.join_to_simulation(sim)

    assert a1.position_contains_mate()
    assert a2.position_contains_mate()
    assert not a3.position_contains_mate()


def test_read_vertex_field_nodes_with_memory():
    G, u = _trivial_graph()

    agent = Agent()
    sim = Simulation(G, agents_list=[agent], nodes_with_memory=True)
    agent.join_to_simulation(sim)

    manager = sim.get_vertices_manager()
    manager.set_vertex_memory(u, "field_test", "value_test")

    assert agent.read_position_memory_field("field_test") == "value_test"


def test_read_nonexisting_vertex_memory_field():
    G, u = _trivial_graph()

    agent = Agent()
    sim = Simulation(G, agents_list=[agent], nodes_with_memory=True)
    agent.join_to_simulation(sim)

    assert agent.read_position_memory_field("nonexisting_field") is None


def test_read_vertex_field_nodes_without_memory():
    G, u = _trivial_graph()

    agent = Agent()
    sim = Simulation(G, agents_list=[agent], nodes_with_memory=False)
    agent.join_to_simulation(sim)

    manager = sim.get_vertices_manager()
    manager.set_vertex_memory(u, "field_test", "value_test")

    assert agent.read_position_memory_field("field_test") is None


def test_write_on_vertex_field_nodes_with_memory():
    G, u = _trivial_graph()

    agent = Agent()
    sim = Simulation(G, agents_list=[agent], nodes_with_memory=True)
    agent.join_to_simulation(sim)

    assert agent.write_on_position_memory_field("field", "value")
    assert agent.read_position_memory_field("field") == "value"

    assert agent.write_on_position_memory_field("field", "newvalue")
    assert agent.read_position_memory_field("field") == "newvalue"

    assert agent.write_on_position_memory_field("field", "oldvalue", append=True)
    assert agent.read_position_memory_field("field") == ["newvalue", "oldvalue"]


def test_write_on_vertex_field_nodes_without_memory():
    G, u = _trivial_graph()

    agent = Agent()
    sim = Simulation(G, agents_list=[agent], nodes_with_memory=False)
    agent.join_to_simulation(sim)

    assert not agent.write_on_position_memory_field("value", "newfield")
    assert agent.read_position_memory_field("newfield") is None

def test_leave_pebble():
    G, _ = _trivial_graph()

    agent = Agent()
    sim = Simulation(G, agents_list=[agent], number_of_pebbles=1)
    agent.join_to_simulation(sim)

    assert agent.leave_pebble()
    assert not agent.leave_pebble()

def test_leave_pebble_agents_without_pebbles():
    G, _ = _trivial_graph()

    agent = Agent()
    sim = Simulation(G, agents_list=[agent], number_of_pebbles=0)
    agent.join_to_simulation(sim)

    assert not agent.leave_pebble()

def test_recover_pebble():
    G, u = _trivial_graph()

    a1 = Agent(desired_position=u)
    a2 = Agent(desired_position=u)
    sim = Simulation(G, agents_list=[a1,a2], number_of_pebbles=1)
    a1.join_to_simulation(sim)
    a2.join_to_simulation(sim)

    assert not a1.recover_pebble()
    assert not a2.recover_pebble()

    assert a1.leave_pebble()
    assert not a2.recover_pebble()
    assert a1.recover_pebble()

def test_recover_nonremovable_pebble():
    G, _ = _trivial_graph()

    a = Agent()
    sim = Simulation(G, agents_list=[a], number_of_pebbles=1, removable_pebbles=False)
    a.join_to_simulation(sim)

    assert a.leave_pebble()
    assert not a.recover_pebble()

def test_position_contains_pebble():
    G, u = _trivial_graph()

    a1 = Agent(desired_position=u)
    a2 = Agent(desired_position=u)
    sim = Simulation(G, agents_list=[a1,a2], number_of_pebbles=1)
    a1.join_to_simulation(sim)
    a2.join_to_simulation(sim)

    assert not a1.position_contains_pebble()
    assert not a2.position_contains_pebble()

    assert a1.leave_pebble()
    assert a1.position_contains_pebble()
    assert not a2.position_contains_pebble()

    assert a2.leave_pebble()
    assert a1.position_contains_pebble()
    assert a2.position_contains_pebble()

    assert a1.recover_pebble()
    assert not a1.position_contains_pebble()
    assert a2.position_contains_pebble()

def test_remaining_pebbles():
    G, _ = _trivial_graph()

    a = Agent()
    sim = Simulation(G, agents_list=[a], number_of_pebbles=2)
    a.join_to_simulation(sim)

    assert a.remaining_pebbles() == 2
    assert a.leave_pebble()
    assert a.remaining_pebbles() == 1
    assert a.leave_pebble()
    assert a.remaining_pebbles() == 0
    assert not a.leave_pebble()
    assert a.remaining_pebbles() == 0