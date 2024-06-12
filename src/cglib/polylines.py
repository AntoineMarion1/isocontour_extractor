import taichi as ti 



@ti.kernel
def compute_lines(lines: ti.template(), 
                  points: ti.template(), 
                  next_edge: ti.template(), 
                  cycles: ti.template()): 
    
    '''
    Compute the polylines described by the graph. 

    Parameters 
    ----------

    points: ti.template

        field containing the coordinates of all the points in the graph, 
        arranged according to 1D indexes of the grid edges. 
    
    next_edge: ti.template

        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    cycles: ti.template

        1D vector fields containing the length and starting edge of each cycle. 
        The starting edge is arbitrarily defined. 
        
    lines

        field containing the data of the polylines


    Returns
    -------

    None    
    '''

    line_index = 0
    point_index =  0 

    ti.loop_config(serialize= True)
    for cycle_index in range(cycles.shape[0]): 

        cycle = cycles[cycle_index] 
        point_index = cycle.x
        
        ti.loop_config(serialize=True)
        for _ in range(cycle.y): 

            lines[line_index] = points[point_index]
            lines[line_index +1] = points[next_edge[point_index]]
            line_index += 2 


            next_point = next_edge[point_index]
            point_index = next_point

def graph_to_polylines(points: ti.template(), 
                       next_edge: ti.template(), 
                       cycles: ti.template())\
                       -> ti.template(): 

    '''
    Returns the polylines of a graph in a field that can be used by the Taichi visualisation tool. 

    Parameters 
    ----------

    points: ti.template

        field containing the coordinates of all the points in the graph, 
        arranged according to 1D indexes of the grid edges. 
    
    next_edge: ti.template

        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    cycles: ti.template

        1D vector fields containing the length and starting edge of each cycle. 
        The starting edge is arbitrarily defined. 
        

    Returns
    -------

    ti.template

        field containing the data of the polylines
    '''

    lines = ti.Vector.field(dtype = float, 
                            n = 2, 
                            shape = points.shape) 
    lines.fill(ti.math.nan)
    compute_lines(lines, 
                  points, 
                  next_edge,
                  cycles)
    
    return lines