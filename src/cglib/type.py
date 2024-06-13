import taichi as ti
import numpy as np 
import tqdm

from svgpathtools import Line, Path, paths2svg



def numpy_to_field(file_path: str) -> ti.template(): 

    '''
    Imports an .npy file containing a scalar field and stores its data in a Taichi field. 
    the file must be located at data/fields. A border of -1 is added to the field.

    Parameters 
    -------

    input_filename

        name of the file without the extension 

        
    Returns
    -------

    ti.template

        field containing the data of the file 
    '''

    imported_arr = np.load(file_path)
    arr = imported_arr.reshape(imported_arr.shape[1], 
                               imported_arr.shape[0])
    arr = arr.astype(np.float32) #convert the array to float32
    arr = arr.T #transpose the array so that the x and y axis are correctly oriented.
    
    
    # Add a border of -1 to the field, so that the edges of the grid 
    # are not considered as part of the field. 
    n, m = arr.shape
    ones_col = np.ones((n, 1))
    arr = np.hstack((ones_col, arr))
    arr = np.hstack((arr, ones_col))

    n, m = arr.shape
    ones_row =  np.ones((1, m))
    arr = np.vstack((ones_row, arr))
    arr = np.vstack((arr, ones_row))    


    # Create a Taichi field and import the data from the numpy array.
    f = ti.field(dtype = float, 
                 shape = arr.shape)
    f.from_numpy(arr)
    return f 

def data_structure_to_numpy(
        points: ti.template(), 
        previous_edge: ti.template(), 
        next_edge: ti.template(), 
        cycle_index: ti.template(), 
        cycles: ti.template(), 
        file_name: str): 
    
    '''
    Exports graph data to an .npz file. The output file will be 
    data/np/file_name.npz

    Parameters 
    -------
    
    points: ti.template

        field containing the coordinates of all the points in the graph, 
        arranged according to 1D indexes of the grid edges. 

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

    file_name

        name of the output file 

        
    Returns
    -------

    None
    '''

    
    points_array = points.to_numpy()
    next_edge_array = next_edge.to_numpy(dtype = int)
    previous_edge_array = previous_edge.to_numpy(dtype = int)
    cycle_index_array = cycle_index.to_numpy(dtype= int)
    cycles_array = cycles.to_numpy(dtype = int)
    output_file_name = "data/np/" + file_name

    np.savez(file=output_file_name, 
             points = points_array, 
             next_edge = next_edge_array, 
             previous_edge = previous_edge_array, 
             cycle_index = cycle_index_array, 
             cycles = cycles_array)

def numpy_contour_to_data_structure(file_name: str) -> tuple[ti.template(), 
                                                             ti.template(), 
                                                             ti.template(), 
                                                             ti.template(),
                                                             ti.template()]: 
    
    '''
    Imports graph data from an .npz file and stores it in fields. 

    Parameters 
    -------
    
    file_name

        name of the .npz file where the data are stored. 

        
    Returns
    -------

    tuple (ti.template)
    
        fields describing the graph
        - points 
        - previous_edge 
        - next_edge 
        - cycle_index 
        - cycles 
    
    '''

    filepath = "data/np/" + file_name + ".npz"
    npz_file = np.load(filepath)
    

    points = ti.Vector.field(n=2, 
                             dtype=float, 
                             shape=npz_file["previous_edge"].shape) 
    previous_edge= ti.field(dtype = int, 
                            shape = npz_file["previous_edge"].shape)
    next_edge= ti.field(dtype = int, 
                        shape = npz_file["previous_edge"].shape)
    cycle_index = ti.field(dtype = int, 
                           shape = npz_file["previous_edge"].shape) 
    cycles = ti.Vector.field(n = 2, 
                             dtype = int, 
                             shape = npz_file["cycles"].shape[0])

    points.from_numpy(npz_file["points"])
    previous_edge.from_numpy(npz_file["previous_edge"])
    next_edge.from_numpy(npz_file["next_edge"])
    cycle_index.from_numpy(npz_file["cycle_index"])
    cycles.from_numpy(npz_file["cycles"])

    return points, previous_edge, next_edge, cycle_index, cycles

def data_structure_to_svg(
        points: ti.template(), 
        next_edge: ti.template(), 
        cycles: ti.template(), 
        output_name: str): 
    '''
    Exports graph data to a SVG file. 

    Parameters 
    -------

    points: ti.template

        field containing the coordinates of all the points in the graph, 
        arranged according to 1D indexes of the grid edges. 
    
    next_edge: ti.template

        field containing the next edge of an edge in a cycle, 
        arranged according to 1D indexes of the grid edges. 

    cycles: ti.template

        1D vector fields containing the length and starting edge of each cycle. 
        The starting edge is arbitrarily defined. 

    output_name

        name of the output file 

        
    Returns
    -------

    None
    '''

    def vector_to_complex(vec: ti.math.vec2) -> complex: 
        '''
        Converts a 2D vector to a complex number.
        we use a minus sign for the imaginary part, 
        so that the y axis is oriented downwards.
        
        Parameters
        -------

        vec: ti.math.vec2

            2D vector to convert to a complex number.

        Returns
        -------

        complex
            
                complex number corresponding to the input vector.
        '''
        return vec.x - 1j * vec.y
        

    paths = []

    for cycle_number in tqdm.tqdm(range(cycles.shape[0])): 

        cycle = cycles[cycle_number]
        
        path_i = Path()
        start_edge_index = cycle.x

        if cycle.y != 0: 

            for _ in range(cycle.y): #cycle.t = lenght of the cycle

                end_edge_index = next_edge[start_edge_index]
                
                
                start_point = points[start_edge_index]
                end_point = points[end_edge_index]

                line = Line(vector_to_complex(start_point), 
                            vector_to_complex(end_point))
                path_i.append(line)
                start_edge_index = end_edge_index
            
            paths.append(path_i)

        cycle_number +=1 

    paths2svg.wsvg(paths, 
                   filename= "data/svg_files/"\
                        + output_name\
                        + ".svg")