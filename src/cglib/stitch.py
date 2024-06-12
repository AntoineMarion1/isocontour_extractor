import taichi as ti 
import tqdm

from cglib.fields import reset_energies, find_minimum_in_field 
from cglib.calc import compute_all_energies, compute_neighbours_energies



@ti.func
def stitch_two_cycles(previous_edge: ti.template(), 
                      next_edge: ti.template(), 
                      cycle_index: ti.template(), 
                      cycles: ti.template(), 
                      minimal_energy_edges: ti.math.ivec2):
    
        
    '''
    Stitch two cycles together, by exchanging the adjacency of two edges.

    Parameters 
    -------

    previous_edge: ti.template

        field containing the previous edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 
    
    next_edge: ti.template

        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    cycle_index: ti.template

        Fields containing the index of the cycle to which each edge belongs, 
        arranged according to 1D indexes of the grid edges.  

    cycles: ti.template

        1D vector fields containing the length and starting edge of each cycle. 
        The starting edge is arbitrarily defined. 

    minimal_energy_edges: ti.math.ivec2

        vector of 1D index of the two edges whose adjacency must be changed. 
        

    Returns
    -------

    None
    '''

    cycle_1_index = cycle_index[minimal_energy_edges.x]
    cycle_2_index = cycle_index[minimal_energy_edges.y]

    #change next_edge and previous_edge
    edge_I = ti.math.ivec2(minimal_energy_edges.x, 
                           next_edge[minimal_energy_edges.x]) #(I1, I2)
    edge_J = ti.math.ivec2(minimal_energy_edges.y, 
                           next_edge[minimal_energy_edges.y]) # (J1, J2)


    next_edge[edge_I.x] = edge_J.y
    previous_edge[edge_I.y] = edge_J.x

    next_edge[edge_J.x] = edge_I.y
    previous_edge[edge_J.y] = edge_I.x 

    #change cycle_index
    point = next_edge[minimal_energy_edges.x] 
    while point != minimal_energy_edges.x: 
        #we keep the first cycle index
        cycle_index[point] = cycle_1_index 
        next_point = next_edge[point]
        point = next_point

    #change cycles
    new_cycle = ti.math.ivec2(cycles[cycle_1_index].x, 
                              cycles[cycle_1_index].y + cycles[cycle_2_index].y)
    cycles[cycle_1_index] = new_cycle
    cycles[cycle_2_index] = ti.math.ivec2(0, 0)

@ti.func
def find_minimal_cycle(cycles: ti.template(), 
                       nb_cycles: int) -> int: 
    '''
    Find the graph cycle with the fewest points. 

    Parameters 
    -------

    cycles: ti.template

        1D vector fields containing the length and starting edge of each cycle. 
        The starting edge is arbitrarily defined. 
        

    Returns
    -------

    int 

        the index of the minimal cycle 
    '''
    minimal_cycle_index = 0 
    minimal_cycle_lenght = ti.math.inf
    cycle_lenght = 0 

    ti.loop_config(serialize=True)
    for cycle_number in range(nb_cycles): 

        cycle = cycles[cycle_number]
        cycle_lenght = cycle.y

        if cycle_lenght < minimal_cycle_lenght\
              and cycle_lenght != 0: 
            minimal_cycle_index = cycle_number
            minimal_cycle_lenght = cycle_lenght

    return minimal_cycle_index

@ti.func
def find_edges_with_minimum_energy(points: ti.template(), 
                                   next_edge: ti.template(),  
                                   cycle_index: ti.template(), 
                                   cycles: ti.template(), 
                                   energies: ti.template(), 
                                   minimal_cycle_index: int)\
                                   -> ti.math.ivec2: 
        
        
    '''
    Find an edge in the minimal cycle and an edge outside this cycle such 
    that the patching energy of these two edges is minimal 
    compared with all the other energies. 

    Parameters 
    -------

    points : ti.template

        field containing the coordinates of all the points in the graph, 
        arranged according to the edges of the grid. 

    next_edge: ti.template

        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    cycle_index: ti.template

        Fields containing the index of the cycle to which each edge belongs, 
        arranged according to 1D indexes of the grid edges.  

    cycles: ti.template

        1D vector fields containing the length and starting edge of each cycle. 
        The starting edge is arbitrarily defined. 

    minimal_cycle_index : int 

        index of the minimal cycle
        

    Returns
    -------

    ti.math.ivec2: 

        int vector containing 1D index of the the edges to stitch
    '''

    minimal_cycle = cycles[minimal_cycle_index]


    start_point_index = minimal_cycle.x

    minimal_energy = ti.math.inf
    minimal_energy_edges = ti.math.ivec2(0, 0)

    end_point_index = 0

    ti.loop_config(serialize=True)
    #cycle.y = lenght of the cycle
    for _ in range(minimal_cycle.y): 
        
        
        reset_energies(energies)
        compute_all_energies(points, 
                             next_edge, 
                             cycle_index, 
                             energies, 
                             start_point_index)
        min_and_index = find_minimum_in_field(energies)
        
        if min_and_index.x < minimal_energy: 
            minimal_energy = min_and_index.x
            minimal_energy_edges = ti.math.ivec2(start_point_index, 
                                                 min_and_index.y)

        end_point_index = next_edge[start_point_index]
        start_point_index = end_point_index


    return minimal_energy_edges

@ti.kernel
def compiled_stitching_algorithm(points: ti.template(), 
                                 previous_edge: ti.template(), 
                                 next_edge: ti.template(), 
                                 cycle_index: ti.template(), 
                                 cycles: ti.template(), 
                                 energies: ti.template()): 

    '''
    Stitch all the cycles of a graph. This is the compiled function called in an non-compiled
    one because we need to create the "energies" field. 

    Parameters 
    -------

    points : ti.template

        field containing the coordinates of all the points in the graph, 
        arranged according to the edges of the grid.

    previous_edge: ti.template

        field containing the previous edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    next_edge: ti.template

        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    cycle_index: ti.template

        Fields containing the index of the cycle to which each edge belongs, 
        arranged according to 1D indexes of the grid edges.  

    cycles: ti.template

        1D vector fields containing the length and starting edge of each cycle. 
        The starting edge is arbitrarily defined. 

    energies : ti.template

        Fields containing the value of the patching energy with the reference edge, 
        arranged according to the edges of the grid. 
        

    Returns
    -------

    None    
    '''
    nb_cycles = cycles.shape[0]

    ti.loop_config(serialize= True)
    for _ in range(nb_cycles - 1): 

        minimal_cycle_index = find_minimal_cycle(cycles, 
                                                 nb_cycles)
        minimal_energy_edges = find_edges_with_minimum_energy(points, 
                                                              next_edge, 
                                                              cycle_index,
                                                              cycles, 
                                                              energies, 
                                                              minimal_cycle_index)
        stitch_two_cycles(previous_edge, 
                          next_edge,
                          cycle_index, 
                          cycles, 
                          minimal_energy_edges)
        
def stitch_all_cycles(points: ti.template(), 
                      previous_edge: ti.template(), 
                      next_edge: ti.template(), 
                      cycle_index: ti.template(), 
                      cycles: ti.template()): 
    
    '''
    Version of the algorithm to be called from the Python scope.

    Parameters 
    -------

    points : ti.template

        field containing the coordinates of all the points in the graph, 
        arranged according to the edges of the grid.

    previous_edge: ti.template

        field containing the previous edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    next_edge: ti.template

        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    cycle_index: ti.template

        Fields containing the index of the cycle to which each edge belongs, 
        arranged according to 1D indexes of the grid edges.  

    cycles: ti.template

        1D vector fields containing the length and starting edge of each cycle. 
        The starting edge is arbitrarily defined. 


    Returns
    -------

    None    
    '''

    energies = ti.field(dtype= float, 
                        shape = points.shape)
    compiled_stitching_algorithm(points, 
                                 previous_edge, 
                                 next_edge, 
                                 cycle_index, 
                                 cycles, 
                                 energies)


'''
OPTIMISED VERSION 
'''

@ti.func
def find_edges_with_minimum_energy_with_neighbours(points: ti.template(), 
                                                    next_edge: ti.template(),  
                                                    cycle_index: ti.template(), 
                                                    cycles: ti.template(), 
                                                    energies: ti.template(), 
                                                    minimal_cycle_index: int, 
                                                    shape: ti.math.ivec2, 
                                                    distance_from_edge: int)\
                                                    -> ti.math.ivec2: 
    
    '''
    Find an edge in the minimal cycle and an edge outside this cycle such 
    that the patching energy of these two edges is minimal 
    compared with all the other energies. This version uses optimisation 
    and only calculates energy for neighbours. The neighbours are defined
    as the edges that are at a distance of "distance_from_edge"  are less 
    from the reference edge.

    Parameters 
    ------

    points : ti.template

        field containing the coordinates of all the points in the graph, 
        arranged according to the edges of the grid. 

    next_edge: ti.template

        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    cycle_index: ti.template

        Fields containing the index of the cycle to which each edge belongs, 
        arranged according to 1D indexes of the grid edges.  

    cycles: ti.template

        1D vector fields containing the length and starting edge of each cycle. 
        The starting edge is arbitrarily defined. 

    minimal_cycle_index : int 

        index of the minimal cycle
    
    shape: ti.math.ivec2

        shape of the scalar field grid
        
    distance_from_edge: int

        distance from the reference edge to compute the neighbours.
        
    Returns
    ------

    ti.math.ivec2: 

        int vector containing 1D index of the the edges to stitch
    '''

    minimal_cycle = cycles[minimal_cycle_index]


    current_edge_1d_index = minimal_cycle.x

    minimal_energy = ti.math.inf
    minimal_energy_edges = ti.math.ivec2(0, 0)

    end_point_index = 0


    #only for neighboring edges 
    ti.loop_config(serialize=True)
    for _ in range(minimal_cycle.y): 
        
        min_and_index = compute_neighbours_energies(points, 
                                                    next_edge, 
                                                    cycle_index, 
                                                    shape, 
                                                    current_edge_1d_index, 
                                                    distance_from_edge)

        if (min_and_index.x < minimal_energy)\
              and (min_and_index.x != ti.math.inf): 
            minimal_energy = min_and_index.x
            minimal_energy_edges = ti.math.ivec2(current_edge_1d_index, 
                                                 min_and_index.y)


        end_point_index = next_edge[current_edge_1d_index]
        current_edge_1d_index = end_point_index
    
    #if we didn't find neighbours, use the classic method 
    if minimal_energy == ti.math.inf: 
        ti.loop_config(serialize=True)
        for _ in range(minimal_cycle.y): 
            
            reset_energies(energies)
            compute_all_energies(points, 
                                 next_edge, 
                                 cycle_index, 
                                 energies, 
                                 current_edge_1d_index)
            min_and_index = find_minimum_in_field(energies)
            
            if min_and_index.x < minimal_energy: 
                minimal_energy = min_and_index.x
                minimal_energy_edges = ti.math.ivec2(current_edge_1d_index, 
                                                     min_and_index.y)

            end_point_index = next_edge[current_edge_1d_index]
            current_edge_1d_index = end_point_index

    return minimal_energy_edges





@ti.kernel
def compiled_stitching_algorithm_with_neighbours(points: ti.template(), 
                                                 previous_edge: ti.template(),
                                                 next_edge: ti.template(), 
                                                 cycle_index: ti.template(), 
                                                 cycles: ti.template(), 
                                                 energies: ti.template(), 
                                                 shape: ti.math.ivec2, 
                                                 distance_from_edge: int): 

    '''
    Stitch all the cycles of a graph. This is the compiled function called in an non-compiled
    one because we need to create the "energies" field. This version uses the optimisation.

    Parameters 
    ------

    points : ti.template

        field containing the coordinates of all the points in the graph, 
        arranged according to the edges of the grid.

    previous_edge: ti.template

        field containing the previous edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    next_edge: ti.template

        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    cycle_index: ti.template

        Fields containing the index of the cycle to which each edge belongs, 
        arranged according to 1D indexes of the grid edges.  

    cycles: ti.template

        1D vector fields containing the length and starting edge of each cycle. 
        The starting edge is arbitrarily defined. 

    energies : ti.template

        Fields containing the value of the patching energy with the reference edge, 
        arranged according to the edges of the grid. 
    
    shape: ti.math.ivec2

        shape of the scalar field grid (useful to compute neighbours)

    distance_from_edge: int

        distance from the reference edge to compute the neighbours.

    Returns
    ------

    None    
    '''
    nb_cycles = cycles.shape[0]

    
    ti.loop_config(serialize= True)
    for _ in range(nb_cycles - 1): 

        minimal_cycle_index = find_minimal_cycle(cycles, 
                                                 nb_cycles)
        minimal_energy_edges = find_edges_with_minimum_energy_with_neighbours(points, 
                                                                                next_edge, 
                                                                                cycle_index, 
                                                                                cycles, 
                                                                                energies, 
                                                                                minimal_cycle_index, 
                                                                                shape, 
                                                                                distance_from_edge)
        stitch_two_cycles(previous_edge, 
                          next_edge, 
                          cycle_index, 
                          cycles, 
                          minimal_energy_edges)
        
def stitch_all_cycles_with_neighbourhood(points: ti.template(), 
                                         previous_edge: ti.template(), 
                                         next_edge: ti.template(), 
                                         cycle_index: ti.template(), 
                                         cycles: ti.template(), 
                                         shape: ti.math.ivec2, 
                                         distance_from_edge: int): 
    '''
    Version of the algorithm to be called from the Python scope.
    It uses the optimisation. We need to create the "energies" field, so this 
    function is a wrapper for the compiled function.

    Parameters 
    ------

    points : ti.template

        field containing the coordinates of all the points in the graph, 
        arranged according to the edges of the grid.

    previous_edge: ti.template

        field containing the previous edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    next_edge: ti.template

        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    cycle_index: ti.template

        Fields containing the index of the cycle to which each edge belongs, 
        arranged according to 1D indexes of the grid edges.  

    cycles: ti.template

        1D vector fields containing the length and starting edge of each cycle. 
        The starting edge is arbitrarily defined. 

    shape: ti.math.ivec2

        shape of the scalar field grid (useful to compute neighbours)

    distance_from_edge: int

        distance from the reference edge to compute the neighbours.
        
    Returns
    ------

    None    
    '''
    energies = ti.field(dtype= float, 
                        shape = points.shape)
    compiled_stitching_algorithm_with_neighbours(points, 
                                                 previous_edge, 
                                                 next_edge, 
                                                 cycle_index, 
                                                 cycles, 
                                                 energies, 
                                                 shape, 
                                                 distance_from_edge)