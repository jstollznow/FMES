import random
import numpy as np
import math
import itertools



################################################################################
# NODE #########################################################################
################################################################################
class Node():
    """A node class for A* Pathfinding"""

    def __init__(self, parent=None, position=None):
        self.parent = parent
        self.position = position

        self.g = 0
        self.h = 0
        self.f = 0

    def __eq__(self, other):
        return self.position == other.position



def AllCombinations(my_list, empty_list):
    """Fills an empty list with all possible combinations from my_list"""
    count = 0
    for i in range(1, len(my_list)+1):
        #Number of combinations for given i
        count += math.factorial(len(my_list))/(math.factorial(i)*math.factorial(len(my_list)-i))

    for i in range(1, len(my_list)+1):
        a = itertools.combinations(my_list, i)
        for subset in a:
            empty_list.append(list(subset))


################################################################################
# A* Algorithm #################################################################
################################################################################
def astar(tmaze, start, end):
    """Returns a list of tuples as a path from the given start to the given end in the given tmaze"""

    # Create start and end node
    start_node = Node(None, start)
    end_node = Node(None, end)

    # Initialize both open and closed list
    open_list = []
    closed_list = []

    # Add the start node
    open_list.append(start_node)

    # Loop until you find the end
    while len(open_list) > 0:

        # Get the current node
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):

            if item.f < current_node.f:
                current_node = item
                current_index = index

        # Pop current off open list, add to closed list
        open_list.pop(current_index)
        closed_list.append(current_node)

        # Found the goal
        if current_node == end_node:
            path = []
            current = current_node

            while current is not None:
                path.append(current.position)
                current = current.parent

            return path[::-1] # Return reversed path

        # Generate children
        children = []
        for new_position in [(0, -1), (0, 1), (-1, 0), (1, 0)]: # Adjacent squares

            # Get node position
            node_position = (current_node.position[0] + new_position[0], current_node.position[1] + new_position[1])

            # Make sure within range
            if node_position[0] > (len(tmaze) - 1) or node_position[0] < 0 or node_position[1] > (len(tmaze[len(tmaze)-1]) -1) or node_position[1] < 0:
                continue

            # Make sure walkable terrain
            if tmaze[node_position[0]][node_position[1]] != 0:
                continue

            if Node(current_node, node_position) in closed_list:
                continue

            # Create new node
            new_node = Node(current_node, node_position)

            # Append
            children.append(new_node)

        # Loop through children
        for child in children:

            # Child is on the closed list
            for closed_child in closed_list:
                if child == closed_child:
                    continue

            # Create the f, g, and h values
            child.g = current_node.g + 1
            child.h = ((child.position[0] - end_node.position[0]) ** 2) + ((child.position[1] - end_node.position[1]) ** 2)
            child.f = child.g + child.h

            # Child is already in the open list
            for open_node in open_list:
                if child == open_node and child.g > open_node.g:
                    continue

            # Add the child to the open list
            open_list.append(child)


################################################################################
# A* Algorithm for trafficBlock ################################################
################################################################################
def trafficBlock_astar(maze, start, end):
    """Returns an array that requires flying
    path_arr = [[start,critical_traffic_1),(critcial_traffic_1, critical_traffic_2),...,(critical_traffic_N,end]]
    """
    #start = (start[1],start[0])
    #end = (end[1], end[0])

    tmaze = flip_matrix(maze)

    #Remove traffic
    maze_simple = np.copy(maze)
    for i in range(0, len(maze)):
        for j in range(0, len(maze[0])):
            if maze_simple[j][i] == 1:
              maze_simple[j][i] = 0


    #Find quickest path if no traffic
    tmaze3=[]
    rez3 = [[maze_simple[j][i] for j in range(len(maze_simple))] for i in range(len(maze_simple[0]))]
    for row in rez3:
        tmaze3.append(row)
    path_nt = astar(tmaze3, start, end)  #path_nt is no traffic path

    one_count = 0  #variable indicates indice of traffic

    one_indices = [] #Stores the indicies of traffic
    one_coordinates = [] #Stores the coordinates of the traffic blocks
    j = 0;


    #Find where traffic is on this path
    for i in path_nt:
        if maze[i[1]][i[0]] == 1:
            one_indices.append(one_count)
            one_coordinates.append(i)
            j+=1
        one_count += 1
    count = 0


    comb_indices = []
    AllCombinations(one_coordinates, comb_indices) #all possible combinaions of traffic indices
    count = 0
    test_maze = np.copy(maze)

    #i is a combination of different traffic indices
    #j is the traffic indices constituting the combination
    #This loop iterates through all combinations, removing traffic at tests indices and seeing
    #if a path is possible
    for i in comb_indices :
        for j in i:
            test_maze[j[1]][j[0]] = 0

        tmaze2=[]
        rez2 = [[test_maze[j][i] for j in range(len(test_maze))] for i in range(len(test_maze[0]))]
        for row in rez2:
            tmaze2.append(row)

        path = astar(tmaze2, start, end)

        if path != None:
            traff_ind = i
            break

        test_maze = np.copy(maze)
        count += 1

    sur_ind = np.zeros(len(traff_ind)) #stores indice of removed traffic
    sur_count = 0
    path_count = 0

    #finds index of traffic in path list
    for k in traff_ind :
        for p in path :
            if k == p:
                sur_ind[sur_count] = path_count
                sur_count += 1
            path_count += 1
        path_count = 0


    #Fill path_arr with different components of rravel

    path_arr = [astar(tmaze, start, path[int(sur_ind[0]-1)][::-1])]

    if sur_ind.size > 2:

        for i in range(1, len(sur_ind)):
            path_arr.append(astar(tmaze), path[sur_ind[i-1]+1][::-1], path[sur_ind[i]-1][::-1])

    path_arr.append(astar(tmaze, path[int(sur_ind[-1]+1)][::-1], end))

    print(path_arr)



################################################################################
# Some Other Functions #########################################################
################################################################################
# Flips the matrix in the crossaxis to get the visuals the match x and y
def flip_matrix(maze):
    tmaze = []
    rez = [[maze[j][i] for j in range(len(maze))] for i in range(len(maze[0]))]
    for row in rez:
        tmaze.append(row)
    return tmaze



# multiple paths ###############################################################
def get_free_coordinates(tmaze):
    # Generates a coordinate list based on the size of the city map matrix
    free_coord = [] # coordinate List
    for x in range(len(tmaze)-1): # iterates through number of columns
        for y in range(len(tmaze[0])-1): # iterates through number of rows
            if tmaze[x][y] == 0: # if There is no traffic in this coordinate "0" then append coordinate
                free_coord.append((x,y)) # Coordinate list that does not have traffic
            elif tmaze[x][y] == 1: # else if there is traffic in this coordinate "1" do nothing
                continue
            elif tmaze[x][y] == 2: # else if there is house in this coordinate "2" do nothing
                continue
    return free_coord



# Generates start and destination positions ####################################
def random_start_dest(tmaze, NUM_OF_WHEELS):
    # Generates a coordinate list based on the size of the city map matrix
    free_coord = get_free_coordinates(tmaze)
    # Select random numbers from 'free_coord' and places them in strt_list and dest_list
    strt_list = [] # Start List
    dest_list = [] # Destination List
    for i in range(NUM_OF_WHEELS):
        strt_list.append(random.choice(free_coord))
        dest_list.append(random.choice(free_coord))
    #print('start list:', strt_list)
    #print('destination list:', dest_list)
    return strt_list, dest_list



# Creates multiple paths #######################################################
def multiple_astar_paths(tmaze, NUM_OF_WHEELS, strt_list, dest_list):
    # Created a list of paths using A* algorithm
    path_list = [] # Path List
    for i in range(NUM_OF_WHEELS):
        path_list.append(astar(tmaze, strt_list[i], dest_list[i]))
    #print('Path list:', path_list)
    return path_list

################################################################################
# END ##########################################################################
################################################################################
