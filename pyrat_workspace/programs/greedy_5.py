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

# Previously developed functions
# [TODO] Put imports of functions you have developed in previous lessons here

from djikstra import djikstra, find_route, locations_to_actions
from tutorial import get_neighbors, locations_to_action


#####################################################################################################################################################
############################################################### CONSTANTS & VARIABLES ###############################################################
#####################################################################################################################################################

# [TODO] It is good practice to keep all your constants and global variables in an easily identifiable section

#####################################################################################################################################################
##################################################################### FUNCTIONS #####################################################################
#####################################################################################################################################################

# [TODO] It is good practice to keep all developed functions in an easily identifiable section

def give_score ( graph:          Union[numpy.ndarray, Dict[int, Dict[int, int]]],
                 player_locations : Dict[str,int],
                 djikstra_cheeses,
                 targets:        List[int]
               ) ->              Tuple[Dict[int, float], Dict[int, Union[None, int]]]:
    """
        Function that associates a score to each target.
        In:
            * graph:          Graph containing the vertices.
            * current_vertex: Current location of the player in the maze.
            * targets:        Targeted vertices

        Out:
            * scores:        Scores given to the targets.
            * routing_table: Routing table obtained from the current vertex.
    """

    scores : Dict[str, Dict[int,float]] = {}

    for (name,current_vertex) in player_locations.items():

        scores[name] = {"routing_table":{},"scores":{}}

        distance_to_current_vertex, routing_table = djikstra(current_vertex, graph)

        scores[name]["routing_table"] = routing_table

        for target in targets:

            distance_to_target, routing_table = djikstra_cheeses[target]
            scores[name]["scores"][target] = 0

            for target2 in targets:
                if target != target2:
                    scores[name]["scores"][target] += 1/distance_to_target[target2]

            for (enemy,enemy_pos) in player_locations.items():
                if (name,current_vertex) != (enemy, enemy_pos) :
                    scores[name]["scores"][target] -= 1/distance_to_target[enemy_pos]

            scores[name]["scores"][target] = scores[name]["scores"][target] / distance_to_current_vertex[target]
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

    memory.nb_cheese_init = len(cheese)

    memory.djikstra_cheeses = {}
    for c in cheese:
        memory.djikstra_cheeses[c] = djikstra(c, maze)

    # Actions à réaliser
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
    current_vertex : int = player_locations[name]

    if memory.route == [] or memory.next_cheese not in cheese:
        scores = give_score(maze, player_locations, memory.djikstra_cheeses , cheese)

        routing_table = scores[name]["routing_table"]
        tmp = list(player_locations.keys())
        tmp.remove(name)

        if tmp != []:
            enemy_name = tmp[0]

            cheese_2 = cheese.copy()

            cheese.sort(key = lambda el : scores[name]["scores"][el],reverse=True)
            cheese_2.sort(key = lambda el : scores[enemy_name]["scores"][el],reverse=True)

            if cheese[0] == cheese_2[0] and memory.djikstra_cheeses[cheese[0]][0][player_locations[enemy_name]] < memory.djikstra_cheeses[cheese[0]][0][player_locations[name]]:
                try:
                    memory.next_cheese = cheese[1]
                except:
                    memory.next_cheese = cheese[0]
            else:
                memory.next_cheese = cheese[0]

        else:

            cheese.sort(key = lambda el : scores[name]["scores"][el],reverse=True)
            memory.next_cheese = cheese[0]


        memory.route = find_route(routing_table,current_vertex, memory.next_cheese)[1:]

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
    players = [{"name": "greedy 4", "preprocessing_function": preprocessing, "turn_function": turn, "location":"random"}]
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