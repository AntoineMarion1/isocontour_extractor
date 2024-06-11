import taichi as ti



@ti.func
def reset_energies(energies: ti.template()): 
    '''
    Resets the value of the entire field to Nan. 

    Parameters 
    -------

    energies : ti.template

        Fields containing the value of the patching energy with the reference edge, 
        arranged according to the edges of the grid. 

        
    Returns
    -------

    None
    '''

    for index in range(energies.shape[0]): 
        energies[index] = ti.math.inf

@ti.func
def find_minimum_in_field(f: ti.template())\
                            -> ti.math.vec2: 
    '''
    Find the minimum value and the position of this minimum in a field. 

    Parameters 
    -------

    f : ti.template

        1D field for which we want to know the minimum

        
    Returns
    -------

    ti.math.vec2

        x: minimum of the field 
        y: index of the minimum 
    '''
    minimal_value = ti.math.inf
    index = 0
        
           
    ti.loop_config(serialize=True)
    for i in range(f.shape[0]):
        
        if f[i] < minimal_value\
              and f[i] != ti.math.inf: 
            minimal_value = f[i]
            index = i

    return ti.math.vec2(minimal_value, 
                        index)

@ti.kernel
def count_cycles(cycles: ti.template())\
                 -> int: 
    '''
    Count the numbers of elements (cycles) in the 'cycles' field, 
    used for the graph data. 

    Parameters 
    -------

    cycles : ti.template

        1D Vector field for which we want to the number of cycles 
        which size is different from 0

        
    Returns
    -------

    int

        number of cycles
    '''
    cycles_count = 0

    for index in cycles: 
        if cycles[index].y != 0: 
            cycles_count += 1 
    
    return cycles_count
    
@ti.kernel 
def fill_final_cycles(cycles: ti.template(), 
                      final_cycles: ti.template()): 
    '''
    Fill the field final_cycles with the data of cycles

    Parameters 
    -------

    cycles : ti.template

        1D Vector field with useless [0, 0] vectors. 

    final_cycles : ti.template 
        
        1D Vector field without useless vectors. 


    Returns
    -------

    None
    '''
    for index in final_cycles: 
        final_cycles[index] = cycles[index]

@ti.kernel
def compute_pixels(pixels: ti.template(), 
                   grid: ti.template()): 
    '''
    Fill the field pixels with the data of grid, in order to be able 
    to display the grid,  which can be in a non-square field. 

    Parameters 
    -------

    pixels : ti.template

        2D square field displayed in a window. 

    grid : ti.template 
        
        the 2D field containing the scalar field values. 

        
    Returns
    -------

    None
    '''
    pixels.fill(viridis(1.))
    for x_index, y_index in grid: 
        pixels[x_index, y_index] = viridis(grid[x_index, y_index])

@ti.kernel 
def normalize_grid(grid: ti.template()): 
    '''
    Transforms the field values so that they are between 0 and 1. 

    Parameters 
    -------

    grid : ti.template 
        
        the 2D field containing the scalar field values. 

        
    Returns
    -------

    None
    '''
    for x_index, y_index in grid: 
        key = grid[x_index, y_index]
        grid[x_index, y_index] = key / 2 + 0.5

@ti.kernel
def shift_lines(grid: ti.template(), 
                lines: ti.template()): 


    '''
    Shift all the lines of half a cell. The scalar field display is 
    offset from the window, so the lines must also be offset. 

    Parameters 
    -------

    grid : ti.template 
        
        the 2D field containing the scalar field values. 

    lines : ti.template 
        
        1D Vector field containing the coordinates of the points 
        forming the polylines. 

    Returns
    -------

    None
    '''
    shift = float(1/(2*ti.math.max(grid.shape[0], grid.shape[1])))

    for x_index in lines: 
        key = lines[x_index] 
        lines[x_index] = ti.math.vec2(key.x + shift, 
                                      key.y + shift)
    
@ti.func
def viridis(t: float) -> ti.math.vec3:
    '''
    Associate a vector with a floating-point number. This vector 
    corresponds to the RBG coding of the colour associated 
    with this float.  

    Parameters 
    -------

    t: float 

        the number which we want the RGB coding.


    Returns
    -------

    ti.math.vec3

        RGB coding
    '''
    c0 = ti.math.vec3(0.2777273272234177, 0.005407344544966578, 0.3340998053353061)
    c1 = ti.math.vec3(0.1050930431085774, 1.404613529898575, 1.384590162594685)
    c2 = ti.math.vec3(-0.3308618287255563, 0.214847559468213, 0.09509516302823659)
    c3 = ti.math.vec3(-4.634230498983486, -5.799100973351585, -19.33244095627987)
    c4 = ti.math.vec3(6.228269936347081, 14.17993336680509, 56.69055260068105)
    c5 = ti.math.vec3(4.776384997670288, -13.74514537774601, -65.35303263337234)
    c6 = ti.math.vec3(-5.435455855934631, 4.645852612178535, 26.3124352495832)
    
    return c0 + t * (c1 + t * (c2 + t * (c3 + t * (c4 + t * (c5 + t * c6)))))