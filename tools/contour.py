import taichi as ti
import time
import argparse
import logging
import json
import os 

from cglib.type import numpy_to_field, data_structure_to_numpy
from cglib.graph import to_graph



ti.init(arch = ti.cpu)



if __name__ == "__main__": 

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file_path", 
                        help= "File in .npy format containing a scalar field whose isocontours we want to extract.", 
                        type = str)
    parser.add_argument("output_filename",
                        help = "Name of the file in which the isocontours will be saved.",
                        type = str)
    
    args = parser.parse_args()
    file_path = args.input_file_path
    output_file_name = args.output_filename

    #save the output file name in a json file
    with open('data/do_not_delete/output_file_names.json', 'r') as f:
        data = json.load(f)

    data[file_path] = output_file_name

    with open('data/do_not_delete/output_file_names.json', 'w') as f:
        json.dump(data, f)

    #remove the flag file if it exists
    try: 
        flag_file = 'data/do_not_delete/flag_' + output_file_name + '.txt'
        os.remove(flag_file)
    except FileNotFoundError:
        pass
    
    #run the extraction of the isocontours
    try: 

        
        log_file_name = "data/log/" + output_file_name + ".log"
        logging.basicConfig(filename=log_file_name, 
                            filemode='w', 
                            format='%(message)s', 
                            level=logging.INFO)
        logging.info("Extract the isocontours of the scalar field : " + output_file_name + ".\n")

        #get the scalar field 
        print("\nCompilation complete, start execution.\n")
        start_data = time.perf_counter()
        grid = numpy_to_field(file_path)
        end_data = time.perf_counter()
        print(f"Shape of the field : {grid.shape}")
        print("\nField imported in : " + str(end_data-start_data) + " seconds.\n")
        logging.info("Field imported in : " + str(end_data-start_data) + " seconds.")

        #initialise the graph
        start_data = time.perf_counter()
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
                                output_file_name + "_contour")
        end_data = time.perf_counter()
        print("Contours data saved in : " + str(end_data-start_data) + " seconds.\n")
        logging.info("Contours data saved in : " + str(end_data-start_data) + " seconds.\n")
                      
    except FileNotFoundError: 
        print("The file containing the scalar field does not exist. Please put it in data/fields.")