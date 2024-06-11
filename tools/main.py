import taichi as ti
import time
import argparse
import logging

from cglib.type import numpy_to_field, data_structure_to_numpy
from cglib.graph import to_graph
from cglib.stitch import stitch_all_cycles_with_neighbourhood



ti.init(arch = ti.cpu)



if __name__ == "__main__": 

    parser = argparse.ArgumentParser()
    parser.add_argument("input_filename", 
                        help= "File in .npy format containing a scalar field whose isocontours we want to extract and stitch.", 
                        type = str)

    args = parser.parse_args()
    file_name = args.input_filename

    try: 
        start_all = time.perf_counter()
        log_file_name = "data/log/" + file_name + ".log"
        logging.basicConfig(filename=log_file_name, 
                            filemode='w', 
                            format='%(message)s', 
                            level=logging.INFO)
        logging.info("Extract and stitch the isocontours of the scalar field : " + file_name + ".\n")



        #get the graph 
        print("\nCompilation complete, start execution.\n")
        start_data = time.perf_counter()
        grid = numpy_to_field(file_name)
        points, previous_edge, next_edge, cycle_index, cycles = to_graph(grid)
        end_data = time.perf_counter()
        print("Graph initialised in : " + str(end_data-start_data) + " seconds.\n")
        logging.info("Graph initialised in : " + str(end_data-start_data) + " seconds.")

        #save the graph 
        start_data = time.perf_counter()
        data_structure_to_numpy(points, 
                                previous_edge, 
                                next_edge, 
                                cycle_index, 
                                cycles, 
                                file_name + "_contour")
        end_data = time.perf_counter()
        print("Contours data saved in : " + str(end_data-start_data) + " seconds.\n")
        logging.info("Contours data saved in : " + str(end_data-start_data) + " seconds.")

        #stitch the graph and get a single cycle 
        start_data = time.perf_counter()
        stitch_all_cycles_with_neighbourhood(points, 
                                             previous_edge, 
                                             next_edge,
                                             cycle_index, 
                                             cycles, 
                                             ti.math.ivec2(grid.shape[0], grid.shape[1]))
        end_data = time.perf_counter()
        print("Stitching algorithm runtime : " + str(-start_data+end_data) + " seconds.\n")
        logging.info("Stitching algorithm runtime : " + str(-start_data+end_data) + " seconds.")

        #save the cycle
        start_data = time.perf_counter()
        output_file_name = str("stitched_" + file_name)
        data_structure_to_numpy(points, 
                                previous_edge,
                                next_edge, 
                                cycle_index, 
                                cycles, 
                                file_name + "_cycle")       
        end_data = time.perf_counter()
        print("Cycle data saved in : " + str(end_data-start_data) + " seconds.\n")
        logging.info("Cycle data saved in : " + str(end_data-start_data) + " seconds.\n")
        end_all = time.perf_counter()   

        print("Total runtime : " + str(end_all-start_all) + " seconds.\n")
        logging.info("Total runtime : " + str(end_all-start_all) + " seconds.\n") 

    except FileNotFoundError: 
        print("The file containing the scalar field does not exist. Please put it in data/fields.")