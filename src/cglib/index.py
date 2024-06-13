import taichi as ti 



@ti.func
def index2d_to_edge_index(
        cell: ti.math.ivec2, 
        grid_shape: ti.math.ivec2) -> ti.math.ivec4: 
    '''
    Give the 1D index of the four edges forming a grid cell. 
    The edges are numbered in the following order: 
        - horizontal then vertical edges 
        - top to bottom 
        - left to right 
    The 1D index corresponds to this numbering.

    Parameters 
    __________

    cell: ti.math.ivec2 

        the 2D index of the cell which we want the edge indexes
        
    grid_shape: ti.math.ivec2

        2D shape of the scalar field grid


    Returns
    _______

    ti.math.ivec4

        edge 1D indexes 
    '''
    shape_x = grid_shape.x
    shape_y = grid_shape.y

    hoizontal_top_edge_index = cell.x * shape_y + cell.y
    horizontal_bottom_edge_index = (cell.x + 1 ) * shape_y + cell.y 

    first_vertical_edge_index = shape_y  * (shape_x + 1) 

    vertical_left_edge_index = first_vertical_edge_index +\
                                cell.x*(shape_y +1) +\
                                cell.y
    vertical_right_edge_index = first_vertical_edge_index +\
                                cell.x*(shape_y +1) +\
                                cell.y + 1

    
    vec = ti.math.ivec4(hoizontal_top_edge_index, 
                        vertical_right_edge_index,
                        horizontal_bottom_edge_index,  
                        vertical_left_edge_index)
 
    return vec 

@ti.func
def index2d_to_cartesians_coo(
        grid_shape: ti.math.ivec2, 
        cell: ti.math.ivec2) -> ti.math.vec2: 
    '''
    Gives the Cartesian coordinates of the point at the top left 
    of the cell whose 2D index is passed as an argument. They 
    range from 0 to 1.

    Parameters 
    __________

    grid_shape: ti.math.ivec2

        2D shape of the scalar field grid

    cell: ti.math.ivec2 

        the 2D index of the cell which we want the coordinates

        
    Returns
    _______

    ti.math.vec2

        cartesian coordinates (x, y)
    '''

    cell_count_x = ti.math.max(grid_shape.x, 
                               grid_shape.y)
    
    x = float(cell.x / cell_count_x)
    y = float(cell.y / cell_count_x)
    
    return ti.math.vec2(x, y)

@ti.func
def edge_1d_to_3d_index(
        shape: ti.math.ivec2, 
        edge: int) -> ti.math.ivec3: 
    '''
    Gives the 3D index of an edge. The 3D index is obtained as follows: 
        - The z coordinate is 0 for horizontal edges, 1 for vertical edges 
        - The x and y coordinates are obtained by looking at the position of the edge, 
            taking into account only edges with the same orientation. 

    Parameters 
    -------

    shape: ti.math.ivec2

        2D shape of the scalar field grid

    edge: int

        1D index of the edge which we want the 3D index. 

        
    Returns
    -------

    ti.math.vec3

        3D index of the edge
    '''

    result = ti.math.ivec3(0, 0, 0)

    maximal_horizontal_index = shape.y * (shape.x + 1) 

    #if the edge is horizontal 
    if edge < maximal_horizontal_index:  
        result.z = 0 
        result.x = edge // shape.y
        result.y = edge % shape.y

    # if the edge is vertical  
    else: 
        result.z = 1
        result.x = (edge - maximal_horizontal_index) // (shape.y + 1)
        result.y = (edge - maximal_horizontal_index) % (shape.y + 1)

    return result 

@ti.func
def edge_3d_to_1d_index(
        shape: ti.math.ivec2, 
        x: int, 
        y: int, 
        z: int) -> int: 
    '''
    Converts the 3D index of an edge to 1D index. 

    Parameters 
    -------

    shape: ti.math.ivec2

        2D shape of the scalar field grid

    x: int

        x coo of the 3D index 

    y: int 

        y coo of the 3D index

    z: int 

        z coo of the 3D index 

        
    Returns
    -------

    int 

        1D edge index 
    '''

    result = 0

    #if the edge is horizontal 
    if z == 0: 
        if (x < 0)\
            or (x > shape.x)\
            or (y < 0)\
            or (y >= shape.y) :

            result = -1

        else: 
            result = x * shape.y + y

    # if the edge is vertical  
    if z == 1: 
        if (x < 0)\
            or (x >= shape.x)\
            or (y < 0)\
            or (y > shape.y):

            result = -1
        else: 
            maximal_horizontal_index = shape.y * (shape.x + 1) 
            result = maximal_horizontal_index + x * (shape.y + 1) + y

    return result