import taichi as ti 

from cglib.index import index2d_to_cartesians_coo, edge_1d_to_3d_index, edge_3d_to_1d_index



@ti.func
def linear_interpolation(grid: ti.template(), 
                         point_0_index : ti.math.ivec2, 
                         point_1_index: ti.math.ivec2, 
                         value: float)\
                         -> ti.math.vec2: 
    '''
    Find the point on a segment where a function, or a scalar field is equal to the value in argument
    by approximating this function by a linear function. 

    Parameters 
    -------

    grid: ti.template 

        the 2D field containing the scalar field values. 

    point_0_index, point_1_index: ti.math.ivec2

        the 2D index of the grid points forming the segment. 
        value : value whose abscissa we want to find on the segment. 

    Returns
    -------

    ti.math.vec2 : 

        the 2D index of the point on the segment whose value 
        in the scalar field is equal to the value passed as an argument. 
    '''

    point_0 = index2d_to_cartesians_coo(ti.math.ivec2(grid.shape[0], grid.shape[1]), 
                                        point_0_index)
    point_1 = index2d_to_cartesians_coo(ti.math.ivec2(grid.shape[0],grid.shape[1]), 
                                        point_1_index)
    
    res_x = 0.
    res_y = 0.


    if point_0_index.y == point_1_index.y: 
        res_x = point_0.x + (value-grid[point_0_index.x, point_0_index.y]) *\
              (point_1.x - point_0.x) / (grid[point_1_index.x, point_1_index.y]\
                                         -grid[point_0_index.x, point_0_index.y])
        res_y = point_1.y

    else: 
        res_y = point_0.y + (value-grid[point_0_index.x, point_0_index.y]) *\
              (point_1.y - point_0.y) / (grid[point_1_index.x, point_1_index.y]\
                                         -grid[point_0_index.x, point_0_index.y])
        res_x = point_0.x

    return ti.math.vec2(res_x, 
                        res_y)

@ti.func
def euclidean_distance(vector: ti.math.vec2)\
                 -> float: 

    '''
    Calculate the Euclidean distance of a two-dimensional vector.

    Parameters 
    -------

    vector : ti.math.vec2

        the two-dimensionnal vector
    

    Returns
    -------

    float: 

        his Euclidean distance. 
    '''
    return ti.math.sqrt(vector.x **2 + vector.y**2)

@ti.func
def compute_all_energies(points: ti.template(), 
                         next_edge: ti.template(), 
                         cycle_index: ti.template(), 
                         energies: ti.template(), 
                         current_edge_1d_index: int): 
   
   
    '''
    For a given edge of the graph, calculate all the patching energies between this edge 
    and edges not belonging to the same cycle. 

    Parameters 
    -------

    points : ti.template

        field containing the coordinates of all the points in the graph, 
        arranged according to 1D indexes of the grid edges. 
    
    next_edge : ti.template
    
        field containing the next edge of an edge in a cycle, 
        arranged according to the edges of the grid. 

    cycle_index : ti.template

        Fields containing the index of the cycle to which each edge belongs, 
        arranged according to the edges of the grid. 

    energies : ti.template

        Fields containing the value of the patching energy with the reference edge, 
        arranged according to the edges of the grid. 

    current_edge_1d_index : int

        1D index of the reference edge which will be used to calcultate the energies. 

        
    Returns
    -------

    None
    '''

    edge_I = ti.math.ivec2(current_edge_1d_index, 
                           next_edge[current_edge_1d_index])
    edge_cycle = cycle_index[current_edge_1d_index]


    for index in range(energies.shape[0]): 
        
        #if there is a point thesame cycle
        if cycle_index[index] == edge_cycle:  
            energies[index] = ti.math.inf

        #if there is no point
        elif cycle_index[index] == -1: 
            energies[index] = ti.math.inf

        #if there is a point belonging to another cycle
        elif cycle_index[index] != edge_cycle: 


            energy = 0. 
            edge_J = ti.math.ivec2(index, next_edge[index])
            i_1 = points[edge_I.x]
            i_2 = points[edge_I.y]
            j_1 = points[edge_J.x]
            j_2 = points[edge_J.y]

            cross = euclidean_distance(i_1 - j_2) + euclidean_distance(i_2 - j_1) 
            no_cross = euclidean_distance(i_1 - j_1) + euclidean_distance(i_2 - j_2)

            if cross < no_cross: 
                energy = cross - euclidean_distance(i_1 - i_2) - euclidean_distance(j_2 - j_1)
            else: 
                energy = no_cross - euclidean_distance(i_1 - i_2) - euclidean_distance(j_2 - j_1)

            energies[index] = energy 

@ti.func
def compute_neighbours_energies(points: ti.template(), 
                                next_edge: ti.template(), 
                                cycle_index: ti.template(),
                                shape: ti.math.ivec2, 
                                current_edge_1d_index: int, 
                                distance_from_edge: int) -> ti.math.vec2: 
    '''
    For a given edge of the graph, calculate all the patching energies between this edge 
    and neighbouring edges not belonging to the same cycle. The neighbouring edges are
    the edges that are at a distance of 2 from the reference edge.

    Parameters 
    -------

    points : ti.template

        field containing the coordinates of all the points in the graph, 
        arranged according to the edges of the grid. 
    
    next_edge : ti.template
    
        field containing the next edge of an edge in a cycle, 
        arranged according to the edges of the grid. 

    cycle_index : ti.template

        Fields containing the index of the cycle to which each edge belongs, 
        arranged according to the edges of the grid. 

    shape : ti.math.ivec2

        the dimensions of the scalar field grid. 

    current_edge_1d_index : int

        1D index of the reference edge which will be used to calcultate the energies. 

        
    Returns
    -------

    ti.math.ivec2: 

        x: minimal energy for the current edge
        y: 1D index of the edge which has the minimal energy with the current edge
    '''
    
    #I use 3D edge index instead of 1D edge index
    edge_I = ti.math.ivec2(current_edge_1d_index, 
                           next_edge[current_edge_1d_index])
    edge_I_cycle = cycle_index[current_edge_1d_index]
    edge_I_3d_index = edge_1d_to_3d_index(shape, 
                                          current_edge_1d_index)

    minimal_energy = ti.math.inf
    minimum_value_3d_index = ti.math.ivec3(0, 0, 0)
    k = distance_from_edge*2 +1 
    ti.loop_config(serialize= True)
    for x_index in range(k): 
        ti.loop_config(serialize= True)
        for y_index in range(k): 
            ti.loop_config(serialize= True)
            for z_index in range(2): 

                edge_J_1d_index = edge_3d_to_1d_index(shape, 
                                                      edge_I_3d_index.x + x_index - distance_from_edge, 
                                                      edge_I_3d_index.y + y_index - distance_from_edge, 
                                                      z_index)
                #if there is a point in the same cycle or no point at all 
                if (cycle_index[edge_J_1d_index] == edge_I_cycle)\
                  or (cycle_index[edge_J_1d_index] == -1):  
                    pass
                
                #if there is a point in another cycle 
                else: 

                    energy = 0.
                    edge_J = ti.math.ivec2(edge_J_1d_index, next_edge[edge_J_1d_index])
                    i_1 = points[edge_I.x]
                    i_2 = points[edge_I.y]
                    j_1 = points[edge_J.x]
                    j_2 = points[edge_J.y]

                    cross = euclidean_distance(i_1 - j_2) + euclidean_distance(i_2 - j_1) 
                    no_cross = euclidean_distance(i_1 - j_1) + euclidean_distance(i_2 - j_2)

                    if cross < no_cross: 
                        energy = cross - euclidean_distance(i_1 - i_2)\
                          - euclidean_distance(j_2 - j_1)
                    else: 
                        energy = no_cross - euclidean_distance(i_1 - i_2)\
                          - euclidean_distance(j_2 - j_1)

                    if energy < minimal_energy and energy != ti.math.inf: 
                        minimal_energy = energy
                        minimum_value_3d_index = ti.math.ivec3(x_index, 
                                                               y_index, 
                                                               z_index)


    res = ti.math.vec3(edge_I_3d_index.x + minimum_value_3d_index.x - distance_from_edge, 
                       edge_I_3d_index.y + minimum_value_3d_index.y - distance_from_edge, 
                       minimum_value_3d_index.z)


    return ti.math.vec2(minimal_energy, 
                        edge_3d_to_1d_index(shape, 
                                            res.x, 
                                            res.y, 
                                            res.z))