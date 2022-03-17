import random
import math

def nothing(agent):
    return

def marche_alea(agent):
   print("Agent n°",agent.get_id())
   print("\tStatus:",agent.status())
   ports=agent.available_ports()
   agent.move_along(random.choice(ports))
   print("\t",ports) 
   print("\t",agent.get_sim_step()) 

def marche_alea2(agent):
   print("Agent n°",agent.get_id())
   print("\tStatus:",agent.status())
   ports=agent.available_ports()
   print("Noeud",agent.get_position_id())
   agent.move_along(random.choice(ports))
   print("\t",ports) 

def RV_synchrone_Arbre(agent):
    agent.move_along(agent.available_ports()[0])
    agent.wait()

    j=math.trunc(math.log2(agent.get_id()))[agent.get_sim_step()]
    if j == 0:
        agent.move_along(agent.available_ports()[0])
        print(agent.get_position_id())
        agent.move_along(agent.available_ports()[0])
        print(agent.get_position_id())
    else:  
        agent.wait()