#####################################################################################################################################################
######################################################################## INFO #######################################################################
#####################################################################################################################################################

"""
    This program is an empty PyRat program file.
    It serves as a template for your own programs.
    Some [TODO] comments below are here to help you keep your code organized.
    Note that all PyRat programs must have a "turn" function.
    Functions "preprocessing" and "postprocessing" are optional.
    Please check the documentation of these functions for more info on their purpose.
    Also, the PyRat website gives more detailed explanation on how a PyRat game works.
    https://formations.imt-atlantique.fr/pyrat
"""

#####################################################################################################################################################
###################################################################### IMPORTS ######################################################################
#####################################################################################################################################################

# Import PyRat
from pyrat import *

# External imports
# [TODO] Put all your standard imports (numpy, random, os, heapq...) here
import numpy as np
import heapq


# Previously developed functions
# [TODO] Put imports of functions you have developed in previous lessons here
from tutorial import locations_to_action


#####################################################################################################################################################
############################################################### CONSTANTS & VARIABLES ###############################################################
#####################################################################################################################################################

# [TODO] It is good practice to keep all your constants and global variables in an easily identifiable section

#####################################################################################################################################################
##################################################################### FUNCTIONS #####################################################################
#####################################################################################################################################################

# [TODO] It is good practice to keep all developed functions in an easily identifiable section

def traversal ( source:             int,
                graph:              Union[numpy.ndarray, Dict[int, Dict[int, int]]],
                create_structure:   Callable[[], Any],
                push_to_structure:  Callable[[Any, Tuple[int, int, int]], None],
                pop_from_structure: Callable[[Any], Tuple[int, int, int]]
              ) ->                  Tuple[Dict[int, int], Dict[int, Union[None, int]]]:
    """
        Traversal function that explores a graph from a given vertex.
        This function is generic and can be used for most graph traversal.
        To adapt it to a specific traversal, you need to provide the adapted functions to create, push and pop elements from the structure.
        In:
            * source:             Vertex from which to start the traversal.
            * graph:              Graph on which to perform the traversal.
            * create_structure:   Function that creates an empty structure to use in the traversal.
            * push_to_structure:  Function that adds an element of type B to the structure of type A.
            * pop_from_structure: Function that returns and removes an element of type B from the structure of type A.
        Out:
            * distances_to_explored_vertices: Dictionary where keys are explored vertices and associated values are the lengths of the paths to reach them.
            * routing_table:                  Routing table to allow reconstructing the paths obtained by the traversal.
    """

    # Initialisation : used stack and empty stack
    stack = create_structure()
    empty_stack = create_structure()

    visited : list = [] # Array of integers representing the visited vertices
    routing_table : Dict[int,Union[None,int]] = {}
    distance_to_explored_vertices  : Dict[int,int] = {}


    push_to_structure(stack,(0,(source,None)))

    while stack != empty_stack:

        distance, (current_vertex, parent)= pop_from_structure(stack)
        if current_vertex not in visited :

            # Updates visited, routing_table, distance_to_explored_vertices
            visited.append(current_vertex)
            routing_table[current_vertex] = parent
            distance_to_explored_vertices[current_vertex] = distance

            # Adds all unvisited neighbours to the stack
            for (neighbour,distance_to_neighbour) in graph[current_vertex].items():
                if neighbour not in visited:
                    push_to_structure(stack,(distance + distance_to_neighbour,(neighbour, current_vertex)))

    return distance_to_explored_vertices, routing_table

def djikstra ( source: int,
          graph:  Union[numpy.ndarray, Dict[int, Dict[int, int]]]
        ) ->      Tuple[Dict[int, int], Dict[int, Union[None, int]]]:
    """
        A DJIKSTRA is a particular traversal where vertices are explored in the order where they are added to the structure.
        In:
            * source: Vertex from which to start the traversal.
            * graph:  Graph on which to perform the traversal.
        Out:
            * distances_to_explored_vertices: Dictionary where keys are explored vertices and associated values are the lengths of the paths to reach them.
            * routing_table:                  Routing table to allow reconstructing the paths obtained by the traversal.
    """

    # Function to create an empty FIFO, encoded as a list
    def _create_structure ():
        return []
    # Function to add an element to the FIFO (elements enter by the end)
    def _push_to_structure (structure, element):
        heapq.heappush(structure, element)
    # Function to extract an element from the FIFO (elements exit by the beginning)
    def _pop_from_structure (structure):
        return heapq.heappop(structure)

    # Perform the traversal
    distances_to_explored_vertices, routing_table = traversal(source, graph, _create_structure, _push_to_structure, _pop_from_structure)
    return distances_to_explored_vertices, routing_table


def find_route ( routing_table: Dict[int, Union[None, int]],
                 source:        int,
                 target:        int
               ) ->             List[int]:
    """
        Function to return a sequence of locations using a provided routing table.
        In:
            * routing_table: Routing table as obtained by the traversal.
            * source:        Vertex from which we start the route (should be the one matching the routing table).
            * target:        Target to reach using the routing table.
        Out:
            * route: Sequence of locations to reach the target from the source, as perfomed in the traversal.
    """
    assert(routing_table[source] == None)
    assert(source in list(routing_table.keys()))
    assert(target in list(routing_table.keys()))

    reversed_route : List[int] = [target]
    parent : int = routing_table[target]

    # While there exist a parent for our vertex, we go back and add him to our path
    while parent != None:
        try:
            reversed_route.append(parent)
            parent = routing_table[parent]
        except:
            raise Exception("ROUTING TABLE INVALID : CANNOT GO BACK TO SOURCE")

    # We return the opposite path
    return [reversed_route[len(reversed_route)-i-1] for i in range(len(reversed_route))]


def locations_to_action ( source:     int,
                          target:     int,
                          maze_width: int
                        ) ->          str:

    """
        Function to transform two locations into an action to reach target from the source.
        In:
            * source:     Vertex on which the player is.
            * target:     Vertex where the character wants to go.
            * maze_width: Width of the maze in number of cells.
        Out:
            * action: Name of the action to go from the source to the target.
    """

    # Convert indices in row, col pairs
    source_row = source // maze_width
    source_col = source % maze_width
    target_row = target // maze_width
    target_col = target % maze_width

    # Check difference to get direction
    difference = (target_row - source_row, target_col - source_col)
    if difference == (0, 0):
        action = "nothing"
    elif difference == (0, -1):
        action = "west"
    elif difference == (0, 1):
        action = "east"
    elif difference == (1, 0):
        action = "south"
    elif difference == (-1, 0):
        action = "north"
    else:
        raise Exception("Impossible move from", source, "to", target)
    return action

def cheese_density( current_cheese : int,
                    cheese : List[int],
                    distance_to_current_cheese : Dict[int,float]
                    ) -> int :
    """
        Function which computes the density of cheese associated with the current cheese
        In :
            * current_cheese :              Cheese whose density is wanted
            * cheese :                      List of cheeses
            * distance_to_current_cheese :  Dictionnary which associates to a vertex its distance to the current_cheese
        Out :
            * final :   Cheese density associated with the current cheese
    """
    final : float = 0
    # On fait la somme des inverses des distances entre current_cheese et les autres fromages
    for c in cheese:
        if c != current_cheese:
            final += 1/distance_to_current_cheese[c]
    return final

def update_cheese_density(  cheese : List[int],
                            cheese_density : Dict[int,float],
                            removed_cheese : List[int],
                            djikstra_cheeses : Dict[int,float]
                            ) -> None :
    """
        Function which updates the density of cheese when a cheese is removed froom the maze
        In :
            * removed_cheese :              Cheese who will be removed
            * cheese :                      List of cheeses
            * djikstra_cheeses :            Dictionnary which associates to a cheese its data obtained from djikstra
            * cheese_density :              Dictionnary which associates a cheese to its density
        Out :
            None
    """
    # On retire la contribution du fromage retiré aux densités de fromages
    for c in cheese:
        if c != removed_cheese:
            cheese_density[c] -= 1/djikstra_cheeses[c][0][removed_cheese]



def give_score ( graph:          Union[numpy.ndarray, Dict[int, Dict[int, int]]],
                 player_locations : Dict[str,int],
                 djikstra_cheeses,
                 targets:        List[int],
                 cheese_density : Dict[int,float]
               ) ->              Tuple[Dict[int, float], Dict[int, Union[None, int]]]:
    """
        Function that associates to each player a routing table and a score dictionnary.
        This score dictionnary associates to each target, a score.
        In:
            * graph:            Graph containing the vertices.
            * player_locations  Dictionnary which associates to the name of a player, its location
            * djikstra_cheese   Dictionnary which associates to a cheese, the data obtained from djikstra
                                (routing table and distance to all vertices)
            * targets           Targeted vertices (cheeses)
            * cheese_density    Dictionnary which associates to a cheese, its density
        Out:
            * scores:           Dictionnary which associates to each player, a routing table and a score dictionnary.
                                This score dictionnary associates to each target, a score.
    """

    scores : Dict[str, Union[Tuple[Dict[int, int], Dict[int, Union[None, int]]] , Dict[int,float]]] = {}

    # On parcourt tous les joueurs
    for (name,current_vertex) in player_locations.items():

        # Initialisation
        scores[name] = {}

        # On parcourt tous les fromages pour calculer leur score
        for target in targets:

            # On récupère les données de djikstra associées à chaque fromage
            distance_to_target, routing_table = djikstra_cheeses[target]

            # Initialisation
            scores[name][target] = 0

            # On parcourt tous les autres joueurs
            for (enemy,enemy_pos) in player_locations.items():
                if (name,current_vertex) != (enemy, enemy_pos) :

                    # On prend en compte la présence d'un ennemi dans le score
                    scores[name][target] -= 1/distance_to_target[enemy_pos]

            # On prend en compte la distance du joueur au fromage dans le score
            scores[name][target] = (scores[name][target] + cheese_density[target]) / distance_to_target[current_vertex]

    return scores


#####################################################################################################################################################
##################################################### EXECUTED ONCE AT THE BEGINNING OF THE GAME ####################################################
#####################################################################################################################################################

def preprocessing ( maze:             Union[numpy.ndarray, Dict[int, Dict[int, int]]],
                    maze_width:       int,
                    maze_height:      int,
                    name:             str,
                    teams:            Dict[str, List[str]],
                    player_locations: Dict[str, int],
                    cheese:           List[int],
                    possible_actions: List[str],
                    memory:           threading.local
                  ) ->                None:

    """
        This function is called once at the beginning of the game.
        It is typically given more time than the turn function, to perform complex computations.
        Store the results of these computations in the provided memory to reuse them later during turns.
        To do so, you can crete entries in the memory dictionary as memory.my_key = my_value.
        In:
            * maze:             Map of the maze, as data type described by PyRat's "maze_representation" option.
            * maze_width:       Width of the maze in number of cells.
            * maze_height:      Height of the maze in number of cells.
            * name:             Name of the player controlled by this function.
            * teams:            Recap of the teams of players.
            * player_locations: Locations for all players in the game.
            * cheese:           List of available pieces of cheese in the maze.
            * possible_actions: List of possible actions.
            * memory:           Local memory to share information between preprocessing, turn and postprocessing.
        Out:
            * None.
    """

    # Emplacement de départ
    starting_point : int = player_locations[name]

    # Dictionnaire associant à tout fromage les donnéees obtenues pas djikstra
    memory.djikstra_cheeses = {}

    # Dictionnaire associant à tout fromage sa densité de fromage
    memory.cheese_density : Dict[int, float] = {}

    # Liste contenant les fromages du tour précédant
    # Cela sert à déterminer quel fromage a été mangé par un des deux fantomes
    memory.backup_cheese : List[int] = cheese

    # Liste contnant les noms des adversaires
    memory.enemies_name = list(player_locations.keys())
    memory.enemies_name.remove(name)

    # On se restreint au cas où il y a 2 joueurs et on garde uniquement le nom de l'adversaire
    if memory.enemies_name != []:
        memory.enemy_name = memory.enemies_name[0]

    # On remplit les dictionnaires memory.djikstra_cheeses et memory.cheese_density
    for c in cheese:
        distance_to_current_cheese, routing_table = djikstra(c, maze)
        memory.djikstra_cheeses[c] = (distance_to_current_cheese, routing_table)
        memory.cheese_density[c] = cheese_density(c, cheese, distance_to_current_cheese)

    # Route pour arriver au fromage que l'on vise
    memory.route = []


#####################################################################################################################################################
######################################################### EXECUTED AT EACH TURN OF THE GAME #########################################################
#####################################################################################################################################################

def turn ( maze:             Union[numpy.ndarray, Dict[int, Dict[int, int]]],
           maze_width:       int,
           maze_height:      int,
           name:             str,
           teams:            Dict[str, List[str]],
           player_locations: Dict[str, int],
           player_scores:    Dict[str, float],
           player_muds:      Dict[str, Dict[str, Union[None, int]]],
           cheese:           List[int],
           possible_actions: List[str],
           memory:           threading.local
         ) ->                str:

    """
        This function is called at every turn of the game and should return an action within the set of possible actions.
        You can access the memory you stored during the preprocessing function by doing memory.my_key.
        You can also update the existing memory with new information, or create new entries as memory.my_key = my_value.
        In:
            * maze:             Map of the maze, as data type described by PyRat's "maze_representation" option.
            * maze_width:       Width of the maze in number of cells.
            * maze_height:      Height of the maze in number of cells.
            * name:             Name of the player controlled by this function.
            * teams:            Recap of the teams of players.
            * player_locations: Locations for all players in the game.
            * player_scores:    Scores for all players in the game.
            * player_muds:      Indicates which player is currently crossing mud.
            * cheese:           List of available pieces of cheese in the maze.
            * possible_actions: List of possible actions.
            * memory:           Local memory to share information between preprocessing, turn and postprocessing.
        Out:
            * action: One of the possible actions, as given in possible_actions.
    """
    # Position actuel du joueur
    current_vertex : int = player_locations[name]

    # Si un fromage a été mangé
    if len(cheese)  != len(memory.backup_cheese) :

        # Détermination du fromage mangé dans le cas d'un match à au plus 2 joueurs
        if player_locations[name] in memory.backup_cheese:
            removed_cheese = player_locations[name]
        else:
            removed_cheese = player_locations[memory.enemy_name]

        # On met à jour la densité de fromage et la liste des précédents fromages
        update_cheese_density(cheese, memory.cheese_density, removed_cheese, memory.djikstra_cheeses)
        memory.backup_cheese = cheese

    # Si notre fromage visé a été mangé (par nous ou l'adversaire)
    if memory.route == [] or memory.next_cheese not in cheese:

        # Calcul des scores associés à chaque fromage
        scores = give_score(maze, player_locations, memory.djikstra_cheeses , cheese, memory.cheese_density)

        # 1er cas : Match à 2 joueurs
        if len(player_locations.keys()) == 2:

            # On tente de prédire où ira l'adversaire en supposant que notre
            # fonction score est la meilleure et que l'adversaire  l'utilise
            # pour déterminer le fromage qu'il vise

            # On copie la liste des fromages, celle ci est associée à l'adversaire
            cheese_2 : List[int] = cheese.copy()

            # On trie les deux listes par score décroissant
            cheese.sort(key = lambda el : scores[name][el],reverse=True)
            cheese_2.sort(key = lambda el : scores[memory.enemy_name][el],reverse=True)

            i : int = 0
            distance_from_enemy_to_next_cheese : int = memory.djikstra_cheeses[cheese[0]][0][player_locations[memory.enemy_name]]

            # Tant qu'on vise le même fromage et que l'ennemi passe par un chemin plus court
            # que notre chemin le plus rapide, on passe au fromage suivant.
            while i + 1 < len(cheese) and cheese[i] == cheese_2[i] and distance_from_enemy_to_next_cheese < memory.djikstra_cheeses[cheese[i]][0][player_locations[name]] :
                i+=1
                distance_from_enemy_to_next_cheese += memory.djikstra_cheeses[cheese[i-1]][0][cheese[i]]

            # Prochain fromage visé est celui avec le plus grand score
            try:
                memory.next_cheese = cheese[i]
            except:
                memory.next_cheese = cheese[0]

        # 2e cas : 1 joueur dans le labyrinthe
        else:

            # Tri des fromages par score décroissant
            cheese.sort(key = lambda el : scores[name][el],reverse=True)

            # Prochain fromage visé est celui avec le plus grand score
            memory.next_cheese = cheese[0]

        # Calcul du chemin pour arriver au fromage visé
        routing_table = memory.djikstra_cheeses[memory.next_cheese][1]
        memory.route = list(reversed(find_route(routing_table, memory.next_cheese, current_vertex)))[1:]

    # Action à effectuer ce tour ci
    action = locations_to_action(current_vertex,memory.route.pop(0),maze_width)

    return action


#####################################################################################################################################################
######################################################## EXECUTED ONCE AT THE END OF THE GAME #######################################################
#####################################################################################################################################################

def postprocessing ( maze:             Union[numpy.ndarray, Dict[int, Dict[int, int]]],
                     maze_width:       int,
                     maze_height:      int,
                     name:             str,
                     teams:            Dict[str, List[str]],
                     player_locations: Dict[str, int],
                     player_scores:    Dict[str, float],
                     player_muds:      Dict[str, Dict[str, Union[None, int]]],
                     cheese:           List[int],
                     possible_actions: List[str],
                     memory:           threading.local,
                     stats:            Dict[str, Any],
                   ) ->                None:

    """
        This function is called once at the end of the game.
        It is not timed, and can be used to make some cleanup, analyses of the completed game, model training, etc.
        In:
            * maze:             Map of the maze, as data type described by PyRat's "maze_representation" option.
            * maze_width:       Width of the maze in number of cells.
            * maze_height:      Height of the maze in number of cells.
            * name:             Name of the player controlled by this function.
            * teams:            Recap of the teams of players.
            * player_locations: Locations for all players in the game.
            * player_scores:    Scores for all players in the game.
            * player_muds:      Indicates which player is currently crossing mud.
            * cheese:           List of available pieces of cheese in the maze.
            * possible_actions: List of possible actions.
            * memory:           Local memory to share information between preprocessing, turn and postprocessing.
        Out:
            * None.
    """

    # [TODO] Write your postprocessing code here
    pass

#####################################################################################################################################################
######################################################################## GO! ########################################################################
#####################################################################################################################################################


if __name__ == "__main__":
    # Map the functions to the character
    players = [{"name": "René Coty", "preprocessing_function": preprocessing, "turn_function": turn, "location":"random"}]
    # Customize the game elements
    config = {"maze_width": 15,
              "maze_height": 11,
              "mud_percentage": 40.0,
              "nb_cheese": 21,
              "trace_length": 1000}
    # Start the game
    game = PyRat(players, **config)
    stats = game.start()
    # Show statistics
    print(stats)


#####################################################################################################################################################
#####################################################################################################################################################