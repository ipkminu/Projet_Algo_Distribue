from mas.visualization import GUI
from mas.graph.graph_generator import *
from mas.agent.Simulation import Simulation
from mas.agent.agent_algorithms import *
from mas.agent.Agent import Agent

if __name__ == "__main__":

    order = 10
    #G = random_graph(order, link_probability=0.2, connected=True)
    G = line(2)

    sim = Simulation(G, agents_number=3, algorithm=marche_alea)

    GUI.start(sim)
