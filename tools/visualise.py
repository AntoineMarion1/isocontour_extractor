import taichi as ti 
import argparse


from cglib.polylines import graph_to_polylines
from cglib.fields import normalize_grid, compute_pixels, shift_lines
from cglib.type import numpy_to_field, numpy_contour_to_data_structure



ti.init(arch = ti.cpu)



if __name__ == "__main__": 

    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", 
                        help= "File in .npy format containing the scalar field to be displayed.")
    
    parser.add_argument("datatosee", 
                        help= "display the scalar field (scalar), a single stitched cycle (cycle), or all the isocontours of the scalar field (contour). ")
    
    parser.add_argument("window_size", 
                        help="Size of the window in pixels. Default is 720x720.",
                        default = 720, 
                        nargs='?')

    args = parser.parse_args()

    file_name = args.input_filename
    data_to_see = args.datatosee
    window_size = int(args.window_size)

    #get the scalar field and put it in a square grid, to be displayed in a square window. 
    grid = numpy_to_field(file_name)
    normalize_grid(grid)
    pixels = ti.Vector.field(n = 3, 
                            dtype = float, 
                            shape = (ti.math.max(grid.shape[0], grid.shape[1]), 
                                    ti.math.max(grid.shape[0], grid.shape[1])))
    compute_pixels(pixels, 
                    grid)
    
    #create the window and the canvas 
    window = ti.ui.Window("visualise "+ data_to_see, (window_size, window_size))
    canvas = window.get_canvas()


    # display the scalar field 
    if data_to_see == "scalar": 

        while window.running: 
            canvas.set_image(pixels)
            window.show()

    #display the contour
    elif data_to_see == "contour": 

        try: 
            switch = 1 
            
            #get the contour data
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

        except FileNotFoundError: 
            print("Please run the main tool before displaying the stitched cycle")

    #display the single cycle
    elif data_to_see == "cycle": 
        
        try: 
            switch = -1 
            
            points, previous_edge, next_edge, cycle_index, cycles =\
                  numpy_contour_to_data_structure(file_name + "_contour")
            points_stitched, previous_edge_stitched, next_edge_stitched, cycle_index_stitched, cycles_stitched =\
                  numpy_contour_to_data_structure(file_name + "_cycle")

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
                    switch = 1
                else: 
                    switch = -1

                if switch == 1: 
                    canvas.lines(lines, 
                                 color=(0., 0.99, 0.), 
                                 width=.001)
                else: 
                    canvas.lines(lines_stitched, 
                                 color=(0., 0., 0.99), 
                                 width=.001)
                window.show()

        except FileNotFoundError: 
            print("Please run the main tool before displaying the isocontour of the scalar field.")

    else: 
        print('Please enter either contour, cycle or scalar as the second argument.')