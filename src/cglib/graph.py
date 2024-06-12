import taichi as ti 

from cglib.index import index2d_to_edge_index
from cglib.calc import linear_interpolation
from cglib.fields import count_cycles, fill_final_cycles



@ti.kernel 
def compute_binary_grid(grid: ti.template(), 
                        binary_grid: ti.template()): 
    '''
    Gives a 1 to the binary grid if the value of the field with the same coordinates 
    is positive, 0 if the value of the field is negative. 

    Parameters 
    -------

    grid: ti.template 

        the 2D field containing the scalar field values. 
        
    binary_grid : ti.template 

        2D field of the same size than grid, 
        containing the sine of the scalar field in each cell. 


    Returns
    -------

    None
    '''
    for x_index, y_index in grid:

        sign = ti.math.sign(grid[x_index, y_index])

        #1 if positive, 0 if negative. If the value is equal to zero, the binary grd take the value 1. 
        if sign == -1: 
            binary_grid[x_index, y_index] = 0
        elif sign == 0: 
            binary_grid[x_index, y_index] = 1 
        else:  
            binary_grid[x_index, y_index] = 1

@ti.kernel
def compute_adjacency_and_points(grid: ti.template(), 
                      binary_grid: ti.template(), 
                      points: ti.template(),
                      previous_edge: ti.template(),
                      next_edge: ti.template()): 
    '''
    Compute the adjacency (previous point and next point in the cycle) 
    for each point of the graph. The interior, i.e. where the field is negative, 
    should always be to the left of the edges. See marching square algorithm
    to understand the way the configuration of a cell is defined. 
    Compute also the coordinates of all the points in the graph.
    
    Parameters 
    -------

    grid: ti.template 

        the 2D field containing the scalar field values. 
        
    binary_grid : ti.template 

        2D field of the same size than grid, 
        containing the sine of the scalar field in each cell. 

    previous_edge: ti.template

        field containing the previous edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    next_edge : ti.template
    
        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 


    Returns
    -------

    None
    '''
    grid_shape = ti.math.ivec2(binary_grid.shape[0], 
                               binary_grid.shape[1])

    for x_index, y_index in binary_grid:

        #border case
        if x_index != grid_shape.x-1 and y_index != grid_shape.y-1: 

            current_cell = ti.math.ivec2(x_index, y_index)
            edge_indexes = index2d_to_edge_index(current_cell, 
                                                    grid_shape)
            current_cell_configuration =\
                        1*binary_grid[current_cell[0], current_cell[1]] +\
                        2*binary_grid[current_cell[0], current_cell[1]+1] +\
                        4*binary_grid[current_cell[0]+1, current_cell[1]+1] +\
                        8*binary_grid[current_cell[0]+1, current_cell[1]]
            
            #arête de droite
            if binary_grid[x_index, y_index+1] !=  binary_grid[x_index+1, y_index+1]: 
                right_edge_point = linear_interpolation(grid, 
                                                        ti.math.ivec2(x_index, y_index+1),
                                                        ti.math.ivec2(x_index+1 , y_index+1), 
                                                        0.)
                points[edge_indexes[1]] = right_edge_point

            #arête du bas 
            if binary_grid[x_index+1, y_index+1] !=  binary_grid[x_index+1, y_index]: 
                bottom_edge_point = linear_interpolation(grid, 
                                                        ti.math.ivec2(x_index+1, y_index+1),
                                                        ti.math.ivec2(x_index+1, y_index), 
                                                        0.)
                points[edge_indexes[2]] = bottom_edge_point

            #for each case of the marching square algorithm, we define the next and previous edge.
            #the interior of the cycle is always to the left of the edge.
            if current_cell_configuration == 0 or current_cell_configuration == 15: 

                next_edge[edge_indexes[1]] = -1
                previous_edge[edge_indexes[1]] = -1

                next_edge[edge_indexes[2]] = -1
                previous_edge[edge_indexes[2]] = -1

            elif current_cell_configuration == 1: 
                next_edge[edge_indexes[0]] = edge_indexes[3]
                previous_edge[edge_indexes[3]] = edge_indexes[0]

                        
            elif current_cell_configuration == 2: 
                next_edge[edge_indexes[1]] = edge_indexes[0]
                previous_edge[edge_indexes[0]] = edge_indexes[1]
                
                                    
            elif current_cell_configuration == 3: 
                next_edge[edge_indexes[1]] = edge_indexes[3]
                previous_edge[edge_indexes[3]] = edge_indexes[1]
            
                                    
            elif current_cell_configuration == 4: 
                next_edge[edge_indexes[2]] = edge_indexes[1]
                previous_edge[edge_indexes[1]] = edge_indexes[2]

            #two edges in the cell                     
            elif current_cell_configuration == 5: 


                average_value = (grid[current_cell.x, current_cell.y] +\
                                    grid[current_cell.x, current_cell.y + 1] +\
                                    grid[current_cell.x+ 1, current_cell.y+1] +\
                                    grid[current_cell.x+1, current_cell.y])/4
                
                if average_value > 0: 
                    next_edge[edge_indexes[0]] = edge_indexes[1]
                    previous_edge[edge_indexes[1]] = edge_indexes[0]
                    
                    next_edge[edge_indexes[2]] = edge_indexes[3]
                    previous_edge[edge_indexes[3]] = edge_indexes[2]
                else: 
                    next_edge[edge_indexes[0]] = edge_indexes[3]
                    previous_edge[edge_indexes[3]] = edge_indexes[0]
                    
                    next_edge[edge_indexes[2]] = edge_indexes[1]
                    previous_edge[edge_indexes[1]] = edge_indexes[2]
            
            elif current_cell_configuration == 6: 
                next_edge[edge_indexes[2]] = edge_indexes[0]
                previous_edge[edge_indexes[0]] = edge_indexes[2]

            elif current_cell_configuration == 7: 
                next_edge[edge_indexes[2]] = edge_indexes[3]
                previous_edge[edge_indexes[3]] = edge_indexes[2]

            elif current_cell_configuration == 8: 
                next_edge[edge_indexes[3]] = edge_indexes[2]
                previous_edge[edge_indexes[2]] = edge_indexes[3]

            elif current_cell_configuration == 9: 
                next_edge[edge_indexes[0]] = edge_indexes[2]
                previous_edge[edge_indexes[2]] = edge_indexes[0]

            #two edges in the cell 
            elif current_cell_configuration == 10: 

                average_value = (grid[current_cell.x, current_cell.y] +\
                                    grid[current_cell.x, current_cell.y + 1] +\
                                    grid[current_cell.x+ 1, current_cell.y+1] +\
                                    grid[current_cell.x+1, current_cell.y])/4
                
                if average_value < 0: 
                    next_edge[edge_indexes[1]] = edge_indexes[0]
                    previous_edge[edge_indexes[0]] = edge_indexes[1]
                    
                    next_edge[edge_indexes[3]] = edge_indexes[2]
                    previous_edge[edge_indexes[2]] = edge_indexes[3]
                else: 
                    next_edge[edge_indexes[3]] = edge_indexes[0]
                    previous_edge[edge_indexes[0]] = edge_indexes[3]
                    
                    next_edge[edge_indexes[1]] = edge_indexes[2]
                    previous_edge[edge_indexes[2]] = edge_indexes[1]       

            elif current_cell_configuration == 11: 
                next_edge[edge_indexes[1]] = edge_indexes[2]
                previous_edge[edge_indexes[2]] = edge_indexes[1]
                
            elif current_cell_configuration == 12: 
                next_edge[edge_indexes[3]] = edge_indexes[1]
                previous_edge[edge_indexes[1]] = edge_indexes[3]

            elif current_cell_configuration == 13: 
                next_edge[edge_indexes[0]] = edge_indexes[1]
                previous_edge[edge_indexes[1]] = edge_indexes[0]

            elif current_cell_configuration == 14: 
                next_edge[edge_indexes[3]] = edge_indexes[0]
                previous_edge[edge_indexes[0]] = edge_indexes[3]

@ti.kernel
def browse_grid(grid: ti.template(), 
                binary_grid: ti.template(), 
                next_edge: ti.template(), 
                cycle_index: ti.template(), 
                cycles: ti.template()): 
    '''
    Browse the entire grid to retrieve information about the graph's cycles. 

    Parameters 
    -------

    grid: ti.template 

        the 2D field containing the scalar field values. 
        
    binary_grid : ti.template 

        2D field of the same size than grid, 
        containing the sine of the scalar field in each cell. 

    next_edge: ti.template

        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    cycle_index: ti.template

        Fields containing the index of the cycle to which each edge belongs, 
        arranged according to 1D indexes of the grid edges. 

        
    Returns
    -------

    None
    '''

    grid_shape = ti.math.ivec2(grid.shape[0], grid.shape[1])
    cycle_number = 0 

    ti.loop_config(serialize= True)
    for x_index in range(binary_grid.shape[0]): 

        ti.loop_config(serialize= True)
        for y_index in range(binary_grid.shape[1]): 

            current_cell = ti.math.ivec2(x_index, y_index)
            current_cell_configuration =\
                            1*binary_grid[current_cell[0], current_cell[1]] +\
                            2*binary_grid[current_cell[0], current_cell[1]+1] +\
                            4*binary_grid[current_cell[0]+1, current_cell[1]+1] +\
                            8*binary_grid[current_cell[0]+1, current_cell[1]]
            

            if x_index != grid_shape.x-1 and\
                y_index != grid_shape.y-1 and \
                current_cell_configuration > 0 and\
                current_cell_configuration < 15 and\
                current_cell_configuration != 5 and\
                current_cell_configuration != 10 and\
                is_in_a_cycle(cycle_index, 
                              ti.math.ivec2(grid.shape[0], grid.shape[1]), 
                              current_cell) == False: 
                
                #we just found a new cycle, give a value to the first edge of the cycle.

                edge_indexes = index2d_to_edge_index(ti.math.ivec2(x_index, y_index),
                                                     ti.math.ivec2(binary_grid.shape[0],
                                                     binary_grid.shape[1]))
                
                first_edge = edge_indexes[2]
                if current_cell_configuration == 1\
                    or current_cell_configuration == 2\
                    or current_cell_configuration == 6\
                    or current_cell_configuration == 14\
                    or current_cell_configuration == 13\
                    or current_cell_configuration == 9:  
                
                    first_edge = edge_indexes[0]

                elif current_cell_configuration == 3\
                    or current_cell_configuration == 4\
                    or current_cell_configuration == 12\
                    or current_cell_configuration == 11: 

                    first_edge = edge_indexes[1]

                #flood the cycle to associate the correct cycle with each 
                #point and calculate the length of the cycle.
                flood(next_edge, 
                      cycle_index, 
                      cycles, 
                      first_edge, 
                      cycle_number)
                
                cycle_number += 1 

@ti.func
def is_in_a_cycle(cycle_index: ti.template(), 
                  grid_shape: ti.math.ivec2, 
                  cell:ti.math.ivec2)\
                      -> bool: 
    '''
    Check is a cell already has edges belonging to a cycle. 

    Parameters 
    -------

    cycle_index: ti.template

        Fields containing the index of the cycle to which each edge belongs, 
        arranged according to 1D indexes of the grid edges.     
        
    grid_shape: ti.math.ivec2

        2D shape of the scalar field grid

    cell: ti.math.ivec2

        cell whose edges we want to check in a cycle. 


    Returns
    -------

    bool

        True if the cell has one or more edges in a cycle 
        False if no edge in the cell is in a cycle 
    '''

    edge_indexes = index2d_to_edge_index(cell, 
                                         grid_shape)
    res = False

    ti.loop_config(serialize= True)
    for i in range(4): 

        if cycle_index[edge_indexes[i]] != -1: 
            res = True

    return res 

@ti.func
def flood(next_edge: ti.template(), 
          cycle_index: ti.template(), 
          cycles: ti.template(), 
          first_edge: int, 
          cycle_number: int): 
    '''
    Flood the cycle just discovered to associate the correct cycle
    with each point and calculate the length of the cycle. 

    Parameters 
    -------

    next_edge: ti.template

        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    cycle_index: ti.template

        Fields containing the index of the cycle to which each edge belongs, 
        arranged according to 1D indexes of the grid edges.     

    first_edge: int

        1D index of the edge from which the cycle was discovered  
        
    cycles: ti.template

        1D vector fields containing the length and starting edge of each cycle. 
        The starting edge is arbitrarily defined. 

    cycle_number: int

        An indication of the cycle we are in the process of flooding. 


    Returns
    -------

    None
    '''

    current_edge = next_edge[first_edge]
    cycle_index[first_edge] = cycle_number
    cycle_lenght = 1

    while current_edge != first_edge: 
        cycle_index[current_edge] = cycle_number
        
        key = next_edge[current_edge]
        current_edge = key
        cycle_lenght += 1   

    cycles[cycle_number] = ti.math.ivec2(first_edge, cycle_lenght)

def to_graph(grid: ti.template())\
      -> (ti.template(), ti.template(), ti.template(), ti.template(),ti.template()): 
    '''
    Extract the isocontours from the scalar field and arrange them in the form of a graph. 

    Parameters 
    -------

    grid: ti.template 

        the 2D field containing the scalar field values.


    Returns
    -------

    tuple (ti.template)
    
        fields describing the graph
            - points 
            - preivous_edge 
            - next_edge 
            - cycle_index 
            - cycles 
    '''
    # get the binary grid
    binary_grid = ti.field(dtype = int, shape = grid.shape) 
    compute_binary_grid(grid, 
                        binary_grid)


    # calculate the coordinates of all the points in parallel. 
    edge_fields_shape = binary_grid.shape[0]*(binary_grid.shape[1]+1)\
            + binary_grid.shape[1] *(binary_grid.shape[0]+1)\
            - 1    
    points = ti.Vector.field(n=2, 
                             dtype=float, 
                             shape=edge_fields_shape) 

    points.fill(ti.math.nan)

    # get the adjacency of the graph 
    previous_edge= ti.field(dtype = int, 
                            shape = edge_fields_shape)
    next_edge= ti.field(dtype = int, 
                        shape = edge_fields_shape)


    compute_adjacency_and_points(grid, 
                      binary_grid, 
                      points,
                      previous_edge, 
                      next_edge)
    
    # get the cycles of the graph
    cycle_index = ti.field(dtype = int, 
                           shape = edge_fields_shape) 
    cycle_index.fill(-1)
    cycles = ti.Vector.field(n = 2, 
                             dtype = int, 
                             shape = edge_fields_shape)
    browse_grid(grid, 
                binary_grid, 
                next_edge, 
                cycle_index,
                cycles)

    # reduce the size of the cycle field 
    cycles_count = count_cycles(cycles)
    final_cycles = ti.Vector.field(n = 2, 
                                   dtype = int, 
                                   shape = cycles_count) 
    fill_final_cycles(cycles, 
                      final_cycles)

    return points, previous_edge, next_edge, cycle_index, final_cycles