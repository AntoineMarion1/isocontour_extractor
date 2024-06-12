import taichi as ti 
import argparse
import json

from cglib.polylines import graph_to_polylines
from cglib.fields import normalize_grid, compute_pixels, shift_lines
from cglib.type import numpy_to_field, numpy_contour_to_data_structure



ti.init(arch = ti.cpu)



if __name__ == "__main__": 

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file_path", 
                        help= "File in .npy format containing the scalar field to be displayed.",
                        type = str)
    
    parser.add_argument("datatosee", 
                        type= str,
                        help= "display the scalar field (scalar), a single stitched cycle (cycle), or all the isocontours of the scalar field (contour). ")
    
    parser.add_argument("window_size", 
                        help="Size of the window in pixels. Default is 720x720.",
                        type = int, 
                        default = 720, 
                        nargs='?')

    args = parser.parse_args()

    file_path = args.input_file_path
    data_to_see = args.datatosee
    window_size = int(args.window_size)
    
    #get the scalar field and put it in a square grid, to be displayed in a square window. 
    grid = numpy_to_field(file_path)
    normalize_grid(grid)
    pixels = ti.Vector.field(n = 3, 
                            dtype = float, 
                            shape = (ti.math.max(grid.shape[0], grid.shape[1]), 
                                    ti.math.max(grid.shape[0], grid.shape[1])))
    compute_pixels(pixels, 
                    grid)
    
    #create the window and the canvas 
    window = ti.ui.Window("visualise "+ data_to_see, 
                          (window_size, window_size))
    canvas = window.get_canvas()


    # display the scalar field 
    if data_to_see == "scalar": 

        while window.running: 
            canvas.set_image(pixels)
            window.show()

    #display the isocontours of the scalar field and the single cycle
    elif data_to_see == "both": 
        
        try: 
                #extract the file name
            with open('data/do_not_delete/output_file_names.json', 'r') as f:
                data = json.load(f)
                file_name = data[file_path]

            switch = 1 
            
            #get the contour and cycle data 
            points, previous_edge, next_edge, cycle_index, cycles =\
                  numpy_contour_to_data_structure(file_name + "_contour")
            points_stitched, previous_edge_stitched, next_edge_stitched, cycle_index_stitched, cycles_stitched =\
                  numpy_contour_to_data_structure(file_name + "_cycle")

            #transform the graph data structure into polylines
            lines = graph_to_polylines(points, 
                                       next_edge, 
                                       cycles)
            shift_lines(grid, 
                        lines)
            lines_stitched = graph_to_polylines(points_stitched,
                                                next_edge_stitched,
                                                cycles_stitched)
            shift_lines(grid,
                        lines_stitched)   
            
            while window.running: 
                canvas.set_image(pixels)
                if window.is_pressed(" "): 
                    switch = -1
                else: 
                    switch = 1

                if switch == 1: 
                    canvas.lines(lines, 
                                 color=(0., 0.99, 0.), 
                                 width=.001)
                else: 
                    canvas.lines(lines_stitched, 
                                 color=(0., 0., 0.99), 
                                 width=.001)
                window.show()

        except FileNotFoundError or KeyError: 
            print("Please run the contour and the stitch tools before displaying both the isocontours and the single cycle.")

    #display the single cycle
    elif data_to_see == "cycle": 
        
        try: 

            #extract the file name
            with open('data/do_not_delete/output_file_names.json', 'r') as f:
                data = json.load(f)
                file_name = data[file_path]
            
            points_stitched, previous_edge_stitched, next_edge_stitched, cycle_index_stitched, cycles_stitched =\
                  numpy_contour_to_data_structure(file_name + "_cycle")

            lines_stitched = graph_to_polylines(points_stitched,
                                                next_edge_stitched, 
                                                cycles_stitched)
            shift_lines(grid, 
                        lines_stitched)
            
            while window.running: 
                canvas.set_image(pixels)
                canvas.lines(lines_stitched, 
                            color=(0., 0., 0.99), 
                            width=.001)
                window.show()

        except FileNotFoundError or KeyError: 
            print("Please run the stitch tool before displaying the single cycle.")
            raise FileNotFoundError
    
    #display the isocontours of the scalar field 
    elif data_to_see == "contour": 

        try: 
            
                #extract the file name
            with open('data/do_not_delete/output_file_names.json', 'r') as f:
                data = json.load(f)
                file_name = data[file_path]

            #get the contour data
            points, previous_edge, next_edge, cycle_index, cycles =\
                  numpy_contour_to_data_structure(file_name + "_contour")
     
            #transform the graph data structure into polylines
            lines = graph_to_polylines(points, 
                                       next_edge, 
                                       cycles)
            shift_lines(grid, 
                        lines)
            
            while window.running: 
                canvas.set_image(pixels)
            
                canvas.lines(lines, 
                            color=(0., 0.99, 0.), 
                            width=.001)
                window.show()

        except FileNotFoundError or KeyError: 
            print("Please run the contour tool before displaying the isocontours of the scalar field.")
            raise FileNotFoundError
    else: 
        print('Please enter either "scalar", "contour", "cycle" or "both" as the second argument.')