import random
import math

from numpy import size

def nothing(agent):
    return

def marche_alea(agent):
    #print("Agent n°",agent.get_id())
    #print("\tStatus:",agent.status())
    ports=agent.available_ports()
    #Arrêter l'agent une fois tous les ports visités
    #lire la liste des noeuds visités
    #if (agent.get_position_id() not in agent.read_memory_field("visited")):
    if size(agent.read_memory_field("visited"))<10:
        agent.write_on_memory_field("visited", agent.get_position_id(),True)
        agent.move_along(random.choice(ports))
        #print("\t",ports) 
        #print("\t",agent.get_sim_step()) 
        print("Memoire",agent.read_memory_field("visited"))
    else:
        print ("Tous les noeuds ont été visités après ",agent.get_moves_nb(),"mouvements")
   

def marche_alea2(agent):
    print("Agent n°",agent.get_id())
    print("\tStatus:",agent.status())
    ports=agent.available_ports()
    print("Noeud",agent.get_position_id())
    agent.move_along(random.choice(ports))
    print("\t",ports) 


def mdm(agent):
    precedent=agent.get_port_back()
    ports=agent.available_ports()
    if agent.read_memory_field("visited")==None:
        agent.write_on_memory_field("visited", [],True)
    if precedent:
        ports.remove(precedent)
        if size(ports)==0:
            agent.write_on_memory_field("visited", precedent,True)
            agent.move_along(precedent)
            agent.leave_pebble()
        else:
            choice=random.choice(ports)
            agent.write_on_memory_field("visited", choice,True)
            agent.move_along(choice)
            agent.leave_pebble()
    else:
        choice=random.choice(ports)
        agent.write_on_memory_field("visited", choice,True)
        agent.move_along(choice)
        agent.leave_pebble()
    
    print(agent.read_memory_field("visited"))




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