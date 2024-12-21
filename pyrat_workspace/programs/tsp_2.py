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
import numpy as np
# External imports
# [TODO] Put all your standard imports (numpy, random, os, heapq...) here

# Previously developed functions
# [TODO] Put imports of functions you have developed in previous lessons here
from tutorial import get_neighbors, locations_to_action
from djikstra import djikstra, find_route, locations_to_actions

#####################################################################################################################################################
############################################################### CONSTANTS & VARIABLES ###############################################################
#####################################################################################################################################################

# [TODO] It is good practice to keep all your constants and global variables in an easily identifiable section

# best_route et best_length seront utilisés pour les fonction tsp
best_route = []
best_length = np.inf

#####################################################################################################################################################
##################################################################### FUNCTIONS #####################################################################
#####################################################################################################################################################

# [TODO] It is good practice to keep all developed functions in an easily identifiable section

def graph_to_metagraph ( graph:    Union[numpy.ndarray, Dict[int, Dict[int, int]]],
                         vertices: List[int],
                       ) ->        Tuple[numpy.ndarray, Dict[int, Dict[int, Union[None, int]]]]:
    """
        Function to build a complete graph out of locations of interest in a given graph.
        In:
            * graph:    Graph containing the vertices of interest.
            * vertices: Vertices to use in the complete graph.
        Out:
            * complete_graph: Complete graph of the vertices of interest.
            * routing_tables: Dictionary of routing tables obtained by traversals used to build the complete graph.
    """
    complete_graph : Dict[int, Dict[int,int]] = {}
    final_routing_table : Dict[int, Dict[int,Union[None,int]]] = {}

    for v1 in vertices:
        distances_to_explored_vertices, routing_table = djikstra(v1, graph)
        # A chaque élément de vertices, on applique djikstra pour avoir sa table de routage
        # et la distance à chaque éléments du labyrinthe


        complete_graph[v1] = {} # On déclare que l'élément sera un dictionnaire

        final_routing_table[v1] = routing_table # On associe à v1 la table de routage de djikstra

        # On crée un edge entre v1 et tous les éléments de vertices dont le poids est celui obtenu par djikstra
        for v2 in vertices:
            if v1 != v2:
                complete_graph[v1][v2] = distances_to_explored_vertices[v2]

    return complete_graph, final_routing_table

assert(graph_to_metagraph({},[]) == ({},{}))


def tsp_2 ( complete_graph: Dict[int, Dict[int, int]],
          source:         int
        ) ->              Tuple[List[int], int]:
    """
        Function to solve the TSP using an exhaustive search.
        In:
            * complete_graph: Complete graph of the vertices of interest.
            * source:         Vertex used to start the search.
        Out:
            * best_route:  Best route found in the search.
            * best_length: Length of the best route found.
    """

    # Appel des variables globales best_route et best_length
    global best_route, best_length

    # Réinit de best_route et best_length puisque en tant que variable globale,
    # si on appelle une fonction tsp après une autre, on aura pas les mêmes conditions initiales
    best_route = [source]
    best_length = np.inf

    # Nb de sommets du graphe
    nb_vertices : int = len(list(complete_graph.keys()))

    def _tsp_2(current_vertex, current_length,current_route):
        # Appel des variables globales best_route et best_length
        global best_route, best_length
        """
        DESCRIPTION
        In :
        Out:
        """
        # Condition d'arrêt : On continue seulement si la longueur actuelle est plus petite que la longueur max
        if current_length < best_length:
            # Condition d'arrêt : Si on a créer une route de longueur max
            if len(current_route) == nb_vertices :
                best_length = current_length
                best_route = current_route

            else:
                # Parcours de tous les voisins non explorés
                for neighbour in complete_graph[current_vertex].keys():
                    if neighbour not in current_route:
                        _tsp_2(neighbour, current_length + complete_graph[current_vertex][neighbour], current_route + [neighbour])

    _tsp_2(source,0,[source])
    return best_route, best_length




def expand_route ( route_in_complete_graph: List[int],
                   routing_tables:          Dict[int, Dict[int, Union[None, int]]],
                   cell_names:              List[int]
                 ) ->                       List[int]:
    """
        Returns the route in the original graph corresponding to a route in the complete graph.
        In:
            * route_in_complete_graph: List of locations in the complete graph.
            * routing_tables:          Routing tables obtained when building the complete graph.
            * cell_names:              List of cells in the graph that were used to build the complete graph.
        Out:
            * route: Route in the original graph corresponding to the given one.
    """
    route : List[int] = [route_in_complete_graph[0]]

    # On trouve le chemin entre les éléments i et i+1 de route_in_complete_graph puis on concatène ces chemins
    for i in range(len(route_in_complete_graph)-1):
        source = route_in_complete_graph[i]
        target = route_in_complete_graph[i+1]
        route = route + find_route(routing_tables[source] ,source , target)[1:]
    return route

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

    # Sommets d'intérêts : position intiale et celles des fromages
    interesting_vertices : List[int] = [starting_point] + cheese

    # Création du métagraph et de toutes les routing table
    meta_graph, routing_tables = graph_to_metagraph(maze, interesting_vertices)

    # Obtention d'un chemin dans le metagraph
    complete_route = tsp_1(meta_graph, starting_point)[0]

    # Conversion du chemin du metagraph en chemin dans le labyrinthe
    final_route = expand_route(complete_route, routing_tables, interesting_vertices)

    # Actions à réaliser
    memory.actions = locations_to_actions(final_route, maze_width)


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

    if memory.actions == []:
        return "nothing"
    else:
        action = memory.actions[0]
        memory.actions = memory.actions[1:]
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


#################################################################################################################
##################################################### TESTS #####################################################
#################################################################################################################

# TESTING VARIABLES
meta_graph_test_tsp_1 = {0 : {1 : 1, 2 : 3, 3 : 5, 4 : 10},
                   1 : {0 : 1, 2 : 6, 3 : 8, 4 : 1},
                   2 : {0 : 3, 1 : 6, 3 : 17, 4 : 2},
                   3 : {0 : 10, 1 : 8, 2 : 17, 4 : 16},
                   4 : {0 : 10, 1 : 1, 2 : 2, 3 : 16}}

testing_graph_1 : Dict[int,Dict[int,int]] = {0 : {1 : 1, 2 : 7, 3 : 5},
                                            1 : {0 : 1},
                                            2 : {0 : 7, 4 : 3},
                                            3 : {0 : 5, 4 : 2},
                                            4 : {2 : 3, 3 : 2, 5 : 1},
                                            5 : {4 : 1}}

testing_graph_2 : Dict[int,Dict[int,int]] = {0 : {1 : 5, 2 : 7, 3 : 1, 4 : 10},
                                            1 : {0 : 5, 4 : 20, 5 : 1},
                                            2 : {0 : 7, 3 : 2},
                                            3 : {0 : 1, 2 : 2, 6 : 4},
                                            4 : {0 : 10, 1 : 20},
                                            5 : {1 : 1},
                                            6 : {3 : 4}}

assert(graph_to_metagraph({},[]) == ({},{}))
assert(graph_to_metagraph(testing_graph_1,[0,1,5]) == ({0 : {1 : 1, 5 : 8},
                                                        1 : {0 : 1, 5 : 9},
                                                        5 : {0 : 8, 1 : 9},},
                                                        {0 : {0:None, 1:0, 2:0, 3:0, 4:3, 5:4},
                                                        1 :  {0:1, 1:None, 2:0, 3:0, 4:3, 5:4},
                                                        5 : {0:3, 1:0, 2:4, 3:4, 4:5, 5:None}}))
assert(graph_to_metagraph(testing_graph_2,[5,6]) == ({5 : {6 : 11},
                                                      6 : {5 : 11}},
                                                      {5 : {5 : None, 1 : 5, 0 : 1, 4 : 0, 3 : 0, 2 : 3, 6 : 3},
                                                       6 : {6 : None, 3 : 6, 0 : 3, 2 : 3, 4 : 0, 1 : 0, 5 : 1}}))

assert(tsp_2(meta_graph_test_tsp_1, 0) == ([0,2,4,1,3],14))
assert(tsp_2({0:{}}, 0) == ([0],0))


assert(expand_route([0,1,5],{0 : {0:None, 1:0, 2:0, 3:0, 4:3, 5:4},
                                1 :  {0:1, 1:None, 2:0, 3:0, 4:3, 5:4},
                                5 : {0:3, 1:0, 2:4, 3:4, 4:5, 5:None}}, []) == [0,1,0,3,4,5])

assert(expand_route([5,6],{5 : {5 : None, 1 : 5, 0 : 1, 4 : 0, 3 : 0, 2 : 3, 6 : 3},
                                6 : {6 : None, 3 : 6, 0 : 3, 2 : 3, 4 : 0, 1 : 0, 5 : 1}},[]) == [5,1,0,3,6])
#####################################################################################################################################################
######################################################################## GO! ########################################################################
#####################################################################################################################################################

if __name__ == "__main__":
    # Map the functions to the character
    players = [{"name": "TSP 2", "preprocessing_function": preprocessing, "turn_function": turn}]
    # Customize the game elements
    config = {"maze_width": 15,
              "maze_height": 11,
              "mud_percentage": 40.0,
              "nb_cheese": 8,
              "trace_length": 1000}
    # Start the game
    game = PyRat(players, **config)
    stats = game.start()
    # Show statistics
    print(stats)

#####################################################################################################################################################
#####################################################################################################################################################