import taichi as ti 



'''
This module contains functions to check if two functions are valid: 

    - check_if_one_cycle: check if there is only one cycle in the graph and if it is closed.
    - check_closure: check if all cycles in the graph are closed.

'''



@ti.kernel
def check_if_one_cycle(
        next_edge: ti.template(),   
        cycles: ti.template()) -> bool:
    '''
    Check if there is only one cycle in the graph and if it is closed.

    Parameters:
    -----------

    next_edge: ti.template

        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    cycles: ti.template

        1D vector fields containing the length and starting edge 
        of each cycle. The starting edge is arbitrarily defined. 

    Returns:
    --------

    bool: 
        
        True if there is only one cycle and if it is closed, 
        False otherwise.

    '''
    result = 1
    nb_cycles = 0 
    
    for x_index in cycles: 
        if cycles[x_index].y != 0: 
            nb_cycles += 1
            result = flood(next_edge, cycles[x_index])

    if nb_cycles != 1: 
        result = 0
    
    return result

@ti.kernel
def check_closure(
        next_edge: ti.template(),   
        cycles: ti.template()) -> bool:
    
    '''
    Check if all cycles in the graph are closed.

    Parameters: 
    -----------

    next_edge: ti.template

        field containing the next edge of an edge in a cycle,
        arranged according to 1D indexes of the grid edges.
    
    cycles: ti.template

        1D vector fields containing the length and starting edge
        of each cycle. The starting edge is arbitrarily defined.

    Returns:
    --------

    bool:

        True if all cycles are closed, False otherwise.
    '''
    result = 1
    for x_index in cycles: 
        if cycles[x_index].y != 0: 
            result = flood(next_edge, 
                           cycles[x_index])
    
    return result

@ti.func
def flood(
        next_edge: ti.template(),   
        cycle: ti.math.ivec2) -> bool:
    '''
    Check if a cycle is closed.

    Parameters:
    -----------

    next_edge: ti.template()

        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    cycle: ti.math.ivec2

        1D vector field containing the length and starting 
        edge of the cycle to check.

    Returns:
    --------

    bool:

        True if the cycle is closed, False otherwise.
    '''
    res = 1
    current_edge = next_edge[cycle.x]
    ti.loop_config(serialize=True)
    for _ in range(cycle.y - 1): 
    
        next = next_edge[current_edge]
        current_edge = next

    if current_edge != cycle.x: 
        res = 0
    
    return res 