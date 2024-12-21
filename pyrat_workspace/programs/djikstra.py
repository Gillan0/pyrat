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
import heapq


# Previously developed functions
# [TODO] Put imports of functions you have developed in previous lessons here
from tutorial import get_neighbors, locations_to_action

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


def locations_to_actions ( locations:  List[int],
                           maze_width: int
                         ) ->          List[str]:
    """
        Function to transform a list of locations into a list of actions to reach vertex i+1 from vertex i.
        In:
            * locations:  List of locations to visit in order.
            * maze_width: Width of the maze in number of cells.
        Out:
            * actions: Sequence of actions to visit the list of locations.
    """

    # We iteratively transforms pairs of locations in the corresponding action
    actions : list = []
    for i in range(len(locations) - 1):
        action = locations_to_action(locations[i], locations[i + 1], maze_width)
        actions.append(action)
    return actions

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

    # [TODO] Write your preprocessing code here
    starting_point = player_locations[name]
    distance_to_vertices, routing_table = djikstra(starting_point,maze)
    route = find_route(routing_table,starting_point,cheese[0])
    actions_to_perform = locations_to_actions(route, maze_width)



    memory.actions = actions_to_perform

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

    # [TODO] Write your turn code here and do not forget to return a possible action
    assert(memory.actions != [])

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


# Distances and routing are from vertex 0
testing_distance_to_vertices_1 = {0:0, 1:1, 2:7, 3:5, 4:7, 5:8}
testing_distance_to_vertices_2 = {0:0, 1:5, 2:3, 3:1, 4:10, 5:6, 6:5}
testing_routing_table_1 = {0:None, 1:0, 2:0, 3:0, 4:3, 5:4}
testing_routing_table_2 = {0:None, 1:0, 2:3, 3:0, 4:0, 5:1, 6:3}

# Tests : djikstra
assert(djikstra(0,{0 : {0 : 0}}) == ({0:0},{0:None}))
assert(djikstra(0,testing_graph_1) == (testing_distance_to_vertices_1, testing_routing_table_1))
assert(djikstra(0,testing_graph_2) == (testing_distance_to_vertices_2, testing_routing_table_2))

# Tests : find_route
assert(find_route(testing_routing_table_1,0,5) == [0,3,4,5])
assert(find_route(testing_routing_table_2,0,2) == [0,3,2])


# Tests :  locations_to_actions
assert(locations_to_actions([],0) == [])
assert(locations_to_actions([0,1,2,3,4],5) == ["east","east","east","east"])
assert(locations_to_actions([4,3,2,1,0],5) == ["west","west","west","west"])
assert(locations_to_actions([0,1,2,3,4],1) == ["south","south","south","south"])
assert(locations_to_actions([4,3,2,1,0],1) == ["north","north","north","north"])
assert(locations_to_actions([4,5,2,1,0,3],3) == ["east","north","west","west","south"])

#################################################################################################################
###################################################### GO ! #####################################################
#################################################################################################################
if __name__ == "__main__":

    # Map the functions to the character
    players = [{"name": "DJIKSTRA", "preprocessing_function": preprocessing, "turn_function": turn}]
    # Customize the game elements
    config = {"maze_width": 15,
              "maze_height": 11,
              "mud_percentage": 30.00,
              "mud_range" : [3,12],
              "nb_cheese": 1,
              "trace_length": 1000}
    # Start the game
    game = PyRat(players, **config)
    stats = game.start()
    # Show statistics
    print(stats)
#################################################################################################################
#################################################################################################################