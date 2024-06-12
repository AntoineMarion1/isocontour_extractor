import taichi as ti
import time
import argparse
import logging
import json 
import os 

from cglib.type import numpy_to_field, data_structure_to_numpy, numpy_contour_to_data_structure
from cglib.stitch import stitch_all_cycles_with_neighbourhood



ti.init(arch = ti.cpu)



if __name__ == "__main__": 

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file_path", 
                        help= "File in .npy format containing a scalar field whose isocontours to stitch.", 
                        type = str)
    parser.add_argument("neighbours",
                        help= "Distance of neighbours to consider when stitching the isocontours.",
                        type = int, 
                        default = 5, 
                        nargs= '?')

    args = parser.parse_args()
    file_path = args.input_file_path
    neighbours = args.neighbours

    #get the output file name
    with open('data/do_not_delete/output_file_names.json', 'r') as f:
        data = json.load(f)
    output_file_name = data[file_path]


    try: 

        # get the isocontours
        print("\nCompilation complete, start execution.\n")
        grid = numpy_to_field(file_path)
        points, previous_edge, next_edge, cycle_index, cycles =\
                  numpy_contour_to_data_structure(output_file_name + "_contour")
    
        #stitch the isocontours
        start_stitch = time.perf_counter()
        stitch_all_cycles_with_neighbourhood(
                                             points, 
                                             previous_edge, 
                                             next_edge,
                                             cycle_index, 
                                             cycles, 
                                             ti.math.ivec2(grid.shape[0], 
                                                           grid.shape[1]), 
                                             neighbours)
        end_stitch = time.perf_counter()
        print("Stitching algorithm runtime : " + str(end_stitch-start_stitch) + " seconds.\n")

        #save the cycle
        start_data = time.perf_counter()
        data_structure_to_numpy(
                                points, 
                                previous_edge,
                                next_edge, 
                                cycle_index, 
                                cycles, 
                                output_file_name + "_cycle")       
        end_data = time.perf_counter()
        print("Cycle data saved in : " + str(end_data-start_data) + " seconds.\n")
        

        flag_file = 'data/do_not_delete/flag_' + output_file_name + '.txt'

        if not os.path.exists(flag_file):
            # This is the first run, so write logs and create the flag file
            log_file_name = "data/log/" + output_file_name + ".log"
            logging.basicConfig(filename=log_file_name, 
                                filemode='a', 
                                format='%(message)s', 
                                level=logging.INFO)
            logging.info("Now stitch the isocontours of the scalar field : " + output_file_name + ".\n")
            logging.info("Stitching algorithm runtime : " + str(end_stitch-start_stitch) + " seconds.")
            logging.info("Cycle data saved in : " + str(end_data-start_data) + " seconds.\n")

            with open(flag_file, 'w') as f:
                f.write('This is not the first run.')
        
    except FileNotFoundError: 
        print("Please execute the contour extraction script first.")


